"""
Core Orchestrator that coordinates all components
"""

from datetime import datetime
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from ..phases.phase_manager import PhaseManager, PhaseName, PhaseStatus
from ..hrg.human_review_gate import HumanReviewGate, ReviewStatus
from ..rol_t.resource_optimizer import ResourceOptimizationLayer, ResourceType
from ..reproducibility.state_manager import StateManager
from ..ethics.axiom_framework import AxiomFramework
from ..audit.audit_logger import AuditLogger


class PipelineConfig(BaseModel):
    """Configuration for pipeline execution"""
    pipeline_id: str
    random_seed: Optional[int] = None
    enable_hrg: bool = True
    enable_ethics_audit: bool = True
    enable_resource_tracking: bool = True
    audit_log_dir: str = "./audit_logs"
    state_dir: str = "./state_snapshots"


class Orchestrator:
    """
    Core orchestrator that coordinates the 8-phase pipeline with all governance components.
    Integrates HRGs, ROL-T, reproducibility, ethics, and audit logging.
    """

    def __init__(self, config: PipelineConfig):
        self.config = config
        
        # Initialize all components
        self.phase_manager = PhaseManager()
        self.hrg = HumanReviewGate() if config.enable_hrg else None
        self.rol_t = ResourceOptimizationLayer() if config.enable_resource_tracking else None
        self.state_manager = StateManager(
            state_dir=config.state_dir,
            random_seed=config.random_seed,
        )
        self.ethics = AxiomFramework() if config.enable_ethics_audit else None
        self.audit_logger = AuditLogger(log_dir=config.audit_log_dir)
        
        # Pipeline state
        self.pipeline_started = False
        self.pipeline_completed = False
        
        # Log initialization
        self.audit_logger.log_event(
            event_type="ORCHESTRATOR_INIT",
            actor="SYSTEM",
            action="Orchestrator initialized",
            metadata={
                "pipeline_id": config.pipeline_id,
                "config": config.model_dump(),
            },
        )

    def execute_pipeline(
        self,
        initial_inputs: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Execute the complete 8-phase pipeline with governance.

        Args:
            initial_inputs: Initial inputs for the pipeline

        Returns:
            Dict with pipeline execution results
        """
        self.pipeline_started = True
        
        # Log pipeline start
        self.audit_logger.log_event(
            event_type="PIPELINE_START",
            actor="SYSTEM",
            action="Started pipeline execution",
            metadata={
                "pipeline_id": self.config.pipeline_id,
                "inputs": initial_inputs or {},
            },
        )
        
        # Execute each phase in sequence
        current_inputs = initial_inputs or {}
        
        for phase in PhaseName:
            result = self._execute_phase(phase, current_inputs)
            
            if not result["success"]:
                # Pipeline failed
                self.audit_logger.log_event(
                    event_type="PIPELINE_FAILED",
                    actor="SYSTEM",
                    action=f"Pipeline failed at phase {phase.value}",
                    phase=phase.value,
                    metadata={"error": result.get("error")},
                )
                return {
                    "success": False,
                    "failed_at_phase": phase.value,
                    "error": result.get("error"),
                }
            
            # Use outputs as inputs for next phase
            current_inputs = result.get("outputs", {})
        
        # Pipeline completed successfully
        self.pipeline_completed = True
        
        self.audit_logger.log_event(
            event_type="PIPELINE_COMPLETED",
            actor="SYSTEM",
            action="Pipeline completed successfully",
            metadata={
                "pipeline_id": self.config.pipeline_id,
            },
        )
        
        # Generate final attestation
        self._generate_final_attestation()
        
        return {
            "success": True,
            "outputs": current_inputs,
            "pipeline_status": self.get_pipeline_status(),
        }

    def _execute_phase(
        self,
        phase: PhaseName,
        inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute a single phase with full governance.

        Args:
            phase: Phase to execute
            inputs: Phase inputs

        Returns:
            Dict with execution results
        """
        # Start phase
        execution = self.phase_manager.start_phase(phase, inputs)
        
        # Log phase start
        self.audit_logger.log_event(
            event_type="PHASE_START",
            actor="SYSTEM",
            action=f"Started phase {phase.value}",
            phase=phase.value,
            metadata={"execution_id": execution.execution_id},
        )
        
        # Allocate resources if enabled
        if self.rol_t:
            self._allocate_phase_resources(phase, execution.execution_id)
        
        # Ethics audit before phase execution
        if self.ethics:
            self._conduct_ethics_audit(phase, inputs, "PRE_PHASE")
        
        # Check for HRG gate
        hrg_gate = self.phase_manager.get_phase_hrg_gate(phase)
        if hrg_gate and self.hrg:
            # Request human review
            review = self.hrg.request_review(
                gate_name=hrg_gate,
                phase=phase.value,
                assigned_to="human_reviewer",
                context={
                    "execution_id": execution.execution_id,
                    "phase": phase.value,
                    "inputs": inputs,
                },
            )
            
            execution.hrg_review_id = review.review_id
            
            # Block phase until review is complete
            self.phase_manager.block_phase(
                execution.execution_id,
                f"Waiting for HRG review: {review.review_id}",
            )
            
            self.audit_logger.log_event(
                event_type="HRG_REVIEW_REQUESTED",
                actor="SYSTEM",
                action=f"Requested HRG review at {hrg_gate}",
                phase=phase.value,
                metadata={
                    "review_id": review.review_id,
                    "execution_id": execution.execution_id,
                },
            )
            
            # In a real system, this would wait for actual human review
            # For this implementation, we'll simulate approval
            self._simulate_hrg_approval(review.review_id)
            
            # Unblock phase
            self.phase_manager.unblock_phase(execution.execution_id)
        
        # Execute phase logic (simplified - would call actual phase implementations)
        try:
            outputs = self._execute_phase_logic(phase, inputs)
            
            # Create state snapshot
            self.state_manager.create_snapshot(
                state_id=execution.execution_id,
                phase=phase.value,
                data={
                    "inputs": inputs,
                    "outputs": outputs,
                    "timestamp": datetime.utcnow().isoformat(),
                },
            )
            
            # Complete phase
            self.phase_manager.complete_phase(
                execution.execution_id,
                outputs=outputs,
                metrics={"processed": True},
            )
            
            # Record resource usage if enabled
            if self.rol_t:
                self._record_phase_resource_usage(phase, execution.execution_id)
            
            # Ethics audit after phase execution
            if self.ethics:
                self._conduct_ethics_audit(phase, outputs, "POST_PHASE")
            
            # Log phase completion
            self.audit_logger.log_event(
                event_type="PHASE_COMPLETED",
                actor="SYSTEM",
                action=f"Completed phase {phase.value}",
                phase=phase.value,
                metadata={
                    "execution_id": execution.execution_id,
                    "duration": execution.duration_seconds,
                },
            )
            
            return {
                "success": True,
                "outputs": outputs,
            }
            
        except Exception as e:
            # Phase failed
            error_msg = str(e)
            self.phase_manager.fail_phase(execution.execution_id, error_msg)
            
            self.audit_logger.log_event(
                event_type="PHASE_FAILED",
                actor="SYSTEM",
                action=f"Phase {phase.value} failed",
                phase=phase.value,
                metadata={
                    "execution_id": execution.execution_id,
                    "error": error_msg,
                },
            )
            
            return {
                "success": False,
                "error": error_msg,
            }

    def _execute_phase_logic(
        self,
        phase: PhaseName,
        inputs: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Execute the actual logic for a phase.
        In a real implementation, this would delegate to phase-specific handlers.

        Args:
            phase: Phase to execute
            inputs: Phase inputs

        Returns:
            Dict with phase outputs
        """
        # Simplified phase execution
        outputs = {
            "phase": phase.value,
            "processed": True,
            "timestamp": datetime.utcnow().isoformat(),
            "data": inputs.get("data", {}),
        }
        
        # Phase-specific logic would go here
        if phase == PhaseName.INGESTION:
            outputs["ingested_records"] = inputs.get("records", 0)
        elif phase == PhaseName.PREPROCESSING:
            outputs["preprocessed_records"] = inputs.get("ingested_records", 0)
        elif phase == PhaseName.PROCESSING:
            outputs["processed_records"] = inputs.get("preprocessed_records", 0)
        elif phase == PhaseName.ANALYSIS:
            outputs["analysis_results"] = {"status": "analyzed"}
        elif phase == PhaseName.VALIDATION:
            outputs["validation_passed"] = True
        elif phase == PhaseName.SYNTHESIS:
            outputs["synthesized_output"] = {"status": "synthesized"}
        elif phase == PhaseName.REVIEW:
            outputs["review_status"] = "reviewed"
        elif phase == PhaseName.FINALIZATION:
            outputs["final_output"] = {"status": "finalized"}
        
        return outputs

    def _allocate_phase_resources(self, phase: PhaseName, execution_id: str):
        """Allocate resources for a phase"""
        if not self.rol_t:
            return
        
        # Allocate compute resources
        self.rol_t.allocate_resource(
            resource_type=ResourceType.COMPUTE,
            phase=phase.value,
            amount_requested=100.0,
            unit="compute_units",
            priority=7,
        )
        
        # Allocate memory
        self.rol_t.allocate_resource(
            resource_type=ResourceType.MEMORY,
            phase=phase.value,
            amount_requested=1024.0,
            unit="MB",
            priority=6,
        )

    def _record_phase_resource_usage(self, phase: PhaseName, execution_id: str):
        """Record resource usage for a phase"""
        if not self.rol_t:
            return
        
        # Find allocations for this phase and record usage
        for allocation_id, allocation in self.rol_t.allocations.items():
            if allocation.phase == phase.value:
                # Simulate usage (80-95% of allocated)
                import random
                usage_factor = 0.80 + random.random() * 0.15
                amount_used = allocation.amount_allocated * usage_factor
                
                self.rol_t.record_usage(
                    allocation_id=allocation_id,
                    amount_used=amount_used,
                )

    def _conduct_ethics_audit(
        self,
        phase: PhaseName,
        context: Dict[str, Any],
        stage: str,
    ):
        """Conduct ethics audit for a phase"""
        if not self.ethics:
            return
        
        audit = self.ethics.conduct_normative_audit(
            phase=f"{phase.value}_{stage}",
            evaluation_context={
                "actor": "SYSTEM",
                "rationale": f"Automated phase execution: {phase.value}",
                "stage": stage,
                **context,
            },
        )
        
        # Log audit
        self.audit_logger.log_event(
            event_type="ETHICS_AUDIT",
            actor="SYSTEM",
            action=f"Conducted ethics audit for {phase.value} ({stage})",
            phase=phase.value,
            metadata={
                "audit_id": audit.audit_id,
                "compliance_score": audit.compliance_score,
                "violations": len(audit.violations),
                "warnings": len(audit.warnings),
            },
        )

    def _simulate_hrg_approval(self, review_id: str):
        """Simulate HRG approval (in real system, this would be actual human review)"""
        if not self.hrg:
            return
        
        self.hrg.start_review(review_id, "simulated_reviewer")
        self.hrg.complete_review(
            review_id,
            decision="APPROVE",
            rationale="Simulated approval for demonstration",
        )

    def _generate_final_attestation(self):
        """Generate final compliance attestation"""
        # Resource compliance
        if self.rol_t:
            waste_assessment = self.rol_t.assess_waste_governance()
            self.audit_logger.create_attestation(
                attestation_type="RESOURCE_COMPLIANCE",
                attester="SYSTEM",
                scope="Pipeline Execution",
                status=waste_assessment.compliance_status,
                findings=waste_assessment.waste_threshold_breaches,
            )
        
        # Ethics compliance
        if self.ethics:
            compliance = self.ethics.get_compliance_summary()
            self.audit_logger.create_attestation(
                attestation_type="ETHICS_COMPLIANCE",
                attester="SYSTEM",
                scope="Pipeline Execution",
                status="COMPLIANT" if compliance["average_compliance_score"] >= 0.8 else "REQUIRES_REVIEW",
                findings=[
                    f"Average compliance score: {compliance['average_compliance_score']:.2%}",
                    f"Total violations: {compliance['total_violations']}",
                    f"Total warnings: {compliance['total_warnings']}",
                ],
            )
        
        # Reproducibility attestation
        repro_info = self.state_manager.get_reproducibility_info()
        self.audit_logger.create_attestation(
            attestation_type="REPRODUCIBILITY",
            attester="SYSTEM",
            scope="Pipeline Execution",
            status="COMPLIANT",
            findings=[
                f"Config hash: {repro_info['config_hash']}",
                f"Random seed: {repro_info['random_seed']}",
                f"Snapshots created: {repro_info['snapshots_count']}",
            ],
        )

    def get_pipeline_status(self) -> Dict[str, Any]:
        """
        Get comprehensive pipeline status.

        Returns:
            Dict with complete pipeline status
        """
        status = {
            "pipeline_id": self.config.pipeline_id,
            "started": self.pipeline_started,
            "completed": self.pipeline_completed,
            "phase_status": self.phase_manager.get_pipeline_status(),
        }
        
        if self.hrg:
            status["hrg_stats"] = self.hrg.get_review_statistics()
        
        if self.rol_t:
            status["resource_stats"] = self.rol_t.get_utilization_stats()
        
        if self.ethics:
            status["ethics_compliance"] = self.ethics.get_compliance_summary()
        
        status["reproducibility"] = self.state_manager.get_reproducibility_info()
        
        # Verify audit log integrity
        status["audit_chain_valid"] = self.audit_logger.verify_chain()
        
        return status
