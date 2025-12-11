from pathlib import Path
from typing import Any, Dict
import yaml

def load_agent_manifest(path: str = "config/agent_manifest.yaml") -> Dict[str, Any]:
    p = Path(path)
    if not p.exists():
        return {"agents": {}, "fallback_strategy": [], "pinned": False}
    data = yaml.safe_load(p.read_text(encoding="utf-8")) or {}
    # Basic validation
    if "agents" not in data or not isinstance(data["agents"], dict):
        raise ValueError("agent_manifest.yaml missing required 'agents' map")
    return data