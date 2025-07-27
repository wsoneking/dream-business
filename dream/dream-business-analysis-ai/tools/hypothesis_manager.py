"""
DREAM Business Analysis AI - Hypothesis Manager
Hypothesis tracking and validation management system
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
import uuid
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)

class HypothesisStatus(Enum):
    """Hypothesis validation status"""
    TO_VALIDATE = "to_validate"
    VALIDATING = "validating"
    VALIDATED = "validated"
    INVALIDATED = "invalidated"
    NEED_ITERATION = "need_iteration"

class ValidationMethod(Enum):
    """Hypothesis validation methods"""
    COMMON_SENSE = "common_sense"  # 靠常识
    RESEARCH = "research"          # 靠调研
    EXPERIMENT = "experiment"      # 靠实验

@dataclass
class Hypothesis:
    """Business hypothesis data structure"""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    description: str = ""
    category: str = ""  # demand, resolution, earning, acquisition, moat
    importance_score: int = 5  # 1-10
    confidence_score: int = 5  # 1-10
    status: HypothesisStatus = HypothesisStatus.TO_VALIDATE
    validation_method: Optional[ValidationMethod] = None
    validation_plan: str = ""
    validation_results: str = ""
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    validated_at: Optional[datetime] = None
    business_case_id: str = ""
    tags: List[str] = field(default_factory=list)
    
    @property
    def priority_score(self) -> float:
        """Calculate priority score based on importance and confidence"""
        return (self.importance_score * 0.7) + (self.confidence_score * 0.3)
    
    @property
    def validation_duration(self) -> Optional[timedelta]:
        """Calculate validation duration if completed"""
        if self.validated_at:
            return self.validated_at - self.created_at
        return None

class HypothesisManager:
    """Hypothesis tracking and management system"""
    
    def __init__(self):
        self.hypotheses: Dict[str, Hypothesis] = {}
        self.business_cases: Dict[str, List[str]] = {}  # business_case_id -> hypothesis_ids
    
    def create_hypothesis(
        self,
        description: str,
        category: str,
        business_case_id: str,
        importance_score: int = 5,
        confidence_score: int = 5,
        tags: Optional[List[str]] = None
    ) -> Hypothesis:
        """Create a new hypothesis"""
        hypothesis = Hypothesis(
            description=description,
            category=category,
            importance_score=importance_score,
            confidence_score=confidence_score,
            business_case_id=business_case_id,
            tags=tags or []
        )
        
        self.hypotheses[hypothesis.id] = hypothesis
        
        # Add to business case tracking
        if business_case_id not in self.business_cases:
            self.business_cases[business_case_id] = []
        self.business_cases[business_case_id].append(hypothesis.id)
        
        logger.info(f"Created hypothesis: {hypothesis.id}")
        return hypothesis
    
    def update_hypothesis_status(
        self,
        hypothesis_id: str,
        status: HypothesisStatus,
        validation_results: Optional[str] = None
    ) -> bool:
        """Update hypothesis validation status"""
        if hypothesis_id not in self.hypotheses:
            logger.error(f"Hypothesis not found: {hypothesis_id}")
            return False
        
        hypothesis = self.hypotheses[hypothesis_id]
        hypothesis.status = status
        hypothesis.updated_at = datetime.now()
        
        if validation_results:
            hypothesis.validation_results = validation_results
        
        if status in [HypothesisStatus.VALIDATED, HypothesisStatus.INVALIDATED]:
            hypothesis.validated_at = datetime.now()
        
        logger.info(f"Updated hypothesis {hypothesis_id} status to {status.value}")
        return True
    
    def set_validation_plan(
        self,
        hypothesis_id: str,
        validation_method: ValidationMethod,
        validation_plan: str
    ) -> bool:
        """Set validation plan for hypothesis"""
        if hypothesis_id not in self.hypotheses:
            logger.error(f"Hypothesis not found: {hypothesis_id}")
            return False
        
        hypothesis = self.hypotheses[hypothesis_id]
        hypothesis.validation_method = validation_method
        hypothesis.validation_plan = validation_plan
        hypothesis.status = HypothesisStatus.VALIDATING
        hypothesis.updated_at = datetime.now()
        
        logger.info(f"Set validation plan for hypothesis: {hypothesis_id}")
        return True
    
    def get_hypotheses_by_business_case(self, business_case_id: str) -> List[Hypothesis]:
        """Get all hypotheses for a business case"""
        if business_case_id not in self.business_cases:
            return []
        
        hypothesis_ids = self.business_cases[business_case_id]
        return [self.hypotheses[hid] for hid in hypothesis_ids if hid in self.hypotheses]
    
    def get_hypotheses_by_status(self, status: HypothesisStatus) -> List[Hypothesis]:
        """Get hypotheses by validation status"""
        return [h for h in self.hypotheses.values() if h.status == status]
    
    def get_hypotheses_by_category(self, category: str) -> List[Hypothesis]:
        """Get hypotheses by DREAM category"""
        return [h for h in self.hypotheses.values() if h.category == category]
    
    def get_priority_hypotheses(self, limit: int = 10) -> List[Hypothesis]:
        """Get top priority hypotheses for validation"""
        all_hypotheses = list(self.hypotheses.values())
        # Filter to only unvalidated hypotheses
        unvalidated = [h for h in all_hypotheses if h.status == HypothesisStatus.TO_VALIDATE]
        # Sort by priority score
        sorted_hypotheses = sorted(unvalidated, key=lambda h: h.priority_score, reverse=True)
        return sorted_hypotheses[:limit]
    
    def get_validation_progress(self, business_case_id: Optional[str] = None) -> Dict[str, Any]:
        """Get validation progress statistics"""
        if business_case_id:
            hypotheses = self.get_hypotheses_by_business_case(business_case_id)
        else:
            hypotheses = list(self.hypotheses.values())
        
        if not hypotheses:
            return {
                "total": 0,
                "to_validate": 0,
                "validating": 0,
                "validated": 0,
                "invalidated": 0,
                "need_iteration": 0,
                "completion_rate": 0.0,
                "average_validation_time": None
            }
        
        status_counts = {}
        for status in HypothesisStatus:
            status_counts[status.value] = len([h for h in hypotheses if h.status == status])
        
        total = len(hypotheses)
        completed = status_counts["validated"] + status_counts["invalidated"]
        completion_rate = (completed / total) * 100 if total > 0 else 0
        
        # Calculate average validation time
        completed_hypotheses = [h for h in hypotheses if h.validation_duration]
        avg_validation_time = None
        if completed_hypotheses:
            total_time = sum([h.validation_duration.total_seconds() for h in completed_hypotheses])
            avg_validation_time = total_time / len(completed_hypotheses) / 3600  # hours
        
        return {
            "total": total,
            "to_validate": status_counts["to_validate"],
            "validating": status_counts["validating"],
            "validated": status_counts["validated"],
            "invalidated": status_counts["invalidated"],
            "need_iteration": status_counts["need_iteration"],
            "completion_rate": completion_rate,
            "average_validation_time": avg_validation_time
        }
    
    def generate_hypothesis_report(self, business_case_id: str) -> Dict[str, Any]:
        """Generate comprehensive hypothesis report"""
        hypotheses = self.get_hypotheses_by_business_case(business_case_id)
        
        if not hypotheses:
            return {"error": "No hypotheses found for business case"}
        
        # Category breakdown
        category_breakdown = {}
        for category in ["demand", "resolution", "earning", "acquisition", "moat"]:
            category_hypotheses = [h for h in hypotheses if h.category == category]
            category_breakdown[category] = {
                "total": len(category_hypotheses),
                "validated": len([h for h in category_hypotheses if h.status == HypothesisStatus.VALIDATED]),
                "invalidated": len([h for h in category_hypotheses if h.status == HypothesisStatus.INVALIDATED]),
                "in_progress": len([h for h in category_hypotheses if h.status == HypothesisStatus.VALIDATING])
            }
        
        # Priority analysis
        high_priority = [h for h in hypotheses if h.priority_score >= 7]
        medium_priority = [h for h in hypotheses if 4 <= h.priority_score < 7]
        low_priority = [h for h in hypotheses if h.priority_score < 4]
        
        # Validation method breakdown
        method_breakdown = {}
        for method in ValidationMethod:
            method_hypotheses = [h for h in hypotheses if h.validation_method == method]
            method_breakdown[method.value] = len(method_hypotheses)
        
        return {
            "business_case_id": business_case_id,
            "total_hypotheses": len(hypotheses),
            "progress": self.get_validation_progress(business_case_id),
            "category_breakdown": category_breakdown,
            "priority_distribution": {
                "high_priority": len(high_priority),
                "medium_priority": len(medium_priority),
                "low_priority": len(low_priority)
            },
            "validation_method_breakdown": method_breakdown,
            "top_priority_hypotheses": [
                {
                    "id": h.id,
                    "description": h.description,
                    "category": h.category,
                    "priority_score": h.priority_score,
                    "status": h.status.value
                }
                for h in sorted(hypotheses, key=lambda x: x.priority_score, reverse=True)[:5]
            ]
        }
    
    def export_hypotheses(self, business_case_id: Optional[str] = None) -> str:
        """Export hypotheses to JSON format"""
        if business_case_id:
            hypotheses = self.get_hypotheses_by_business_case(business_case_id)
        else:
            hypotheses = list(self.hypotheses.values())
        
        export_data = []
        for h in hypotheses:
            export_data.append({
                "id": h.id,
                "description": h.description,
                "category": h.category,
                "importance_score": h.importance_score,
                "confidence_score": h.confidence_score,
                "priority_score": h.priority_score,
                "status": h.status.value,
                "validation_method": h.validation_method.value if h.validation_method else None,
                "validation_plan": h.validation_plan,
                "validation_results": h.validation_results,
                "created_at": h.created_at.isoformat(),
                "updated_at": h.updated_at.isoformat(),
                "validated_at": h.validated_at.isoformat() if h.validated_at else None,
                "business_case_id": h.business_case_id,
                "tags": h.tags
            })
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)
    
    def import_hypotheses(self, json_data: str) -> bool:
        """Import hypotheses from JSON format"""
        try:
            data = json.loads(json_data)
            
            for item in data:
                hypothesis = Hypothesis(
                    id=item["id"],
                    description=item["description"],
                    category=item["category"],
                    importance_score=item["importance_score"],
                    confidence_score=item["confidence_score"],
                    status=HypothesisStatus(item["status"]),
                    validation_method=ValidationMethod(item["validation_method"]) if item["validation_method"] else None,
                    validation_plan=item["validation_plan"],
                    validation_results=item["validation_results"],
                    created_at=datetime.fromisoformat(item["created_at"]),
                    updated_at=datetime.fromisoformat(item["updated_at"]),
                    validated_at=datetime.fromisoformat(item["validated_at"]) if item["validated_at"] else None,
                    business_case_id=item["business_case_id"],
                    tags=item["tags"]
                )
                
                self.hypotheses[hypothesis.id] = hypothesis
                
                # Update business case tracking
                if hypothesis.business_case_id not in self.business_cases:
                    self.business_cases[hypothesis.business_case_id] = []
                if hypothesis.id not in self.business_cases[hypothesis.business_case_id]:
                    self.business_cases[hypothesis.business_case_id].append(hypothesis.id)
            
            logger.info(f"Imported {len(data)} hypotheses")
            return True
            
        except Exception as e:
            logger.error(f"Failed to import hypotheses: {e}")
            return False

# Global hypothesis manager instance
hypothesis_manager = HypothesisManager()