@@
-from datetime import datetime
+from datetime import datetime
 from typing import Any, Dict, List, Optional
 from pydantic import BaseModel, Field
+from pathlib import Path
@@
-from ..phases.phase_manager import PhaseManager, PhaseName, PhaseStatus
+from ..phases.phase_manager import PhaseManager, PhaseName, PhaseStatus
 from ..hrg.human_review_gate import HumanReviewGate, ReviewStatus
 from ..rol_t.resource_optimizer import ResourceOptimizationLayer, ResourceType
 from ..reproducibility.state_manager import StateManager
 from ..ethics.axiom_framework import AxiomFramework
 from ..audit.audit_logger import AuditLogger
+from .agent_manifest_loader import load_agent_manifest
@@ class Orchestrator:
     def __init__(self, config: PipelineConfig):
         self.config = config
@@
-        self.ethics = AxiomFramework() if config.enable_ethics_audit else None
+        self.ethics = AxiomFramework() if config.enable_ethics_audit else None
         self.audit_logger = AuditLogger(log_dir=config.audit_log_dir)
@@
+        # Governance anchors & agent manifest
+        self.governance = {
+            "axioms_path": str(Path("governance/AXIOMS.md").resolve()),
+            "ethics_path": str(Path("governance/ETHICS.md").resolve()),
+        }
+        self.agent_manifest = load_agent_manifest()
+        self.audit_logger.log_event(
+            event_type="GOVERNANCE_LOAD",
+            actor="SYSTEM",
+            action="Loaded governance anchors and agent manifest",
+            metadata={
+                "axioms_exists": Path(self.governance["axioms_path"]).exists(),
+                "ethics_exists": Path(self.governance["ethics_path"]).exists(),
+                "agents": list(self.agent_manifest.get("agents", {}).keys()),
+                "pinned": self.agent_manifest.get("pinned", False),
+            },
+        )