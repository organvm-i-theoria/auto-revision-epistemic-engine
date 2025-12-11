"""
Auto-Revision Epistemic Engine (v4.2)

A self-governing orchestration framework with eight phases and four human oversight gates.
Balances automation and governance via HRGs, RBAC, and SLAs, ensuring reproducibility,
ethical audits, and full auditability through append-only logs and BLAKE3 hashing.
"""

__version__ = "4.2.0"

from .core.engine import AutoRevisionEngine
from .core.orchestrator import Orchestrator
from .phases.phase_manager import PhaseManager
from .hrg.human_review_gate import HumanReviewGate
from .rol_t.resource_optimizer import ResourceOptimizationLayer
from .reproducibility.state_manager import StateManager
from .ethics.axiom_framework import AxiomFramework
from .audit.audit_logger import AuditLogger

__all__ = [
    "AutoRevisionEngine",
    "Orchestrator",
    "PhaseManager",
    "HumanReviewGate",
    "ResourceOptimizationLayer",
    "StateManager",
    "AxiomFramework",
    "AuditLogger",
]
