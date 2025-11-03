"""
Axiom Framework for ethics and reflexivity with normative audits and meta-commentary
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class AxiomCategory(str, Enum):
    """Categories of ethical axioms"""
    FAIRNESS = "FAIRNESS"
    TRANSPARENCY = "TRANSPARENCY"
    ACCOUNTABILITY = "ACCOUNTABILITY"
    PRIVACY = "PRIVACY"
    SAFETY = "SAFETY"
    BENEFICENCE = "BENEFICENCE"
    NON_MALEFICENCE = "NON_MALEFICENCE"
    AUTONOMY = "AUTONOMY"


class Axiom(BaseModel):
    """Single ethical axiom"""
    axiom_id: str
    category: AxiomCategory
    statement: str
    weight: float = 1.0
    enforcement_level: str = "WARN"  # BLOCK, WARN, LOG


class NormativeAudit(BaseModel):
    """Normative audit result"""
    audit_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    phase: str
    axioms_evaluated: List[str]
    violations: List[Dict[str, Any]] = Field(default_factory=list)
    warnings: List[Dict[str, Any]] = Field(default_factory=list)
    compliance_score: float = 1.0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class MetaCommentary(BaseModel):
    """Meta-commentary on system behavior"""
    commentary_id: str
    timestamp: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())
    context: str
    observation: str
    implications: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    reflexivity_level: int = 1  # Depth of meta-reflection


class AxiomFramework:
    """
    Ethics and reflexivity framework with axioms, normative audits, and meta-commentary.
    Ensures ethical operation and reflexive self-monitoring.
    """

    def __init__(self):
        self.axioms: Dict[str, Axiom] = {}
        self.audits: List[NormativeAudit] = []
        self.commentaries: List[MetaCommentary] = []
        self._initialize_default_axioms()

    def _initialize_default_axioms(self):
        """Initialize default ethical axioms"""
        default_axioms = [
            Axiom(
                axiom_id="FAIR_001",
                category=AxiomCategory.FAIRNESS,
                statement="All actors must have equitable access to oversight mechanisms",
                weight=1.0,
                enforcement_level="WARN",
            ),
            Axiom(
                axiom_id="TRANS_001",
                category=AxiomCategory.TRANSPARENCY,
                statement="All decisions must be logged with clear rationale",
                weight=1.0,
                enforcement_level="WARN",
            ),
            Axiom(
                axiom_id="ACCT_001",
                category=AxiomCategory.ACCOUNTABILITY,
                statement="Every action must have a traceable actor or system component",
                weight=1.0,
                enforcement_level="BLOCK",
            ),
            Axiom(
                axiom_id="PRIV_001",
                category=AxiomCategory.PRIVACY,
                statement="Sensitive data must be handled with appropriate protections",
                weight=1.0,
                enforcement_level="BLOCK",
            ),
            Axiom(
                axiom_id="SAFE_001",
                category=AxiomCategory.SAFETY,
                statement="Operations must not cause harm to systems or stakeholders",
                weight=1.5,
                enforcement_level="BLOCK",
            ),
            Axiom(
                axiom_id="BENEF_001",
                category=AxiomCategory.BENEFICENCE,
                statement="System should actively promote beneficial outcomes",
                weight=0.8,
                enforcement_level="LOG",
            ),
            Axiom(
                axiom_id="NON_MAL_001",
                category=AxiomCategory.NON_MALEFICENCE,
                statement="System must avoid causing harm even through inaction",
                weight=1.5,
                enforcement_level="BLOCK",
            ),
            Axiom(
                axiom_id="AUTO_001",
                category=AxiomCategory.AUTONOMY,
                statement="Human oversight must retain meaningful control over critical decisions",
                weight=1.2,
                enforcement_level="WARN",
            ),
        ]
        
        for axiom in default_axioms:
            self.axioms[axiom.axiom_id] = axiom

    def add_axiom(self, axiom: Axiom):
        """
        Add a new ethical axiom.

        Args:
            axiom: Axiom to add
        """
        self.axioms[axiom.axiom_id] = axiom

    def remove_axiom(self, axiom_id: str) -> bool:
        """
        Remove an axiom.

        Args:
            axiom_id: ID of axiom to remove

        Returns:
            bool: True if removed, False if not found
        """
        if axiom_id in self.axioms:
            del self.axioms[axiom_id]
            return True
        return False

    def conduct_normative_audit(
        self,
        phase: str,
        evaluation_context: Dict[str, Any],
        axiom_ids: Optional[List[str]] = None,
    ) -> NormativeAudit:
        """
        Conduct a normative audit against ethical axioms.

        Args:
            phase: Phase being audited
            evaluation_context: Context for evaluation
            axiom_ids: Specific axioms to evaluate (if None, evaluates all)

        Returns:
            NormativeAudit: Audit results
        """
        audit_id = f"AUDIT_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Select axioms to evaluate
        if axiom_ids:
            axioms_to_eval = [self.axioms[aid] for aid in axiom_ids if aid in self.axioms]
        else:
            axioms_to_eval = list(self.axioms.values())
        
        violations = []
        warnings = []
        total_weight = sum(a.weight for a in axioms_to_eval)
        compliance_weight = 0.0
        
        # Evaluate each axiom
        for axiom in axioms_to_eval:
            # Simplified evaluation - in production, this would involve complex checks
            violation_detected = self._evaluate_axiom(axiom, evaluation_context)
            
            if violation_detected:
                issue = {
                    "axiom_id": axiom.axiom_id,
                    "category": axiom.category,
                    "statement": axiom.statement,
                    "enforcement_level": axiom.enforcement_level,
                    "context": violation_detected,
                }
                
                if axiom.enforcement_level == "BLOCK":
                    violations.append(issue)
                elif axiom.enforcement_level == "WARN":
                    warnings.append(issue)
                # LOG level just gets recorded in metadata
            else:
                compliance_weight += axiom.weight
        
        # Calculate compliance score
        compliance_score = compliance_weight / total_weight if total_weight > 0 else 1.0
        
        audit = NormativeAudit(
            audit_id=audit_id,
            phase=phase,
            axioms_evaluated=[a.axiom_id for a in axioms_to_eval],
            violations=violations,
            warnings=warnings,
            compliance_score=compliance_score,
            metadata=evaluation_context,
        )
        
        self.audits.append(audit)
        return audit

    def _evaluate_axiom(
        self,
        axiom: Axiom,
        context: Dict[str, Any],
    ) -> Optional[str]:
        """
        Evaluate a single axiom against context.

        Args:
            axiom: Axiom to evaluate
            context: Evaluation context

        Returns:
            Optional[str]: Violation description if detected, None if compliant
        """
        # Simplified evaluation logic - production would be more sophisticated
        
        if axiom.category == AxiomCategory.ACCOUNTABILITY:
            if "actor" not in context or not context.get("actor"):
                return "No actor identified for action"
        
        elif axiom.category == AxiomCategory.TRANSPARENCY:
            if "rationale" not in context or not context.get("rationale"):
                return "No rationale provided for decision"
        
        elif axiom.category == AxiomCategory.PRIVACY:
            if context.get("contains_sensitive_data", False):
                if not context.get("privacy_protections_applied", False):
                    return "Sensitive data without privacy protections"
        
        elif axiom.category == AxiomCategory.SAFETY:
            if context.get("risk_level", "low") in ["high", "critical"]:
                if not context.get("safety_review_completed", False):
                    return "High-risk operation without safety review"
        
        # No violation detected
        return None

    def add_meta_commentary(
        self,
        context: str,
        observation: str,
        implications: Optional[List[str]] = None,
        recommendations: Optional[List[str]] = None,
        reflexivity_level: int = 1,
    ) -> MetaCommentary:
        """
        Add meta-commentary on system behavior.

        Args:
            context: Context of the observation
            observation: The observation itself
            implications: Implications of the observation
            recommendations: Recommendations based on observation
            reflexivity_level: Depth of meta-reflection

        Returns:
            MetaCommentary: The created meta-commentary
        """
        commentary_id = f"META_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S_%f')}"
        
        commentary = MetaCommentary(
            commentary_id=commentary_id,
            context=context,
            observation=observation,
            implications=implications or [],
            recommendations=recommendations or [],
            reflexivity_level=reflexivity_level,
        )
        
        self.commentaries.append(commentary)
        return commentary

    def get_audits(
        self,
        phase: Optional[str] = None,
        min_compliance_score: Optional[float] = None,
    ) -> List[NormativeAudit]:
        """
        Get normative audits with optional filters.

        Args:
            phase: Filter by phase
            min_compliance_score: Minimum compliance score

        Returns:
            List of matching audits
        """
        audits = self.audits
        
        if phase:
            audits = [a for a in audits if a.phase == phase]
        
        if min_compliance_score is not None:
            audits = [a for a in audits if a.compliance_score >= min_compliance_score]
        
        return audits

    def get_commentaries(
        self,
        context: Optional[str] = None,
        min_reflexivity_level: Optional[int] = None,
    ) -> List[MetaCommentary]:
        """
        Get meta-commentaries with optional filters.

        Args:
            context: Filter by context substring
            min_reflexivity_level: Minimum reflexivity level

        Returns:
            List of matching commentaries
        """
        commentaries = self.commentaries
        
        if context:
            commentaries = [c for c in commentaries if context in c.context]
        
        if min_reflexivity_level is not None:
            commentaries = [
                c for c in commentaries if c.reflexivity_level >= min_reflexivity_level
            ]
        
        return commentaries

    def get_axioms_by_category(self, category: AxiomCategory) -> List[Axiom]:
        """
        Get axioms by category.

        Args:
            category: Axiom category

        Returns:
            List of axioms in that category
        """
        return [a for a in self.axioms.values() if a.category == category]

    def get_compliance_summary(self) -> Dict[str, Any]:
        """
        Get overall compliance summary.

        Returns:
            Dict with compliance statistics
        """
        if not self.audits:
            return {
                "total_audits": 0,
                "average_compliance_score": 1.0,
                "total_violations": 0,
                "total_warnings": 0,
            }
        
        return {
            "total_audits": len(self.audits),
            "average_compliance_score": sum(a.compliance_score for a in self.audits) / len(self.audits),
            "total_violations": sum(len(a.violations) for a in self.audits),
            "total_warnings": sum(len(a.warnings) for a in self.audits),
            "recent_audits": len([a for a in self.audits[-10:]]),
        }
