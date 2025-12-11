"""
Phase Manager for the 8-phase orchestration pipeline
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class PhaseStatus(str, Enum):
    """Status of a phase"""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    BLOCKED = "BLOCKED"
    SKIPPED = "SKIPPED"


class PhaseName(str, Enum):
    """The 8 phases of the pipeline"""
    INGESTION = "INGESTION"
    PREPROCESSING = "PREPROCESSING"
    PROCESSING = "PROCESSING"
    ANALYSIS = "ANALYSIS"
    VALIDATION = "VALIDATION"
    SYNTHESIS = "SYNTHESIS"
    REVIEW = "REVIEW"
    FINALIZATION = "FINALIZATION"


class PhaseExecution(BaseModel):
    """Record of a phase execution"""
    execution_id: str
    phase: PhaseName
    status: PhaseStatus = PhaseStatus.PENDING
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    duration_seconds: Optional[float] = None
    inputs: Dict[str, Any] = Field(default_factory=dict)
    outputs: Dict[str, Any] = Field(default_factory=dict)
    metrics: Dict[str, Any] = Field(default_factory=dict)
    error: Optional[str] = None
    hrg_review_id: Optional[str] = None


class PhaseManager:
    """
    Manages the 8-phase orchestration pipeline:
    1. INGESTION - Data and request ingestion
    2. PREPROCESSING - Data cleaning and preparation
    3. PROCESSING - Main processing logic
    4. ANALYSIS - Analysis and pattern detection
    5. VALIDATION - Quality validation and checks
    6. SYNTHESIS - Result synthesis
    7. REVIEW - Human review and approval
    8. FINALIZATION - Final packaging and delivery
    """

    def __init__(self):
        self.phases = {
            PhaseName.INGESTION: {
                "order": 1,
                "description": "Ingest data and requests",
                "hrg_gate": "GATE_1_INGESTION",
                "required": True,
            },
            PhaseName.PREPROCESSING: {
                "order": 2,
                "description": "Preprocess and clean data",
                "hrg_gate": None,
                "required": True,
            },
            PhaseName.PROCESSING: {
                "order": 3,
                "description": "Execute main processing",
                "hrg_gate": "GATE_2_PROCESSING",
                "required": True,
            },
            PhaseName.ANALYSIS: {
                "order": 4,
                "description": "Analyze results and patterns",
                "hrg_gate": None,
                "required": True,
            },
            PhaseName.VALIDATION: {
                "order": 5,
                "description": "Validate quality and correctness",
                "hrg_gate": "GATE_3_VALIDATION",
                "required": True,
            },
            PhaseName.SYNTHESIS: {
                "order": 6,
                "description": "Synthesize final results",
                "hrg_gate": None,
                "required": True,
            },
            PhaseName.REVIEW: {
                "order": 7,
                "description": "Human review and approval",
                "hrg_gate": None,
                "required": True,
            },
            PhaseName.FINALIZATION: {
                "order": 8,
                "description": "Finalize and deliver",
                "hrg_gate": "GATE_4_FINALIZATION",
                "required": True,
            },
        }
        
        self.executions: Dict[str, PhaseExecution] = {}
        self.current_pipeline: List[str] = []

    def start_phase(
        self,
        phase: PhaseName,
        inputs: Optional[Dict[str, Any]] = None,
    ) -> PhaseExecution:
        """
        Start a phase execution.

        Args:
            phase: Phase to start
            inputs: Input data for the phase

        Returns:
            PhaseExecution: The phase execution record
        """
        execution_id = f"{phase.value}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}"
        
        execution = PhaseExecution(
            execution_id=execution_id,
            phase=phase,
            status=PhaseStatus.RUNNING,
            started_at=datetime.now(timezone.utc).isoformat(),
            inputs=inputs or {},
        )
        
        self.executions[execution_id] = execution
        self.current_pipeline.append(execution_id)
        
        return execution

    def complete_phase(
        self,
        execution_id: str,
        outputs: Optional[Dict[str, Any]] = None,
        metrics: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Mark a phase as completed.

        Args:
            execution_id: Execution ID
            outputs: Output data from the phase
            metrics: Performance metrics

        Returns:
            bool: True if completed successfully
        """
        if execution_id not in self.executions:
            return False
        
        execution = self.executions[execution_id]
        
        if execution.status != PhaseStatus.RUNNING:
            return False
        
        execution.status = PhaseStatus.COMPLETED
        execution.completed_at = datetime.now(timezone.utc).isoformat()
        
        if outputs:
            execution.outputs = outputs
        
        if metrics:
            execution.metrics = metrics
        
        # Calculate duration
        if execution.started_at:
            started = datetime.fromisoformat(execution.started_at)
            completed = datetime.fromisoformat(execution.completed_at)
            execution.duration_seconds = (completed - started).total_seconds()
        
        return True

    def fail_phase(
        self,
        execution_id: str,
        error: str,
    ) -> bool:
        """
        Mark a phase as failed.

        Args:
            execution_id: Execution ID
            error: Error message

        Returns:
            bool: True if marked as failed successfully
        """
        if execution_id not in self.executions:
            return False
        
        execution = self.executions[execution_id]
        
        execution.status = PhaseStatus.FAILED
        execution.completed_at = datetime.now(timezone.utc).isoformat()
        execution.error = error
        
        # Calculate duration
        if execution.started_at:
            started = datetime.fromisoformat(execution.started_at)
            completed = datetime.fromisoformat(execution.completed_at)
            execution.duration_seconds = (completed - started).total_seconds()
        
        return True

    def block_phase(self, execution_id: str, reason: str) -> bool:
        """
        Block a phase (e.g., waiting for HRG approval).

        Args:
            execution_id: Execution ID
            reason: Reason for blocking

        Returns:
            bool: True if blocked successfully
        """
        if execution_id not in self.executions:
            return False
        
        execution = self.executions[execution_id]
        execution.status = PhaseStatus.BLOCKED
        execution.error = reason
        
        return True

    def unblock_phase(self, execution_id: str) -> bool:
        """
        Unblock a phase and resume.

        Args:
            execution_id: Execution ID

        Returns:
            bool: True if unblocked successfully
        """
        if execution_id not in self.executions:
            return False
        
        execution = self.executions[execution_id]
        
        if execution.status != PhaseStatus.BLOCKED:
            return False
        
        execution.status = PhaseStatus.RUNNING
        execution.error = None
        
        return True

    def get_next_phase(self, current_phase: PhaseName) -> Optional[PhaseName]:
        """
        Get the next phase in the pipeline.

        Args:
            current_phase: Current phase

        Returns:
            Optional[PhaseName]: Next phase, or None if at the end
        """
        current_order = self.phases[current_phase]["order"]
        
        for phase, config in self.phases.items():
            if config["order"] == current_order + 1:
                return phase
        
        return None

    def get_phase_hrg_gate(self, phase: PhaseName) -> Optional[str]:
        """
        Get HRG gate name for a phase.

        Args:
            phase: Phase name

        Returns:
            Optional[str]: HRG gate name, or None if no gate
        """
        return self.phases[phase].get("hrg_gate")

    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get overall pipeline status.

        Returns:
            Dict with pipeline status
        """
        if not self.current_pipeline:
            return {
                "status": "NOT_STARTED",
                "phases_completed": 0,
                "phases_total": len(self.phases),
                "progress_percentage": 0.0,
            }
        
        # Count phase statuses
        status_counts = {status.value: 0 for status in PhaseStatus}
        for exec_id in self.current_pipeline:
            execution = self.executions[exec_id]
            status_counts[execution.status.value] += 1
        
        # Determine overall status
        if status_counts[PhaseStatus.FAILED.value] > 0:
            overall_status = "FAILED"
        elif status_counts[PhaseStatus.BLOCKED.value] > 0:
            overall_status = "BLOCKED"
        elif status_counts[PhaseStatus.RUNNING.value] > 0:
            overall_status = "RUNNING"
        elif status_counts[PhaseStatus.COMPLETED.value] == len(self.phases):
            overall_status = "COMPLETED"
        else:
            overall_status = "IN_PROGRESS"
        
        progress = (
            status_counts[PhaseStatus.COMPLETED.value] / len(self.phases) * 100
        )
        
        return {
            "status": overall_status,
            "phases_completed": status_counts[PhaseStatus.COMPLETED.value],
            "phases_total": len(self.phases),
            "progress_percentage": progress,
            "status_breakdown": status_counts,
        }

    def get_phase_executions(
        self,
        phase: Optional[PhaseName] = None,
        status: Optional[PhaseStatus] = None,
    ) -> List[PhaseExecution]:
        """
        Get phase executions with optional filters.

        Args:
            phase: Filter by phase
            status: Filter by status

        Returns:
            List of matching executions
        """
        executions = list(self.executions.values())
        
        if phase:
            executions = [e for e in executions if e.phase == phase]
        
        if status:
            executions = [e for e in executions if e.status == status]
        
        return executions

    def get_phase_metrics(self, phase: PhaseName) -> Dict[str, Any]:
        """
        Get aggregated metrics for a phase across all executions.

        Args:
            phase: Phase name

        Returns:
            Dict with aggregated metrics
        """
        executions = self.get_phase_executions(phase=phase)
        
        if not executions:
            return {
                "total_executions": 0,
                "average_duration_seconds": 0.0,
                "success_rate": 1.0,
            }
        
        completed = [e for e in executions if e.status == PhaseStatus.COMPLETED]
        failed = [e for e in executions if e.status == PhaseStatus.FAILED]
        
        durations = [
            e.duration_seconds for e in executions
            if e.duration_seconds is not None
        ]
        
        avg_duration = sum(durations) / len(durations) if durations else 0.0
        
        success_rate = (
            len(completed) / len(executions)
            if executions
            else 1.0
        )
        
        return {
            "total_executions": len(executions),
            "completed": len(completed),
            "failed": len(failed),
            "average_duration_seconds": avg_duration,
            "success_rate": success_rate,
        }
