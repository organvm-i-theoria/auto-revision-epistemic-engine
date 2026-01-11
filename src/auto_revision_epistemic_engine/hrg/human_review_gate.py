"""
Human Review Gates (HRG) with clear SLAs and escalation mechanisms
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class ReviewStatus(str, Enum):
    """Status of a review"""
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"
    EXPIRED = "EXPIRED"


class EscalationLevel(str, Enum):
    """Escalation levels"""
    NONE = "NONE"
    LEVEL_1 = "LEVEL_1"  # Team lead
    LEVEL_2 = "LEVEL_2"  # Manager
    LEVEL_3 = "LEVEL_3"  # Director
    CRITICAL = "CRITICAL"  # Executive


class SLA(BaseModel):
    """Service Level Agreement for reviews"""
    response_time_hours: float
    resolution_time_hours: float
    escalation_time_hours: float


class HRGReview(BaseModel):
    """Human Review Gate review record"""
    review_id: str
    gate_name: str
    phase: str
    created_at: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    status: ReviewStatus = ReviewStatus.PENDING
    assigned_to: Optional[str] = None
    reviewer: Optional[str] = None
    decision: Optional[str] = None
    rationale: Optional[str] = None
    escalation_level: EscalationLevel = EscalationLevel.NONE
    sla: SLA
    responded_at: Optional[str] = None
    resolved_at: Optional[str] = None
    context: Dict[str, Any] = Field(default_factory=dict)
    artifacts: List[str] = Field(default_factory=list)


class EscalationEvent(BaseModel):
    """Escalation event record"""
    event_id: str
    review_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    from_level: EscalationLevel
    to_level: EscalationLevel
    reason: str
    escalated_to: str


class HumanReviewGate:
    """
    Human Review Gate (HRG) system with SLAs and escalation.
    Provides human oversight at critical junctions with governance.
    """

    def __init__(
        self,
        default_sla: Optional[SLA] = None,
    ):
        self.reviews: Dict[str, HRGReview] = {}
        self.escalations: List[EscalationEvent] = []
        
        # Default SLA if not specified
        self.default_sla = default_sla or SLA(
            response_time_hours=4.0,
            resolution_time_hours=24.0,
            escalation_time_hours=8.0,
        )
        
        # Gate configurations
        self.gates = {
            "GATE_1_INGESTION": {
                "phase": "ingestion",
                "description": "Review data ingestion and validation",
                "criticality": "high",
            },
            "GATE_2_PROCESSING": {
                "phase": "processing",
                "description": "Review processing strategy and approach",
                "criticality": "medium",
            },
            "GATE_3_VALIDATION": {
                "phase": "validation",
                "description": "Review validation results and quality metrics",
                "criticality": "high",
            },
            "GATE_4_FINALIZATION": {
                "phase": "finalization",
                "description": "Review final outputs and approve for release",
                "criticality": "critical",
            },
        }

    def request_review(
        self,
        gate_name: str,
        phase: str,
        assigned_to: str,
        context: Optional[Dict[str, Any]] = None,
        artifacts: Optional[List[str]] = None,
        custom_sla: Optional[SLA] = None,
    ) -> HRGReview:
        """
        Request a human review at a gate.

        Args:
            gate_name: Name of the gate
            phase: Phase requesting review
            assigned_to: Person or role assigned to review
            context: Review context and metadata
            artifacts: List of artifact references for review
            custom_sla: Custom SLA for this review

        Returns:
            HRGReview: The created review request
        """
        review_id = f"HRG_{gate_name}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}"
        
        review = HRGReview(
            review_id=review_id,
            gate_name=gate_name,
            phase=phase,
            assigned_to=assigned_to,
            sla=custom_sla or self.default_sla,
            context=context or {},
            artifacts=artifacts or [],
        )
        
        self.reviews[review_id] = review
        return review

    def start_review(self, review_id: str, reviewer: str) -> bool:
        """
        Start a review (mark as in progress).

        Args:
            review_id: Review ID
            reviewer: Person conducting the review

        Returns:
            bool: True if started successfully
        """
        if review_id not in self.reviews:
            return False
        
        review = self.reviews[review_id]
        if review.status != ReviewStatus.PENDING:
            return False
        
        review.status = ReviewStatus.IN_PROGRESS
        review.reviewer = reviewer
        review.responded_at = datetime.now(timezone.utc).isoformat()
        
        return True

    def complete_review(
        self,
        review_id: str,
        decision: str,
        rationale: str,
        reviewer: Optional[str] = None,
    ) -> bool:
        """
        Complete a review with a decision.

        Args:
            review_id: Review ID
            decision: Decision (APPROVE or REJECT)
            rationale: Rationale for the decision
            reviewer: Person completing the review

        Returns:
            bool: True if completed successfully
        """
        if review_id not in self.reviews:
            return False
        
        review = self.reviews[review_id]
        
        # Ensure reviewer is set
        if reviewer:
            review.reviewer = reviewer
        elif not getattr(review, "reviewer", None):
            # No reviewer set, cannot complete review
            return False
        review.decision = decision.upper()
        review.rationale = rationale
        review.resolved_at = datetime.now(timezone.utc).isoformat()
        
        if review.decision == "APPROVE":
            review.status = ReviewStatus.APPROVED
        elif review.decision == "REJECT":
            review.status = ReviewStatus.REJECTED
        
        return True

    def escalate_review(
        self,
        review_id: str,
        to_level: EscalationLevel,
        reason: str,
        escalated_to: str,
    ) -> EscalationEvent:
        """
        Escalate a review to a higher level.

        Args:
            review_id: Review ID
            to_level: Target escalation level
            reason: Reason for escalation
            escalated_to: Person or role escalated to

        Returns:
            EscalationEvent: The escalation event
        """
        if review_id not in self.reviews:
            raise ValueError(f"Review {review_id} not found")
        
        review = self.reviews[review_id]
        from_level = review.escalation_level
        
        event_id = f"ESC_{review_id}_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}"
        
        escalation = EscalationEvent(
            event_id=event_id,
            review_id=review_id,
            from_level=from_level,
            to_level=to_level,
            reason=reason,
            escalated_to=escalated_to,
        )
        
        # Update review
        review.escalation_level = to_level
        review.status = ReviewStatus.ESCALATED
        review.assigned_to = escalated_to
        
        self.escalations.append(escalation)
        return escalation

    def check_sla_compliance(self) -> List[Dict[str, Any]]:
        """
        Check SLA compliance for all pending/in-progress reviews.

        Returns:
            List of SLA violations
        """
        violations = []
        now = datetime.now(timezone.utc)
        
        for review in self.reviews.values():
            if review.status in [ReviewStatus.PENDING, ReviewStatus.IN_PROGRESS]:
                created_at = datetime.fromisoformat(review.created_at)
                elapsed_hours = (now - created_at).total_seconds() / 3600
                
                # Check response time
                if review.status == ReviewStatus.PENDING:
                    if elapsed_hours > review.sla.response_time_hours:
                        violations.append({
                            "review_id": review.review_id,
                            "violation_type": "RESPONSE_TIME",
                            "elapsed_hours": elapsed_hours,
                            "sla_hours": review.sla.response_time_hours,
                        })
                
                # Check resolution time
                if elapsed_hours > review.sla.resolution_time_hours:
                    violations.append({
                        "review_id": review.review_id,
                        "violation_type": "RESOLUTION_TIME",
                        "elapsed_hours": elapsed_hours,
                        "sla_hours": review.sla.resolution_time_hours,
                    })
                
                # Check escalation time
                if (
                    elapsed_hours > review.sla.escalation_time_hours
                    and review.escalation_level == EscalationLevel.NONE
                ):
                    violations.append({
                        "review_id": review.review_id,
                        "violation_type": "ESCALATION_REQUIRED",
                        "elapsed_hours": elapsed_hours,
                        "sla_hours": review.sla.escalation_time_hours,
                    })
        
        return violations

    def auto_escalate_expired(self) -> List[str]:
        """
        Automatically escalate reviews that have exceeded escalation SLA.

        Returns:
            List of escalated review IDs
        """
        violations = self.check_sla_compliance()
        escalated = []
        
        for violation in violations:
            if violation["violation_type"] == "ESCALATION_REQUIRED":
                review_id = violation["review_id"]
                review = self.reviews[review_id]
                
                # Determine next escalation level
                next_level = self._get_next_escalation_level(review.escalation_level)
                
                # Escalate
                self.escalate_review(
                    review_id=review_id,
                    to_level=next_level,
                    reason="Auto-escalation due to SLA violation",
                    escalated_to=f"escalation_{next_level.value}",
                )
                
                escalated.append(review_id)
        
        return escalated

    def _get_next_escalation_level(self, current_level: EscalationLevel) -> EscalationLevel:
        """Get next escalation level"""
        levels = [
            EscalationLevel.NONE,
            EscalationLevel.LEVEL_1,
            EscalationLevel.LEVEL_2,
            EscalationLevel.LEVEL_3,
            EscalationLevel.CRITICAL,
        ]
        
        if current_level in levels:
            current_idx = levels.index(current_level)
            if current_idx < len(levels) - 1:
                return levels[current_idx + 1]
        # If current_level is not found, escalate to CRITICAL as a safe fallback.
        return EscalationLevel.CRITICAL

    def get_pending_reviews(
        self,
        assigned_to: Optional[str] = None,
        gate_name: Optional[str] = None,
    ) -> List[HRGReview]:
        """
        Get pending reviews.

        Args:
            assigned_to: Filter by assigned person
            gate_name: Filter by gate name

        Returns:
            List of pending reviews
        """
        reviews = [
            r for r in self.reviews.values()
            if r.status in [ReviewStatus.PENDING, ReviewStatus.IN_PROGRESS]
        ]
        
        if assigned_to:
            reviews = [r for r in reviews if r.assigned_to == assigned_to]
        
        if gate_name:
            reviews = [r for r in reviews if r.gate_name == gate_name]
        
        return reviews

    def get_review_statistics(self) -> Dict[str, Any]:
        """
        Get review statistics.

        Returns:
            Dict with review statistics
        """
        total = len(self.reviews)
        if total == 0:
            return {
                "total_reviews": 0,
                "by_status": {},
                "by_gate": {},
                "average_resolution_time_hours": 0.0,
                "sla_compliance_rate": 1.0,
            }
        
        by_status = {}
        by_gate = {}
        resolution_times = []
        sla_compliant = 0
        
        for review in self.reviews.values():
            # Count by status
            status = review.status.value
            by_status[status] = by_status.get(status, 0) + 1
            
            # Count by gate
            gate = review.gate_name
            by_gate[gate] = by_gate.get(gate, 0) + 1
            
            # Calculate resolution time
            if review.resolved_at:
                created = datetime.fromisoformat(review.created_at)
                resolved = datetime.fromisoformat(review.resolved_at)
                hours = (resolved - created).total_seconds() / 3600
                resolution_times.append(hours)
                
                # Check SLA compliance
                if hours <= review.sla.resolution_time_hours:
                    sla_compliant += 1
        
        avg_resolution = (
            sum(resolution_times) / len(resolution_times)
            if resolution_times
            else 0.0
        )
        
        sla_rate = (
            sla_compliant / len(resolution_times)
            if resolution_times
            else 1.0
        )
        
        return {
            "total_reviews": total,
            "by_status": by_status,
            "by_gate": by_gate,
            "average_resolution_time_hours": avg_resolution,
            "sla_compliance_rate": sla_rate,
            "total_escalations": len(self.escalations),
        }
