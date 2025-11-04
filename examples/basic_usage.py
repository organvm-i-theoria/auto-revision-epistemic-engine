"""
Example usage of the Auto-Revision Epistemic Engine
"""

from auto_revision_epistemic_engine import AutoRevisionEngine


def main():
    """Demonstrate the Auto-Revision Epistemic Engine"""
    
    print("=" * 80)
    print("Auto-Revision Epistemic Engine v4.2 - Example Execution")
    print("=" * 80)
    print()
    
    # Initialize the engine
    print("1. Initializing engine with full governance...")
    engine = AutoRevisionEngine(
        pipeline_id="example_pipeline_001",
        random_seed=42,
        enable_hrg=True,
        enable_ethics_audit=True,
        enable_resource_tracking=True,
        audit_log_dir="./example_audit_logs",
        state_dir="./example_state_snapshots",
    )
    print("   ✓ Engine initialized")
    print()
    
    # Pin models for reproducibility
    print("2. Pinning models for reproducibility...")
    engine.pin_model("gpt-4", "20240101_snapshot")
    engine.pin_model("bert-base", "v2.1.0")
    print("   ✓ Models pinned")
    print()
    
    # Add custom ethical axiom
    print("3. Adding custom ethical axiom...")
    engine.add_ethical_axiom(
        axiom_id="CUSTOM_001",
        category="TRANSPARENCY",
        statement="All processing steps must document their methodology",
        weight=1.0,
        enforcement_level="WARN",
    )
    print("   ✓ Custom axiom added")
    print()
    
    # Execute pipeline
    print("4. Executing 8-phase pipeline...")
    print("   Phases: Ingestion → Preprocessing → Processing → Analysis →")
    print("           Validation → Synthesis → Review → Finalization")
    print()
    
    result = engine.execute(
        inputs={
            "data": {"records": 100},
            "config": {"mode": "standard"},
        }
    )
    
    if result["success"]:
        print("   ✓ Pipeline completed successfully!")
    else:
        print(f"   ✗ Pipeline failed: {result.get('error')}")
    print()
    
    # Get comprehensive status
    print("5. Retrieving pipeline status...")
    status = engine.get_status()
    print(f"   Pipeline ID: {status['pipeline_id']}")
    print(f"   Started: {status['started']}")
    print(f"   Completed: {status['completed']}")
    print(f"   Phase Progress: {status['phase_status']['progress_percentage']:.1f}%")
    print(f"   Audit Chain Valid: {status['audit_chain_valid']}")
    print()
    
    # Get audit trail
    print("6. Audit Trail Summary...")
    audit = engine.get_audit_trail()
    print(f"   Total Audit Entries: {audit['total_entries']}")
    print(f"   Chain Integrity: {'✓ Valid' if audit['chain_valid'] else '✗ Invalid'}")
    print(f"   Compliance Attestations: {len(audit['attestations'])}")
    print()
    
    # Get reproducibility info
    print("7. Reproducibility Information...")
    repro = engine.get_reproducibility_info()
    print(f"   Config Hash: {repro['config_hash'][:16]}...")
    print(f"   Random Seed: {repro['random_seed']}")
    print(f"   Model Pins: {len(repro['model_pins'])}")
    print(f"   State Snapshots: {repro['snapshots_count']}")
    print()
    
    # Get resource report
    print("8. Resource Optimization Report...")
    resources = engine.get_resource_report()
    if resources['enabled']:
        stats = resources['utilization_stats']
        print(f"   Average Efficiency: {stats['average_efficiency']:.2%}")
        print(f"   Total Waste: {stats['total_waste']:.2f} units")
        print(f"   Total Used: {stats['total_used']:.2f} units")
    print()
    
    # Get ethics report
    print("9. Ethics Compliance Report...")
    ethics = engine.get_ethics_report()
    if ethics['enabled']:
        summary = ethics['compliance_summary']
        print(f"   Total Audits: {summary['total_audits']}")
        print(f"   Average Compliance: {summary['average_compliance_score']:.2%}")
        print(f"   Total Violations: {summary['total_violations']}")
        print(f"   Total Warnings: {summary['total_warnings']}")
    print()
    
    # Get HRG report
    print("10. Human Review Gate Report...")
    hrg = engine.get_hrg_report()
    if hrg['enabled']:
        stats = hrg['statistics']
        print(f"   Total Reviews: {stats['total_reviews']}")
        print(f"   SLA Compliance Rate: {stats['sla_compliance_rate']:.2%}")
        print(f"   Pending Reviews: {hrg['pending_reviews']}")
        print(f"   Total Escalations: {stats['total_escalations']}")
    print()
    
    print("=" * 80)
    print("✓ Example execution completed successfully!")
    print("=" * 80)
    print()
    print("Key Features Demonstrated:")
    print("  ✓ 8 phases with human oversight at 4 gates")
    print("  ✓ HRGs with SLAs and escalation")
    print("  ✓ ROL-T resource optimization and waste governance")
    print("  ✓ Reproducibility via pinned models and seeds")
    print("  ✓ Ethics and reflexivity framework")
    print("  ✓ Full auditability with BLAKE3 hashing")
    print()


if __name__ == "__main__":
    main()
