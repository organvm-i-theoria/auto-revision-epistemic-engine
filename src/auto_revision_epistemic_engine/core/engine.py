"""
Auto-Revision Epistemic Engine - Main entry point
"""

from typing import Any, Dict, Optional
from .orchestrator import Orchestrator, PipelineConfig


class AutoRevisionEngine:
    """
    Auto-Revision Epistemic Engine (v4.2)
    
    A self-governing orchestration framework that integrates:
    - 8 phases (ingestion → finalization) with human oversight at 4 gates
    - Balances automation & governance via HRGs with clear SLAs and escalation
    - Optimizes resources via ROL-T (utilization tracking, waste governance)
    - Ensures reproducibility via pinned models, seeds, and immutable state
    - Embeds ethics & reflexivity via axioms, normative audit, and meta-commentary
    - Provides full auditability via append-only logs, BLAKE3 hashing, and compliance attestations
    """

    def __init__(
        self,
        pipeline_id: str = "default",
        random_seed: Optional[int] = None,
        enable_hrg: bool = True,
        enable_ethics_audit: bool = True,
        enable_resource_tracking: bool = True,
        audit_log_dir: str = "./audit_logs",
        state_dir: str = "./state_snapshots",
    ):
        """
        Initialize the Auto-Revision Epistemic Engine.

        Args:
            pipeline_id: Unique identifier for this pipeline
            random_seed: Random seed for reproducibility
            enable_hrg: Enable Human Review Gates
            enable_ethics_audit: Enable ethics auditing
            enable_resource_tracking: Enable resource optimization tracking
            audit_log_dir: Directory for audit logs
            state_dir: Directory for state snapshots
        """
        self.config = PipelineConfig(
            pipeline_id=pipeline_id,
            random_seed=random_seed,
            enable_hrg=enable_hrg,
            enable_ethics_audit=enable_ethics_audit,
            enable_resource_tracking=enable_resource_tracking,
            audit_log_dir=audit_log_dir,
            state_dir=state_dir,
        )
        
        self.orchestrator = Orchestrator(self.config)

    def execute(self, inputs: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Execute the complete 8-phase pipeline.

        Args:
            inputs: Initial inputs for the pipeline

        Returns:
            Dict with execution results and status
        """
        return self.orchestrator.execute_pipeline(inputs)

    def get_status(self) -> Dict[str, Any]:
        """
        Get current pipeline status.

        Returns:
            Dict with comprehensive status information
        """
        return self.orchestrator.get_pipeline_status()

    def get_audit_trail(self) -> Dict[str, Any]:
        """
        Get audit trail information.

        Returns:
            Dict with audit trail details
        """
        audit_logger = self.orchestrator.audit_logger
        
        return {
            "chain_valid": audit_logger.verify_chain(),
            "total_entries": len(audit_logger.get_entries()),
            "recent_entries": [
                entry.model_dump() for entry in audit_logger.get_entries(limit=10)
            ],
            "attestations": [
                att.model_dump() for att in audit_logger.get_attestations()
            ],
        }

    def get_reproducibility_info(self) -> Dict[str, Any]:
        """
        Get reproducibility information.

        Returns:
            Dict with reproducibility configuration
        """
        return self.orchestrator.state_manager.get_reproducibility_info()

    def get_resource_report(self) -> Dict[str, Any]:
        """
        Get resource utilization and waste report.

        Returns:
            Dict with resource management details
        """
        if not self.orchestrator.rol_t:
            return {"enabled": False}
        
        return {
            "enabled": True,
            "waste_report": self.orchestrator.rol_t.get_waste_report(),
            "utilization_stats": self.orchestrator.rol_t.get_utilization_stats(),
        }

    def get_ethics_report(self) -> Dict[str, Any]:
        """
        Get ethics compliance report.

        Returns:
            Dict with ethics audit information
        """
        if not self.orchestrator.ethics:
            return {"enabled": False}
        
        return {
            "enabled": True,
            "compliance_summary": self.orchestrator.ethics.get_compliance_summary(),
            "recent_audits": [
                audit.model_dump() for audit in self.orchestrator.ethics.get_audits()[-5:]
            ],
            "axiom_count": len(self.orchestrator.ethics.axioms),
        }

    def get_hrg_report(self) -> Dict[str, Any]:
        """
        Get Human Review Gate report.

        Returns:
            Dict with HRG statistics
        """
        if not self.orchestrator.hrg:
            return {"enabled": False}
        
        return {
            "enabled": True,
            "statistics": self.orchestrator.hrg.get_review_statistics(),
            "pending_reviews": len(self.orchestrator.hrg.get_pending_reviews()),
            "sla_violations": len(self.orchestrator.hrg.check_sla_compliance()),
        }

    def pin_model(self, model_name: str, version: str):
        """
        Pin a model to a specific version for reproducibility.

        Args:
            model_name: Name of the model
            version: Version identifier
        """
        self.orchestrator.state_manager.pin_model(model_name, version)

    def add_ethical_axiom(self, axiom_id: str, category: str, statement: str, **kwargs):
        """
        Add a custom ethical axiom.

        Args:
            axiom_id: Unique axiom identifier
            category: Axiom category
            statement: Axiom statement
            **kwargs: Additional axiom parameters
        """
        if self.orchestrator.ethics:
            from ..ethics.axiom_framework import Axiom, AxiomCategory
            
            axiom = Axiom(
                axiom_id=axiom_id,
                category=AxiomCategory[category.upper()],
                statement=statement,
                **kwargs,
            )
            self.orchestrator.ethics.add_axiom(axiom)
