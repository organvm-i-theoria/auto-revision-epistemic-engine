"""
Expanded test suite for individual components of the Auto-Revision Epistemic Engine.

Tests PhaseManager, HumanReviewGate, AuditLogger, AxiomFramework,
ResourceOptimizationLayer, and StateManager in depth.
"""

import json
import os
import tempfile

import pytest

from auto_revision_epistemic_engine.phases.phase_manager import (
    PhaseManager,
    PhaseName,
    PhaseStatus,
)
from auto_revision_epistemic_engine.hrg.human_review_gate import (
    EscalationLevel,
    HumanReviewGate,
    ReviewStatus,
    SLA,
)
from auto_revision_epistemic_engine.audit.audit_logger import AuditLogger
from auto_revision_epistemic_engine.ethics.axiom_framework import (
    Axiom,
    AxiomCategory,
    AxiomFramework,
)
from auto_revision_epistemic_engine.rol_t.resource_optimizer import (
    ResourceOptimizationLayer,
    ResourceType,
)
from auto_revision_epistemic_engine.reproducibility.state_manager import StateManager


# ---------------------------------------------------------------------------
# PhaseManager tests
# ---------------------------------------------------------------------------

class TestPhaseManagerTransitions:
    """Test all phase transitions and edge cases for PhaseManager."""

    def test_start_phase_sets_running(self):
        """Starting a phase sets status to RUNNING."""
        pm = PhaseManager()
        execution = pm.start_phase(PhaseName.INGESTION, inputs={"key": "value"})
        assert execution.status == PhaseStatus.RUNNING
        assert execution.inputs == {"key": "value"}
        assert execution.started_at is not None

    def test_complete_phase_from_running(self):
        """Completing a RUNNING phase transitions to COMPLETED."""
        pm = PhaseManager()
        execution = pm.start_phase(PhaseName.PREPROCESSING)
        result = pm.complete_phase(
            execution.execution_id,
            outputs={"cleaned": True},
            metrics={"rows": 42},
        )
        assert result is True
        assert execution.status == PhaseStatus.COMPLETED
        assert execution.outputs == {"cleaned": True}
        assert execution.metrics == {"rows": 42}
        assert execution.completed_at is not None
        assert execution.duration_seconds is not None

    def test_complete_already_completed_returns_false(self):
        """Completing a phase that is already COMPLETED returns False (double-complete guard)."""
        pm = PhaseManager()
        execution = pm.start_phase(PhaseName.ANALYSIS)
        pm.complete_phase(execution.execution_id)
        result = pm.complete_phase(execution.execution_id)
        assert result is False

    def test_fail_phase(self):
        """Failing a phase sets FAILED status with error message."""
        pm = PhaseManager()
        execution = pm.start_phase(PhaseName.PROCESSING)
        result = pm.fail_phase(execution.execution_id, "data corruption")
        assert result is True
        assert execution.status == PhaseStatus.FAILED
        assert execution.error == "data corruption"
        assert execution.duration_seconds is not None

    def test_block_and_unblock_phase(self):
        """Blocking a phase sets BLOCKED; unblocking restores RUNNING."""
        pm = PhaseManager()
        execution = pm.start_phase(PhaseName.VALIDATION)
        pm.block_phase(execution.execution_id, "awaiting HRG")
        assert execution.status == PhaseStatus.BLOCKED
        pm.unblock_phase(execution.execution_id)
        assert execution.status == PhaseStatus.RUNNING
        assert execution.error is None

    def test_unblock_non_blocked_returns_false(self):
        """Unblocking a non-BLOCKED phase returns False."""
        pm = PhaseManager()
        execution = pm.start_phase(PhaseName.SYNTHESIS)
        result = pm.unblock_phase(execution.execution_id)
        assert result is False

    def test_get_next_phase_sequential(self):
        """get_next_phase follows the 8-phase sequence."""
        pm = PhaseManager()
        assert pm.get_next_phase(PhaseName.INGESTION) == PhaseName.PREPROCESSING
        assert pm.get_next_phase(PhaseName.REVIEW) == PhaseName.FINALIZATION
        assert pm.get_next_phase(PhaseName.FINALIZATION) is None

    def test_pipeline_status_not_started(self):
        """Pipeline status reports NOT_STARTED when no phases have run."""
        pm = PhaseManager()
        status = pm.get_pipeline_status()
        assert status["status"] == "NOT_STARTED"
        assert status["phases_completed"] == 0

    def test_pipeline_status_after_all_complete(self):
        """Pipeline status reports COMPLETED when all 8 phases finish."""
        pm = PhaseManager()
        for phase in PhaseName:
            ex = pm.start_phase(phase)
            pm.complete_phase(ex.execution_id)
        status = pm.get_pipeline_status()
        assert status["status"] == "COMPLETED"
        assert status["progress_percentage"] == 100.0

    def test_phase_metrics_empty(self):
        """Phase metrics for a phase with no executions returns defaults."""
        pm = PhaseManager()
        metrics = pm.get_phase_metrics(PhaseName.INGESTION)
        assert metrics["total_executions"] == 0
        assert metrics["success_rate"] == 1.0

    def test_get_phase_hrg_gate(self):
        """HRG gates are associated with specific phases."""
        pm = PhaseManager()
        assert pm.get_phase_hrg_gate(PhaseName.INGESTION) == "GATE_1_INGESTION"
        assert pm.get_phase_hrg_gate(PhaseName.PREPROCESSING) is None
        assert pm.get_phase_hrg_gate(PhaseName.FINALIZATION) == "GATE_4_FINALIZATION"

    def test_complete_nonexistent_execution_returns_false(self):
        """Completing a nonexistent execution ID returns False."""
        pm = PhaseManager()
        assert pm.complete_phase("NONEXISTENT_ID") is False

    def test_fail_nonexistent_execution_returns_false(self):
        """Failing a nonexistent execution ID returns False."""
        pm = PhaseManager()
        assert pm.fail_phase("NONEXISTENT_ID", "error") is False


