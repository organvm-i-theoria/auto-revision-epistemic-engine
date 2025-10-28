"""
Resource Optimization Layer-Tracking (ROL-T) for utilization tracking and waste governance
"""

from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from enum import Enum


class ResourceType(str, Enum):
    """Types of resources tracked"""
    COMPUTE = "COMPUTE"
    MEMORY = "MEMORY"
    STORAGE = "STORAGE"
    NETWORK = "NETWORK"
    API_CALLS = "API_CALLS"
    HUMAN_TIME = "HUMAN_TIME"


class ResourceAllocation(BaseModel):
    """Resource allocation record"""
    allocation_id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    resource_type: ResourceType
    phase: str
    amount_requested: float
    amount_allocated: float
    unit: str
    priority: int = 5  # 1-10 scale


class ResourceUsage(BaseModel):
    """Resource usage record"""
    usage_id: str
    allocation_id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    resource_type: ResourceType
    phase: str
    amount_used: float
    amount_wasted: float = 0.0
    unit: str
    efficiency: float = 1.0


class WasteGovernance(BaseModel):
    """Waste governance assessment"""
    assessment_id: str
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    time_period: str
    total_waste: Dict[str, float] = Field(default_factory=dict)
    waste_threshold_breaches: List[str] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)
    compliance_status: str = "COMPLIANT"


