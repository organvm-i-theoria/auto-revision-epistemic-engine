# Auto-Revision Epistemic Engine (v4.2)

The Auto-Rev-Epistemic-Engine is a self-governing orchestration framework with eight phases and four human oversight gates. It balances automation and governance via HRGs, RBAC, and SLAs, ensuring reproducibility, ethical audits, and full auditability through append-only logs and BLAKE3 hashing.

## Features

### ✅ 8-Phase Pipeline with Human Oversight
Integrates 8 phases (ingestion → finalization) with human oversight at 4 critical gates:
- **Phase 1: INGESTION** - Data and request ingestion (HRG Gate 1)
- **Phase 2: PREPROCESSING** - Data cleaning and preparation
- **Phase 3: PROCESSING** - Main processing logic (HRG Gate 2)
- **Phase 4: ANALYSIS** - Analysis and pattern detection
- **Phase 5: VALIDATION** - Quality validation and checks (HRG Gate 3)
- **Phase 6: SYNTHESIS** - Result synthesis
- **Phase 7: REVIEW** - Human review and approval
- **Phase 8: FINALIZATION** - Final packaging and delivery (HRG Gate 4)

### ✅ Human Review Gates (HRGs)
Balances automation & governance via HRGs with clear SLAs and escalation:
- **Response Time SLA**: 4 hours (configurable)
- **Resolution Time SLA**: 24 hours (configurable)
- **Auto-escalation**: 8 hours (configurable)
- **Escalation Levels**: L1 (Team Lead) → L2 (Manager) → L3 (Director) → Critical (Executive)

### ✅ Resource Optimization Layer-Tracking (ROL-T)
Optimizes resources via ROL-T with utilization tracking and waste governance:
- Tracks compute, memory, storage, network, API calls, and human time
- Waste thresholds by resource type (configurable)
- Automatic efficiency calculations
- Waste governance assessments with compliance reporting

### ✅ Reproducibility
Ensures reproducibility via pinned models, seeds, and immutable state:
- **Pinned Models**: Version-lock models for consistent results
- **Random Seeds**: Deterministic random number generation
- **Immutable State Snapshots**: BLAKE3-hashed state captures
- **Environment Snapshots**: Full environment configuration tracking

### ✅ Ethics & Reflexivity
Embeds ethics & reflexivity via axioms, normative audit, and meta-commentary:
- **8 Default Ethical Axioms**: Fairness, Transparency, Accountability, Privacy, Safety, Beneficence, Non-maleficence, Autonomy
- **Normative Audits**: Pre/post-phase ethical compliance checks
- **Meta-commentary**: Reflexive system behavior analysis
- **Configurable Enforcement**: BLOCK, WARN, or LOG levels

### ✅ Full Auditability
Provides full auditability via append-only logs, BLAKE3 hashing, and compliance attestations:
- **Append-only Audit Log**: Immutable event chain
- **BLAKE3 Hashing**: Cryptographic integrity verification
- **Chain Verification**: Detect any tampering
- **Compliance Attestations**: Resource, ethics, and reproducibility compliance

## Installation

```bash
pip install -r requirements.txt
pip install -e .
```

## Quick Start

```python
from auto_revision_epistemic_engine import AutoRevisionEngine

# Initialize engine
engine = AutoRevisionEngine(
    pipeline_id="my_pipeline",
    random_seed=42,
    enable_hrg=True,
    enable_ethics_audit=True,
    enable_resource_tracking=True,
)

# Pin models for reproducibility
engine.pin_model("gpt-4", "20240101_snapshot")

# Execute pipeline
result = engine.execute(
    inputs={"data": {"records": 100}}
)

# Get comprehensive status
status = engine.get_status()
print(f"Pipeline completed: {status['completed']}")
print(f"Audit chain valid: {status['audit_chain_valid']}")
```

## Architecture

```
Auto-Revision Epistemic Engine
├── Core Engine (engine.py)
│   └── Orchestrator (orchestrator.py)
│       ├── Phase Manager (8 phases)
│       ├── Human Review Gates (HRGs)
│       ├── Resource Optimization Layer (ROL-T)
│       ├── State Manager (Reproducibility)
│       ├── Axiom Framework (Ethics)
│       └── Audit Logger (Auditability)
```

## Components

### Phase Manager
Manages the 8-phase orchestration pipeline with status tracking, metrics, and HRG integration.

**Key Methods:**
- `start_phase()` - Begin phase execution
- `complete_phase()` - Mark phase as completed
- `fail_phase()` - Mark phase as failed
- `block_phase()` - Block phase (waiting for HRG)
- `get_pipeline_status()` - Get overall status

