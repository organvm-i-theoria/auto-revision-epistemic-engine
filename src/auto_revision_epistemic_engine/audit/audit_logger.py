"""
Audit Logger with BLAKE3 hashing for immutable append-only logs
"""

import blake3
import json
import os
import threading
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AuditEntry(BaseModel):
    """Single audit log entry"""
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    event_type: str
    phase: Optional[str] = None
    actor: str
    action: str
    metadata: Dict[str, Any] = Field(default_factory=dict)
    previous_hash: Optional[str] = None
    entry_hash: str = ""

    def compute_hash(self) -> str:
        """Compute BLAKE3 hash for this entry"""
        data = {
            "timestamp": self.timestamp,
            "event_type": self.event_type,
            "phase": self.phase,
            "actor": self.actor,
            "action": self.action,
            "metadata": self.metadata,
            "previous_hash": self.previous_hash,
        }
        hasher = blake3.blake3(json.dumps(data, sort_keys=True).encode())
        return hasher.hexdigest()


class ComplianceAttestation(BaseModel):
    """Compliance attestation record"""
    attestation_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    attestation_type: str
    attester: str
    scope: str
    status: str
    findings: List[str] = Field(default_factory=list)
    hash: str = ""


class AuditLogger:
    """
    Append-only audit logger with BLAKE3 hashing and compliance attestations.
    Provides full auditability and immutable log chain.
    """

    def __init__(self, log_dir: str = "./audit_logs"):
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.log_file = self.log_dir / "audit_log.jsonl"
        self.attestation_file = self.log_dir / "attestations.jsonl"
        self._last_hash: Optional[str] = None
        self._lock = threading.Lock()  # Thread safety for concurrent access
        self._initialize_log()

    def _initialize_log(self):
        """Initialize or load existing log with corruption recovery"""
        if self.log_file.exists():
            # Load last hash from existing log with error recovery
            try:
                with open(self.log_file, "r") as f:
                    lines = f.readlines()
                    if lines:
                        # Try from end backward to handle corrupted last line
                        for line in reversed(lines[-10:]):  # Check last 10 entries
                            try:
                                last_entry = json.loads(line.strip())
                                # Verify entry has required fields
                                if "entry_hash" in last_entry:
                                    self._last_hash = last_entry.get("entry_hash")
                                    break
                            except json.JSONDecodeError:
                                continue  # Skip corrupted line
            except IOError as e:
                # Log file exists but cannot be read - critical error
                raise RuntimeError(f"Cannot initialize audit log: {e}")
        else:
            # Create new log file
            self.log_file.touch()

    def log_event(
        self,
        event_type: str,
        actor: str,
        action: str,
        phase: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> AuditEntry:
        """
        Log an event to the append-only audit log with thread safety.

        Args:
            event_type: Type of event (e.g., 'PHASE_START', 'HRG_REVIEW', 'RESOURCE_ALLOCATION')
            actor: Who performed the action (human or system)
            action: Description of the action
            phase: Optional phase name
            metadata: Additional metadata

        Returns:
            AuditEntry: The created audit entry
        """
        with self._lock:  # Thread-safe logging
            entry = AuditEntry(
                event_type=event_type,
                phase=phase,
                actor=actor,
                action=action,
                metadata=metadata or {},
                previous_hash=self._last_hash,
            )
            entry.entry_hash = entry.compute_hash()
            self._last_hash = entry.entry_hash

            # Append to log file with error handling
            try:
                with open(self.log_file, "a") as f:
                    f.write(entry.model_dump_json() + "\n")
                    f.flush()  # Force write to OS buffer
                    os.fsync(f.fileno())  # Force write to disk
            except IOError as e:
                # Critical: audit log write failed
                raise RuntimeError(f"Failed to write audit log: {e}")

            return entry

    def create_attestation(
        self,
        attestation_type: str,
        attester: str,
        scope: str,
        status: str,
        findings: Optional[List[str]] = None,
    ) -> ComplianceAttestation:
        """
        Create a compliance attestation.

        Args:
            attestation_type: Type of attestation (e.g., 'ETHICS_AUDIT', 'RESOURCE_COMPLIANCE')
            attester: Who performed the attestation
            scope: Scope of attestation
            status: Status (e.g., 'COMPLIANT', 'NON_COMPLIANT', 'REQUIRES_REVIEW')
            findings: List of findings

        Returns:
            ComplianceAttestation: The created attestation
        """
        attestation_id = blake3.blake3(
            f"{attestation_type}_{attester}_{datetime.now(timezone.utc).isoformat()}".encode()
        ).hexdigest()[:16]

        attestation = ComplianceAttestation(
            attestation_id=attestation_id,
            attestation_type=attestation_type,
            attester=attester,
            scope=scope,
            status=status,
            findings=findings or [],
        )
        
        # Compute hash
        hasher = blake3.blake3(attestation.model_dump_json().encode())
        attestation.hash = hasher.hexdigest()

        # Append to attestations file
        with open(self.attestation_file, "a") as f:
            f.write(attestation.model_dump_json() + "\n")

        # Also log as audit event
        self.log_event(
            event_type="COMPLIANCE_ATTESTATION",
            actor=attester,
            action=f"Created {attestation_type} attestation",
            metadata={
                "attestation_id": attestation_id,
                "status": status,
                "findings": findings or [],
            },
        )

        return attestation

    def verify_chain(self) -> bool:
        """
        Verify the integrity of the audit log chain.

        Returns:
            bool: True if chain is valid, False otherwise
        """
        if not self.log_file.exists():
            return True

        with open(self.log_file, "r") as f:
            lines = f.readlines()

        previous_hash = None
        for line in lines:
            entry_data = json.loads(line)
            entry = AuditEntry(**entry_data)

            # Verify previous hash matches
            if entry.previous_hash != previous_hash:
                return False

            # Verify entry hash
            expected_hash = entry.compute_hash()
            if entry.entry_hash != expected_hash:
                return False

            previous_hash = entry.entry_hash

        return True

    def get_entries(
        self,
        event_type: Optional[str] = None,
        phase: Optional[str] = None,
        actor: Optional[str] = None,
        limit: Optional[int] = None,
    ) -> List[AuditEntry]:
        """
        Query audit log entries.

        Args:
            event_type: Filter by event type
            phase: Filter by phase
            actor: Filter by actor
            limit: Maximum number of entries to return

        Returns:
            List of matching audit entries
        """
        if not self.log_file.exists():
            return []

        entries = []
        with open(self.log_file, "r") as f:
            for line in f:
                entry = AuditEntry(**json.loads(line))

                # Apply filters
                if event_type and entry.event_type != event_type:
                    continue
                if phase and entry.phase != phase:
                    continue
                if actor and entry.actor != actor:
                    continue

                entries.append(entry)

                if limit and len(entries) >= limit:
                    break

        return entries

    def get_attestations(
        self,
        attestation_type: Optional[str] = None,
        status: Optional[str] = None,
    ) -> List[ComplianceAttestation]:
        """
        Query compliance attestations.

        Args:
            attestation_type: Filter by attestation type
            status: Filter by status

        Returns:
            List of matching attestations
        """
        if not self.attestation_file.exists():
            return []

        attestations = []
        with open(self.attestation_file, "r") as f:
            for line in f:
                attestation = ComplianceAttestation(**json.loads(line))

                # Apply filters
                if attestation_type and attestation.attestation_type != attestation_type:
                    continue
                if status and attestation.status != status:
                    continue

                attestations.append(attestation)

        return attestations