class ResourceOptimizationLayer:
    """
    ROL-T (Resource Optimization Layer-Tracking) for comprehensive resource management.
    Tracks utilization, identifies waste, and enforces governance policies.
    """

    def __init__(self, waste_thresholds: Optional[Dict[str, float]] = None):
        self.allocations: Dict[str, ResourceAllocation] = {}
        self.usages: List[ResourceUsage] = []
        self.assessments: List[WasteGovernance] = []
        
        # Waste thresholds by resource type (percentage)
        self.waste_thresholds = waste_thresholds or {
            ResourceType.COMPUTE: 0.15,  # 15% waste threshold
            ResourceType.MEMORY: 0.20,   # 20% waste threshold
            ResourceType.STORAGE: 0.10,  # 10% waste threshold
            ResourceType.NETWORK: 0.25,  # 25% waste threshold
            ResourceType.API_CALLS: 0.05, # 5% waste threshold
            ResourceType.HUMAN_TIME: 0.10, # 10% waste threshold
        }

    def allocate_resource(
        self,
        resource_type: ResourceType,
        phase: str,
        amount_requested: float,
        unit: str,
        priority: int = 5,
    ) -> ResourceAllocation:
        """
        Allocate resources for a phase.

        Args:
            resource_type: Type of resource
            phase: Phase requesting resources
            amount_requested: Amount requested
            unit: Unit of measurement
            priority: Priority level (1-10)

        Returns:
            ResourceAllocation: The allocation record
        """
        allocation_id = f"ALLOC_{resource_type}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Apply optimization logic
        amount_allocated = self._optimize_allocation(
            resource_type, amount_requested, priority
        )
        
        allocation = ResourceAllocation(
            allocation_id=allocation_id,
            resource_type=resource_type,
            phase=phase,
            amount_requested=amount_requested,
            amount_allocated=amount_allocated,
            unit=unit,
            priority=priority,
        )
        
        self.allocations[allocation_id] = allocation
        return allocation

    def _optimize_allocation(
        self,
        resource_type: ResourceType,
        amount_requested: float,
        priority: int,
    ) -> float:
        """
        Optimize resource allocation based on priority and availability.

        Args:
            resource_type: Type of resource
            amount_requested: Amount requested
            priority: Priority level

        Returns:
            float: Optimized allocation amount
        """
        # Simple optimization: adjust based on priority
        # High priority (8-10) gets full allocation
        # Medium priority (4-7) gets 80-95% allocation
        # Low priority (1-3) gets 60-80% allocation
        
        if priority >= 8:
            return amount_requested
        elif priority >= 4:
            factor = 0.80 + (priority - 4) * 0.05
            return amount_requested * factor
        else:
            factor = 0.60 + priority * 0.067
            return amount_requested * factor

    def record_usage(
        self,
        allocation_id: str,
        amount_used: float,
    ) -> ResourceUsage:
        """
        Record resource usage.

        Args:
            allocation_id: ID of the allocation
            amount_used: Amount actually used

        Returns:
            ResourceUsage: The usage record
        """
        if allocation_id not in self.allocations:
            raise ValueError(f"Allocation {allocation_id} not found")
        
        allocation = self.allocations[allocation_id]
        usage_id = f"USAGE_{allocation_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Calculate waste
        amount_wasted = max(0, allocation.amount_allocated - amount_used)
        
        # Calculate efficiency
        efficiency = (
            amount_used / allocation.amount_allocated
            if allocation.amount_allocated > 0
            else 1.0
        )
        
        usage = ResourceUsage(
            usage_id=usage_id,
            allocation_id=allocation_id,
            resource_type=allocation.resource_type,
            phase=allocation.phase,
            amount_used=amount_used,
            amount_wasted=amount_wasted,
            unit=allocation.unit,
            efficiency=efficiency,
        )
        
        self.usages.append(usage)
        return usage

    def assess_waste_governance(
        self,
        time_period: str = "current",
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
    ) -> WasteGovernance:
        """
        Assess waste governance compliance.

        Args:
            time_period: Description of time period
            start_time: Start of assessment period
            end_time: End of assessment period

        Returns:
            WasteGovernance: Waste governance assessment
        """
        assessment_id = f"WASTE_ASSESS_{datetime.utcnow().strftime('%Y%m%d_%H%M%S_%f')}"
        
        # Filter usages by time period if specified
        usages = self.usages
        if start_time or end_time:
            usages = [
                u for u in usages
                if self._in_time_range(u.timestamp, start_time, end_time)
            ]
        
        # Calculate total waste by resource type
        total_waste: Dict[str, float] = {}
        total_allocated: Dict[str, float] = {}
        
        for usage in usages:
            rt = usage.resource_type.value
            total_waste[rt] = total_waste.get(rt, 0.0) + usage.amount_wasted
            
            # Get allocation amount
            if usage.allocation_id in self.allocations:
                alloc = self.allocations[usage.allocation_id]
                total_allocated[rt] = total_allocated.get(rt, 0.0) + alloc.amount_allocated
        
        # Check for threshold breaches
        breaches = []
        for resource_type, threshold in self.waste_thresholds.items():
            rt = resource_type.value
            if rt in total_waste and rt in total_allocated:
                waste_percentage = (
                    total_waste[rt] / total_allocated[rt]
                    if total_allocated[rt] > 0
                    else 0.0
                )
                if waste_percentage > threshold:
                    breaches.append(
                        f"{rt}: {waste_percentage:.2%} waste exceeds threshold of {threshold:.2%}"
                    )
        
        # Generate recommendations
        recommendations = []
        if breaches:
            recommendations.append("Reduce resource over-allocation in high-waste categories")
            recommendations.append("Review phase requirements and adjust allocation policies")
        
        if total_waste:
            avg_efficiency = sum(u.efficiency for u in usages) / len(usages) if usages else 1.0
            if avg_efficiency < 0.8:
                recommendations.append(
                    f"Overall efficiency is {avg_efficiency:.2%}, consider optimization"
                )
        
        # Determine compliance status
        compliance_status = "COMPLIANT" if not breaches else "NON_COMPLIANT"
        
        assessment = WasteGovernance(
            assessment_id=assessment_id,
            time_period=time_period,
            total_waste=total_waste,
            waste_threshold_breaches=breaches,
            recommendations=recommendations,
            compliance_status=compliance_status,
        )
        
        self.assessments.append(assessment)
        return assessment

    def _in_time_range(
        self,
        timestamp: str,
        start_time: Optional[datetime],
        end_time: Optional[datetime],
    ) -> bool:
        """Check if timestamp is within time range"""
        dt = datetime.fromisoformat(timestamp)
        if start_time and dt < start_time:
            return False
        if end_time and dt > end_time:
            return False
        return True

    def get_utilization_stats(
        self,
        resource_type: Optional[ResourceType] = None,
        phase: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Get resource utilization statistics.

        Args:
            resource_type: Filter by resource type
            phase: Filter by phase

        Returns:
            Dict with utilization statistics
        """
        usages = self.usages
        
        if resource_type:
            usages = [u for u in usages if u.resource_type == resource_type]
        
        if phase:
            usages = [u for u in usages if u.phase == phase]
        
        if not usages:
            return {
                "count": 0,
                "average_efficiency": 1.0,
                "total_waste": 0.0,
                "total_used": 0.0,
            }
        
        return {
            "count": len(usages),
            "average_efficiency": sum(u.efficiency for u in usages) / len(usages),
            "total_waste": sum(u.amount_wasted for u in usages),
            "total_used": sum(u.amount_used for u in usages),
            "by_resource_type": self._group_by_resource_type(usages),
        }

    def _group_by_resource_type(self, usages: List[ResourceUsage]) -> Dict[str, Any]:
        """Group usage statistics by resource type"""
        grouped: Dict[str, List[ResourceUsage]] = {}
        
        for usage in usages:
            rt = usage.resource_type.value
            if rt not in grouped:
                grouped[rt] = []
            grouped[rt].append(usage)
        
        stats = {}
        for rt, rt_usages in grouped.items():
            stats[rt] = {
                "count": len(rt_usages),
                "average_efficiency": sum(u.efficiency for u in rt_usages) / len(rt_usages),
                "total_waste": sum(u.amount_wasted for u in rt_usages),
                "total_used": sum(u.amount_used for u in rt_usages),
            }
        
        return stats

    def get_waste_report(self) -> Dict[str, Any]:
        """
        Get comprehensive waste report.

        Returns:
            Dict with waste governance report
        """
        latest_assessment = self.assessments[-1] if self.assessments else None
        
        return {
            "total_assessments": len(self.assessments),
            "latest_assessment": latest_assessment.model_dump() if latest_assessment else None,
            "historical_compliance": [
                a.compliance_status for a in self.assessments
            ],
            "utilization_stats": self.get_utilization_stats(),
        }