### Human Review Gate (HRG)
Provides human oversight at critical junctions with SLA management and escalation.

**Key Methods:**
- `request_review()` - Request human review
- `start_review()` - Begin reviewing
- `complete_review()` - Complete with decision
- `escalate_review()` - Escalate to higher level
- `check_sla_compliance()` - Check SLA violations

### Resource Optimization Layer (ROL-T)
Tracks and optimizes resource utilization with waste governance.

**Key Methods:**
- `allocate_resource()` - Allocate resources
- `record_usage()` - Record actual usage
- `assess_waste_governance()` - Assess compliance
- `get_utilization_stats()` - Get statistics

### State Manager
Manages reproducibility through configuration, snapshots, and verification.

**Key Methods:**
- `pin_model()` - Pin model version
- `create_snapshot()` - Create immutable snapshot
- `get_snapshot()` - Retrieve snapshot
- `verify_snapshot()` - Verify integrity

### Axiom Framework
Embeds ethics and reflexivity with normative audits.

**Key Methods:**
- `add_axiom()` - Add ethical axiom
- `conduct_normative_audit()` - Audit compliance
- `add_meta_commentary()` - Add reflexive commentary
- `get_compliance_summary()` - Get summary

### Audit Logger
Provides append-only logging with BLAKE3 hashing.

**Key Methods:**
- `log_event()` - Log audit event
- `create_attestation()` - Create compliance attestation
- `verify_chain()` - Verify log integrity
- `get_entries()` - Query log entries

## Configuration

### Pipeline Config
```python
config = PipelineConfig(
    pipeline_id="unique_id",
    random_seed=42,
    enable_hrg=True,
    enable_ethics_audit=True,
    enable_resource_tracking=True,
    audit_log_dir="./audit_logs",
    state_dir="./state_snapshots",
)
```

### SLA Configuration
```python
from auto_revision_epistemic_engine.hrg import SLA

custom_sla = SLA(
    response_time_hours=2.0,
    resolution_time_hours=12.0,
    escalation_time_hours=4.0,
)
```

### Waste Thresholds
```python
from auto_revision_epistemic_engine.rol_t import ResourceType

waste_thresholds = {
    ResourceType.COMPUTE: 0.10,  # 10%
    ResourceType.MEMORY: 0.15,   # 15%
    ResourceType.STORAGE: 0.05,  # 5%
}
```

## Example Usage

See `examples/basic_usage.py` for a complete example demonstrating all features.

```bash
cd examples
python basic_usage.py
```

## API Reference

### AutoRevisionEngine

Main entry point for the engine.

**Constructor Parameters:**
- `pipeline_id` (str): Unique pipeline identifier
- `random_seed` (Optional[int]): Random seed for reproducibility
- `enable_hrg` (bool): Enable Human Review Gates
- `enable_ethics_audit` (bool): Enable ethics auditing
- `enable_resource_tracking` (bool): Enable resource tracking
- `audit_log_dir` (str): Audit log directory path
- `state_dir` (str): State snapshot directory path

**Methods:**
- `execute(inputs)` - Execute complete pipeline
- `get_status()` - Get pipeline status
- `get_audit_trail()` - Get audit trail
- `get_reproducibility_info()` - Get reproducibility info
- `get_resource_report()` - Get resource report
- `get_ethics_report()` - Get ethics report
- `get_hrg_report()` - Get HRG report
- `pin_model(name, version)` - Pin model version
- `add_ethical_axiom(...)` - Add custom axiom

## Compliance & Governance

### Audit Trail
All operations are logged to an append-only audit log with BLAKE3 hashing:
- Event type, timestamp, actor, action
- Phase context and metadata
- Cryptographic chain linking

### Reproducibility
Ensures exact reproducibility through:
- Pinned model versions
- Fixed random seeds
- Immutable state snapshots
- Configuration hashing

### Ethics
Enforces ethical guidelines through:
- Pre-defined ethical axioms
- Custom axiom support
- Normative audits (pre/post phase)
- Configurable enforcement levels

### Resource Governance
Manages resources through:
- Allocation tracking
- Usage monitoring
- Waste threshold enforcement
- Compliance assessments

### Human Oversight
Balances automation with human judgment:
- 4 strategic review gates
- SLA-driven processes
- Automatic escalation
- Decision auditability

## Testing

Run tests to verify implementation:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=auto_revision_epistemic_engine --cov-report=html
```

## License

See LICENSE file for details.

## Version

**v4.2.0** - Full governance, reproducibility, and auditability

## Support

For issues, questions, or contributions, please visit the repository.