# ---------------------------------------------------------------------------
# HumanReviewGate tests
# ---------------------------------------------------------------------------

class TestHumanReviewGateLifecycle:
    """Test HRG review lifecycle: request -> start -> complete/reject."""

    def test_request_creates_pending_review(self):
        """Requesting a review creates a PENDING review."""
        hrg = HumanReviewGate()
        review = hrg.request_review(
            gate_name="GATE_1_INGESTION",
            phase="INGESTION",
            assigned_to="alice",
            context={"batch_id": "b-001"},
        )
        assert review.status == ReviewStatus.PENDING
        assert review.assigned_to == "alice"
        assert review.context["batch_id"] == "b-001"

    def test_start_transitions_to_in_progress(self):
        """Starting a review transitions from PENDING to IN_PROGRESS."""
        hrg = HumanReviewGate()
        review = hrg.request_review("GATE_2_PROCESSING", "PROCESSING", "bob")
        result = hrg.start_review(review.review_id, "bob")
        assert result is True
        assert review.status == ReviewStatus.IN_PROGRESS
        assert review.reviewer == "bob"
        assert review.responded_at is not None

    def test_start_already_started_returns_false(self):
        """Starting a review that is already IN_PROGRESS returns False."""
        hrg = HumanReviewGate()
        review = hrg.request_review("GATE_3_VALIDATION", "VALIDATION", "carol")
        hrg.start_review(review.review_id, "carol")
        result = hrg.start_review(review.review_id, "carol")
        assert result is False

    def test_complete_with_approve(self):
        """Completing a review with APPROVE sets APPROVED status."""
        hrg = HumanReviewGate()
        review = hrg.request_review("GATE_4_FINALIZATION", "FINALIZATION", "dave")
        hrg.start_review(review.review_id, "dave")
        hrg.complete_review(review.review_id, "APPROVE", "Looks good")
        assert review.status == ReviewStatus.APPROVED
        assert review.rationale == "Looks good"

    def test_complete_with_reject(self):
        """Completing a review with REJECT sets REJECTED status."""
        hrg = HumanReviewGate()
        review = hrg.request_review("GATE_1_INGESTION", "INGESTION", "eve")
        hrg.start_review(review.review_id, "eve")
        hrg.complete_review(review.review_id, "REJECT", "Data quality too low")
        assert review.status == ReviewStatus.REJECTED
        assert review.decision == "REJECT"

    def test_escalate_review(self):
        """Escalating a review updates level and status."""
        hrg = HumanReviewGate()
        review = hrg.request_review("GATE_2_PROCESSING", "PROCESSING", "frank")
        event = hrg.escalate_review(
            review.review_id,
            to_level=EscalationLevel.LEVEL_1,
            reason="Response timeout",
            escalated_to="team_lead",
        )
        assert review.status == ReviewStatus.ESCALATED
        assert review.escalation_level == EscalationLevel.LEVEL_1
        assert event.from_level == EscalationLevel.NONE
        assert event.to_level == EscalationLevel.LEVEL_1

    def test_escalate_nonexistent_raises(self):
        """Escalating a nonexistent review raises ValueError."""
        hrg = HumanReviewGate()
        with pytest.raises(ValueError, match="not found"):
            hrg.escalate_review("FAKE_ID", EscalationLevel.LEVEL_1, "no reason", "nobody")

    def test_get_pending_reviews_filter(self):
        """get_pending_reviews filters by assigned_to and gate_name."""
        hrg = HumanReviewGate()
        hrg.request_review("GATE_1_INGESTION", "INGESTION", "alice")
        hrg.request_review("GATE_2_PROCESSING", "PROCESSING", "bob")
        hrg.request_review("GATE_1_INGESTION", "INGESTION", "alice")

        assert len(hrg.get_pending_reviews(assigned_to="alice")) == 2
        assert len(hrg.get_pending_reviews(gate_name="GATE_2_PROCESSING")) == 1

    def test_review_statistics(self):
        """Review statistics reflect all reviews."""
        hrg = HumanReviewGate()
        r1 = hrg.request_review("GATE_1_INGESTION", "INGESTION", "x")
        hrg.start_review(r1.review_id, "x")
        hrg.complete_review(r1.review_id, "APPROVE", "ok")
        r2 = hrg.request_review("GATE_2_PROCESSING", "PROCESSING", "y")

        stats = hrg.get_review_statistics()
        assert stats["total_reviews"] == 2
        assert stats["by_status"]["APPROVED"] == 1
        assert stats["by_status"]["PENDING"] == 1


