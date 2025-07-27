"""
DREAM Business Analysis AI - Unit Economics Calculator
Unit economics modeling and analysis tools
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
import numpy as np
import pandas as pd

logger = logging.getLogger(__name__)

class RevenueModel(Enum):
    """Revenue model types"""
    ONE_TIME = "one_time"           # 一次性收费
    SUBSCRIPTION = "subscription"   # 订阅模式
    COMMISSION = "commission"       # 佣金模式
    FREEMIUM = "freemium"          # 免费增值
    ADVERTISING = "advertising"     # 广告模式
    MARKETPLACE = "marketplace"     # 市场平台
    USAGE_BASED = "usage_based"    # 按使用量计费

class CostType(Enum):
    """Cost classification"""
    FIXED = "fixed"       # 固定成本
    VARIABLE = "variable" # 变动成本
    SEMI_VARIABLE = "semi_variable" # 半变动成本

@dataclass
class CostItem:
    """Cost item structure"""
    name: str
    amount: float
    cost_type: CostType
    description: str = ""
    category: str = ""  # CAC, COGS, Operations, etc.
    
@dataclass
class RevenueStream:
    """Revenue stream structure"""
    name: str
    amount: float
    model: RevenueModel
    description: str = ""
    frequency: str = "monthly"  # monthly, yearly, per_transaction
    
@dataclass
class UnitEconomicsModel:
    """Unit economics model structure"""
    name: str
    unit_definition: str  # 单位定义，如"每个用户"、"每笔交易"
    revenue_streams: List[RevenueStream] = field(default_factory=list)
    cost_items: List[CostItem] = field(default_factory=list)
    time_period: str = "monthly"  # monthly, yearly
    currency: str = "CNY"
    
    @property
    def total_revenue(self) -> float:
        """Calculate total revenue per unit"""
        return sum(stream.amount for stream in self.revenue_streams)
    
    @property
    def total_costs(self) -> float:
        """Calculate total costs per unit"""
        return sum(cost.amount for cost in self.cost_items)
    
    @property
    def contribution_margin(self) -> float:
        """Calculate contribution margin"""
        return self.total_revenue - self.total_costs
    
    @property
    def contribution_margin_percentage(self) -> float:
        """Calculate contribution margin percentage"""
        if self.total_revenue == 0:
            return 0
        return (self.contribution_margin / self.total_revenue) * 100
    
    @property
    def variable_costs(self) -> float:
        """Calculate total variable costs"""
        return sum(cost.amount for cost in self.cost_items if cost.cost_type == CostType.VARIABLE)
    
    @property
    def fixed_costs(self) -> float:
        """Calculate total fixed costs"""
        return sum(cost.amount for cost in self.cost_items if cost.cost_type == CostType.FIXED)

class UnitEconomicsCalculator:
    """Unit economics calculator and analyzer"""
    
    def __init__(self):
        self.models: Dict[str, UnitEconomicsModel] = {}
    
    def create_model(
        self,
        name: str,
        unit_definition: str,
        time_period: str = "monthly",
        currency: str = "CNY"
    ) -> UnitEconomicsModel:
        """Create a new unit economics model"""
        model = UnitEconomicsModel(
            name=name,
            unit_definition=unit_definition,
            time_period=time_period,
            currency=currency
        )
        
        self.models[name] = model
        logger.info(f"Created unit economics model: {name}")
        return model
    
    def add_revenue_stream(
        self,
        model_name: str,
        stream_name: str,
        amount: float,
        model_type: RevenueModel,
        description: str = "",
        frequency: str = "monthly"
    ) -> bool:
        """Add revenue stream to model"""
        if model_name not in self.models:
            logger.error(f"Model not found: {model_name}")
            return False
        
        revenue_stream = RevenueStream(
            name=stream_name,
            amount=amount,
            model=model_type,
            description=description,
            frequency=frequency
        )
        
        self.models[model_name].revenue_streams.append(revenue_stream)
        logger.info(f"Added revenue stream {stream_name} to model {model_name}")
        return True
    
    def add_cost_item(
        self,
        model_name: str,
        cost_name: str,
        amount: float,
        cost_type: CostType,
        description: str = "",
        category: str = ""
    ) -> bool:
        """Add cost item to model"""
        if model_name not in self.models:
            logger.error(f"Model not found: {model_name}")
            return False
        
        cost_item = CostItem(
            name=cost_name,
            amount=amount,
            cost_type=cost_type,
            description=description,
            category=category
        )
        
        self.models[model_name].cost_items.append(cost_item)
        logger.info(f"Added cost item {cost_name} to model {model_name}")
        return True
    
    def calculate_ltv_cac_ratio(
        self,
        model_name: str,
        customer_lifetime_months: int,
        churn_rate: float,
        cac_amount: float
    ) -> Dict[str, Any]:
        """Calculate LTV/CAC ratio"""
        if model_name not in self.models:
            return {"error": "Model not found"}
        
        model = self.models[model_name]
        
        # Calculate LTV using contribution margin
        monthly_contribution = model.contribution_margin
        
        # Method 1: Using customer lifetime
        ltv_method1 = monthly_contribution * customer_lifetime_months
        
        # Method 2: Using churn rate
        if churn_rate > 0:
            ltv_method2 = monthly_contribution / churn_rate
        else:
            ltv_method2 = float('inf')
        
        # Calculate ratios
        ltv_cac_ratio1 = ltv_method1 / cac_amount if cac_amount > 0 else float('inf')
        ltv_cac_ratio2 = ltv_method2 / cac_amount if cac_amount > 0 else float('inf')
        
        # Payback period (months to recover CAC)
        payback_period = cac_amount / monthly_contribution if monthly_contribution > 0 else float('inf')
        
        return {
            "ltv_method1": ltv_method1,
            "ltv_method2": ltv_method2,
            "cac": cac_amount,
            "ltv_cac_ratio1": ltv_cac_ratio1,
            "ltv_cac_ratio2": ltv_cac_ratio2,
            "payback_period_months": payback_period,
            "monthly_contribution": monthly_contribution,
            "assessment": self._assess_ltv_cac_ratio(ltv_cac_ratio1)
        }
    
    def _assess_ltv_cac_ratio(self, ratio: float) -> str:
        """Assess LTV/CAC ratio health"""
        if ratio >= 3:
            return "健康 - LTV/CAC比率良好，业务可持续"
        elif ratio >= 2:
            return "一般 - LTV/CAC比率可接受，但有改进空间"
        elif ratio >= 1:
            return "警告 - LTV/CAC比率偏低，需要优化"
        else:
            return "危险 - LTV/CAC比率过低，商业模式不可持续"
    
    def calculate_break_even_analysis(
        self,
        model_name: str,
        fixed_costs_total: float,
        target_units: int = None
    ) -> Dict[str, Any]:
        """Calculate break-even analysis"""
        if model_name not in self.models:
            return {"error": "Model not found"}
        
        model = self.models[model_name]
        
        # Break-even units
        if model.contribution_margin > 0:
            break_even_units = fixed_costs_total / model.contribution_margin
        else:
            break_even_units = float('inf')
        
        # Break-even revenue
        break_even_revenue = break_even_units * model.total_revenue
        
        # If target units provided, calculate margin of safety
        margin_of_safety = None
        margin_of_safety_percentage = None
        if target_units:
            if target_units > break_even_units:
                margin_of_safety = target_units - break_even_units
                margin_of_safety_percentage = (margin_of_safety / target_units) * 100
            else:
                margin_of_safety = 0
                margin_of_safety_percentage = 0
        
        return {
            "break_even_units": break_even_units,
            "break_even_revenue": break_even_revenue,
            "contribution_margin": model.contribution_margin,
            "contribution_margin_percentage": model.contribution_margin_percentage,
            "fixed_costs": fixed_costs_total,
            "target_units": target_units,
            "margin_of_safety": margin_of_safety,
            "margin_of_safety_percentage": margin_of_safety_percentage
        }
    
    def sensitivity_analysis(
        self,
        model_name: str,
        variable_changes: Dict[str, float]  # {"revenue": 0.1, "costs": -0.05}
    ) -> Dict[str, Any]:
        """Perform sensitivity analysis on unit economics"""
        if model_name not in self.models:
            return {"error": "Model not found"}
        
        model = self.models[model_name]
        base_contribution = model.contribution_margin
        
        scenarios = {}
        
        for variable, change_percentage in variable_changes.items():
            if variable == "revenue":
                new_revenue = model.total_revenue * (1 + change_percentage)
                new_contribution = new_revenue - model.total_costs
            elif variable == "costs":
                new_costs = model.total_costs * (1 + change_percentage)
                new_contribution = model.total_revenue - new_costs
            elif variable == "variable_costs":
                new_variable_costs = model.variable_costs * (1 + change_percentage)
                new_total_costs = model.fixed_costs + new_variable_costs
                new_contribution = model.total_revenue - new_total_costs
            else:
                continue
            
            impact = new_contribution - base_contribution
            impact_percentage = (impact / base_contribution) * 100 if base_contribution != 0 else 0
            
            scenarios[variable] = {
                "change_percentage": change_percentage * 100,
                "new_contribution": new_contribution,
                "impact": impact,
                "impact_percentage": impact_percentage
            }
        
        return {
            "base_contribution": base_contribution,
            "scenarios": scenarios,
            "most_sensitive_variable": max(scenarios.keys(), 
                                         key=lambda x: abs(scenarios[x]["impact_percentage"]))
        }
    
    def scenario_modeling(
        self,
        model_name: str,
        scenarios: Dict[str, Dict[str, float]]
    ) -> Dict[str, Any]:
        """Model different business scenarios"""
        if model_name not in self.models:
            return {"error": "Model not found"}
        
        model = self.models[model_name]
        results = {}
        
        for scenario_name, changes in scenarios.items():
            # Apply changes to create scenario model
            scenario_revenue = model.total_revenue
            scenario_costs = model.total_costs
            
            if "revenue_multiplier" in changes:
                scenario_revenue *= changes["revenue_multiplier"]
            if "cost_multiplier" in changes:
                scenario_costs *= changes["cost_multiplier"]
            if "revenue_change" in changes:
                scenario_revenue += changes["revenue_change"]
            if "cost_change" in changes:
                scenario_costs += changes["cost_change"]
            
            scenario_contribution = scenario_revenue - scenario_costs
            scenario_margin_pct = (scenario_contribution / scenario_revenue) * 100 if scenario_revenue > 0 else 0
            
            results[scenario_name] = {
                "revenue": scenario_revenue,
                "costs": scenario_costs,
                "contribution_margin": scenario_contribution,
                "contribution_margin_percentage": scenario_margin_pct,
                "vs_base_change": scenario_contribution - model.contribution_margin
            }
        
        return {
            "base_scenario": {
                "revenue": model.total_revenue,
                "costs": model.total_costs,
                "contribution_margin": model.contribution_margin,
                "contribution_margin_percentage": model.contribution_margin_percentage
            },
            "scenarios": results
        }
    
    def generate_unit_economics_report(self, model_name: str) -> Dict[str, Any]:
        """Generate comprehensive unit economics report"""
        if model_name not in self.models:
            return {"error": "Model not found"}
        
        model = self.models[model_name]
        
        # Revenue breakdown
        revenue_breakdown = []
        for stream in model.revenue_streams:
            revenue_breakdown.append({
                "name": stream.name,
                "amount": stream.amount,
                "model": stream.model.value,
                "percentage": (stream.amount / model.total_revenue) * 100 if model.total_revenue > 0 else 0
            })
        
        # Cost breakdown
        cost_breakdown = []
        cost_by_type = {"fixed": 0, "variable": 0, "semi_variable": 0}
        cost_by_category = {}
        
        for cost in model.cost_items:
            cost_breakdown.append({
                "name": cost.name,
                "amount": cost.amount,
                "type": cost.cost_type.value,
                "category": cost.category,
                "percentage": (cost.amount / model.total_costs) * 100 if model.total_costs > 0 else 0
            })
            
            cost_by_type[cost.cost_type.value] += cost.amount
            
            if cost.category:
                if cost.category not in cost_by_category:
                    cost_by_category[cost.category] = 0
                cost_by_category[cost.category] += cost.amount
        
        # Key metrics
        key_metrics = {
            "total_revenue": model.total_revenue,
            "total_costs": model.total_costs,
            "contribution_margin": model.contribution_margin,
            "contribution_margin_percentage": model.contribution_margin_percentage,
            "variable_costs": model.variable_costs,
            "fixed_costs": model.fixed_costs,
            "variable_cost_ratio": (model.variable_costs / model.total_revenue) * 100 if model.total_revenue > 0 else 0
        }
        
        # Health assessment
        health_score = self._calculate_health_score(model)
        
        return {
            "model_name": model_name,
            "unit_definition": model.unit_definition,
            "time_period": model.time_period,
            "currency": model.currency,
            "key_metrics": key_metrics,
            "revenue_breakdown": revenue_breakdown,
            "cost_breakdown": cost_breakdown,
            "cost_by_type": cost_by_type,
            "cost_by_category": cost_by_category,
            "health_score": health_score,
            "recommendations": self._generate_recommendations(model)
        }
    
    def _calculate_health_score(self, model: UnitEconomicsModel) -> Dict[str, Any]:
        """Calculate unit economics health score"""
        score = 0
        max_score = 100
        
        # Contribution margin health (40 points)
        if model.contribution_margin_percentage >= 70:
            score += 40
        elif model.contribution_margin_percentage >= 50:
            score += 30
        elif model.contribution_margin_percentage >= 30:
            score += 20
        elif model.contribution_margin_percentage >= 10:
            score += 10
        
        # Positive contribution margin (30 points)
        if model.contribution_margin > 0:
            score += 30
        
        # Cost structure balance (30 points)
        if model.total_costs > 0:
            variable_ratio = model.variable_costs / model.total_costs
            if 0.4 <= variable_ratio <= 0.7:  # Balanced cost structure
                score += 30
            elif 0.2 <= variable_ratio <= 0.8:
                score += 20
            else:
                score += 10
        
        # Health assessment
        if score >= 80:
            health_status = "优秀"
            health_description = "单位经济学模型健康，具有良好的盈利能力"
        elif score >= 60:
            health_status = "良好"
            health_description = "单位经济学模型基本健康，有改进空间"
        elif score >= 40:
            health_status = "一般"
            health_description = "单位经济学模型需要优化"
        else:
            health_status = "差"
            health_description = "单位经济学模型存在严重问题，需要重新设计"
        
        return {
            "score": score,
            "max_score": max_score,
            "percentage": (score / max_score) * 100,
            "status": health_status,
            "description": health_description
        }
    
    def _generate_recommendations(self, model: UnitEconomicsModel) -> List[str]:
        """Generate optimization recommendations"""
        recommendations = []
        
        if model.contribution_margin <= 0:
            recommendations.append("贡献边际为负，需要提高收入或降低成本")
        
        if model.contribution_margin_percentage < 30:
            recommendations.append("贡献边际率偏低，建议优化定价策略或成本结构")
        
        if model.variable_costs / model.total_costs > 0.8:
            recommendations.append("变动成本占比过高，考虑通过规模效应降低单位成本")
        
        if model.fixed_costs / model.total_costs > 0.8:
            recommendations.append("固定成本占比过高，需要提高业务量以摊薄固定成本")
        
        if len(model.revenue_streams) == 1:
            recommendations.append("收入来源单一，建议多元化收入流以降低风险")
        
        if not recommendations:
            recommendations.append("单位经济学模型表现良好，继续保持并寻找规模化机会")
        
        return recommendations
    
    def export_model(self, model_name: str) -> str:
        """Export model to JSON"""
        if model_name not in self.models:
            return json.dumps({"error": "Model not found"})
        
        model = self.models[model_name]
        
        export_data = {
            "name": model.name,
            "unit_definition": model.unit_definition,
            "time_period": model.time_period,
            "currency": model.currency,
            "revenue_streams": [
                {
                    "name": stream.name,
                    "amount": stream.amount,
                    "model": stream.model.value,
                    "description": stream.description,
                    "frequency": stream.frequency
                }
                for stream in model.revenue_streams
            ],
            "cost_items": [
                {
                    "name": cost.name,
                    "amount": cost.amount,
                    "cost_type": cost.cost_type.value,
                    "description": cost.description,
                    "category": cost.category
                }
                for cost in model.cost_items
            ]
        }
        
        return json.dumps(export_data, indent=2, ensure_ascii=False)

# Global unit economics calculator instance
unit_economics_calculator = UnitEconomicsCalculator()