# ---------------------------------------------------------------------------
# AuditLogger tests
# ---------------------------------------------------------------------------

class TestAuditLoggerChain:
    """Test BLAKE3 audit chain integrity and attestation creation."""

    def test_log_event_returns_entry_with_hash(self):
        """log_event returns an AuditEntry with a non-empty hash."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)
            entry = logger.log_event("TEST", "actor", "did something")
            assert entry.entry_hash != ""
            assert entry.event_type == "TEST"

    def test_chain_integrity_after_multiple_events(self):
        """Chain stays valid after logging many events."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)
            for i in range(20):
                logger.log_event(f"EVT_{i}", "SYS", f"action {i}")
            assert logger.verify_chain() is True

    def test_attestation_creates_entry_and_file(self):
        """create_attestation persists to the attestation file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)
            att = logger.create_attestation(
                attestation_type="ETHICS_COMPLIANCE",
                attester="SYSTEM",
                scope="test scope",
                status="COMPLIANT",
                findings=["no issues"],
            )
            assert att.status == "COMPLIANT"
            assert att.hash != ""
            # Verify the attestation is retrievable
            attestations = logger.get_attestations()
            assert len(attestations) == 1
            assert attestations[0].attestation_id == att.attestation_id

    def test_get_entries_with_filters(self):
        """get_entries respects event_type, phase, and actor filters."""
        with tempfile.TemporaryDirectory() as tmpdir:
            logger = AuditLogger(log_dir=tmpdir)
            logger.log_event("A", "user1", "action", phase="P1")
            logger.log_event("B", "user2", "action", phase="P2")
            logger.log_event("A", "user1", "action", phase="P2")

            assert len(logger.get_entries(event_type="A")) == 2
            assert len(logger.get_entries(phase="P2")) == 2
            assert len(logger.get_entries(actor="user2")) == 1
            assert len(logger.get_entries(limit=1)) == 1


# ---------------------------------------------------------------------------
# AxiomFramework tests
# ---------------------------------------------------------------------------

class TestAxiomFrameworkCompliance:
    """Test axiom registration, compliance checking, and meta-commentary."""

    def test_default_axioms_loaded(self):
        """Framework initializes with 8 default axioms."""
        fw = AxiomFramework()
        assert len(fw.axioms) == 8

    def test_add_and_remove_axiom(self):
        """Custom axioms can be added and removed."""
        fw = AxiomFramework()
        axiom = Axiom(
            axiom_id="CUSTOM_001",
            category=AxiomCategory.FAIRNESS,
            statement="Custom test axiom",
        )
        fw.add_axiom(axiom)
        assert "CUSTOM_001" in fw.axioms
        assert fw.remove_axiom("CUSTOM_001") is True
        assert "CUSTOM_001" not in fw.axioms
        assert fw.remove_axiom("NONEXISTENT") is False

    def test_normative_audit_compliant(self):
        """Audit passes when context satisfies all axioms."""
        fw = AxiomFramework()
        audit = fw.conduct_normative_audit(
            phase="TEST",
            evaluation_context={
                "actor": "SYSTEM",
                "rationale": "automated test",
            },
        )
        assert audit.compliance_score > 0.0
        assert len(audit.axioms_evaluated) == 8

    def test_normative_audit_missing_actor_violation(self):
        """Missing actor triggers ACCOUNTABILITY violation."""
        fw = AxiomFramework()
        audit = fw.conduct_normative_audit(
            phase="TEST",
            evaluation_context={"rationale": "test"},
        )
        # ACCT_001 is enforcement_level=BLOCK, so it should be a violation
        violation_ids = [v["axiom_id"] for v in audit.violations]
        assert "ACCT_001" in violation_ids

    def test_normative_audit_missing_rationale_warning(self):
        """Missing rationale triggers TRANSPARENCY warning."""
        fw = AxiomFramework()
        audit = fw.conduct_normative_audit(
            phase="TEST",
            evaluation_context={"actor": "SYSTEM"},
        )
        warning_ids = [w["axiom_id"] for w in audit.warnings]
        assert "TRANS_001" in warning_ids

    def test_get_axioms_by_category(self):
        """Axioms can be filtered by category."""
        fw = AxiomFramework()
        safety_axioms = fw.get_axioms_by_category(AxiomCategory.SAFETY)
        assert len(safety_axioms) >= 1
        assert all(a.category == AxiomCategory.SAFETY for a in safety_axioms)

    def test_compliance_summary_empty(self):
        """Compliance summary returns defaults when no audits exist."""
        fw = AxiomFramework()
        summary = fw.get_compliance_summary()
        assert summary["total_audits"] == 0
        assert summary["average_compliance_score"] == 1.0

    def test_meta_commentary(self):
        """Meta-commentary can be added and retrieved."""
        fw = AxiomFramework()
        commentary = fw.add_meta_commentary(
            context="unit test",
            observation="the framework is under test",
            implications=["coverage increases"],
            reflexivity_level=2,
        )
        assert commentary.reflexivity_level == 2
        results = fw.get_commentaries(min_reflexivity_level=2)
        assert len(results) == 1


# ---------------------------------------------------------------------------
# ResourceOptimizationLayer tests
# ---------------------------------------------------------------------------

class TestResourceOptimizationLayer:
    """Test allocation, usage recording, and waste detection."""

    def test_allocate_high_priority_full(self):
        """High-priority allocation (>=8) receives the full requested amount."""
        rol = ResourceOptimizationLayer()
        alloc = rol.allocate_resource(
            ResourceType.COMPUTE, "TEST", 100.0, "units", priority=10,
        )
        assert alloc.amount_allocated == 100.0

    def test_allocate_medium_priority_partial(self):
        """Medium-priority allocation receives less than full amount."""
        rol = ResourceOptimizationLayer()
        alloc = rol.allocate_resource(
            ResourceType.MEMORY, "TEST", 100.0, "MB", priority=5,
        )
        assert 80.0 <= alloc.amount_allocated < 100.0

    def test_record_usage_calculates_waste(self):
        """Recording usage calculates waste = allocated - used."""
        rol = ResourceOptimizationLayer()
        alloc = rol.allocate_resource(
            ResourceType.STORAGE, "TEST", 500.0, "GB", priority=10,
        )
        usage = rol.record_usage(alloc.allocation_id, 400.0)
        assert usage.amount_wasted == 100.0
        assert usage.efficiency == pytest.approx(0.8)

    def test_record_usage_nonexistent_raises(self):
        """Recording usage for a nonexistent allocation raises ValueError."""
        rol = ResourceOptimizationLayer()
        with pytest.raises(ValueError, match="not found"):
            rol.record_usage("FAKE_ALLOC", 100.0)

    def test_waste_governance_compliant(self):
        """Waste assessment returns COMPLIANT when under thresholds."""
        rol = ResourceOptimizationLayer()
        alloc = rol.allocate_resource(
            ResourceType.COMPUTE, "TEST", 100.0, "units", priority=10,
        )
        rol.record_usage(alloc.allocation_id, 95.0)  # 5% waste < 15% threshold
        assessment = rol.assess_waste_governance()
        assert assessment.compliance_status == "COMPLIANT"
        assert len(assessment.waste_threshold_breaches) == 0

    def test_waste_governance_non_compliant(self):
        """Waste assessment returns NON_COMPLIANT when over threshold."""
        rol = ResourceOptimizationLayer()
        alloc = rol.allocate_resource(
            ResourceType.API_CALLS, "TEST", 1000.0, "calls", priority=10,
        )
        # Use only 500 of 1000 -- 50% waste, threshold is 5% for API_CALLS
        rol.record_usage(alloc.allocation_id, 500.0)
        assessment = rol.assess_waste_governance()
        assert assessment.compliance_status == "NON_COMPLIANT"
        assert len(assessment.waste_threshold_breaches) > 0

    def test_utilization_stats_empty(self):
        """Utilization stats with no usages returns zero defaults."""
        rol = ResourceOptimizationLayer()
        stats = rol.get_utilization_stats()
        assert stats["count"] == 0
        assert stats["average_efficiency"] == 1.0

    def test_invalid_waste_threshold_raises(self):
        """Invalid waste threshold raises ValueError."""
        with pytest.raises(ValueError, match="Invalid waste threshold"):
            ResourceOptimizationLayer(waste_thresholds={ResourceType.COMPUTE: 1.5})


# ---------------------------------------------------------------------------
# StateManager tests
# ---------------------------------------------------------------------------

class TestStateManagerReproducibility:
    """Test snapshot creation, verification, and reproducibility info."""

    def test_snapshot_creation_and_retrieval(self):
        """Created snapshots can be retrieved by ID."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sm = StateManager(state_dir=tmpdir, random_seed=42)
            snap = sm.create_snapshot("snap-1", "INGESTION", {"key": "val"})
            retrieved = sm.get_snapshot("snap-1")
            assert retrieved is not None
            assert retrieved.state_hash == snap.state_hash

    def test_snapshot_verification_succeeds(self):
        """verify_snapshot returns True for untampered snapshots."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sm = StateManager(state_dir=tmpdir, random_seed=99)
            sm.create_snapshot("verify-me", "ANALYSIS", {"data": [1, 2, 3]})
            assert sm.verify_snapshot("verify-me") is True

    def test_snapshot_verification_fails_on_tamper(self):
        """verify_snapshot returns False when data is tampered."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sm = StateManager(state_dir=tmpdir, random_seed=99)
            snap = sm.create_snapshot("tamper-me", "ANALYSIS", {"data": "original"})
            # Tamper with the data in-memory
            snap.data = {"data": "tampered"}
            assert sm.verify_snapshot("tamper-me") is False

    def test_nonexistent_snapshot_verification_fails(self):
        """verify_snapshot returns False for nonexistent snapshot."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sm = StateManager(state_dir=tmpdir, random_seed=1)
            assert sm.verify_snapshot("does-not-exist") is False

    def test_reproducibility_info_includes_seed(self):
        """Reproducibility info reports the configured random seed."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sm = StateManager(state_dir=tmpdir, random_seed=7777)
            info = sm.get_reproducibility_info()
            assert info["random_seed"] == 7777
            assert info["config_hash"] != ""
            assert info["snapshots_count"] == 0

    def test_pin_model(self):
        """Pinning a model records it in reproducibility info."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sm = StateManager(state_dir=tmpdir, random_seed=1)
            sm.pin_model("gpt-4o", "2025-05-13")
            info = sm.get_reproducibility_info()
            assert info["model_pins"]["gpt-4o"] == "2025-05-13"

    def test_get_all_snapshots(self):
        """get_all_snapshots returns all created snapshots."""
        with tempfile.TemporaryDirectory() as tmpdir:
            sm = StateManager(state_dir=tmpdir, random_seed=1)
            sm.create_snapshot("a", "P1", {"x": 1})
            sm.create_snapshot("b", "P2", {"y": 2})
            all_snaps = sm.get_all_snapshots()
            assert len(all_snaps) == 2
            assert "a" in all_snaps
            assert "b" in all_snaps
