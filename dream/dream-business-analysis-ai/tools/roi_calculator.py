"""
DREAM Business Analysis AI - ROI Calculator
ROI and financial analysis tools for business decisions
"""

from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
import numpy as np
import numpy_financial as npf
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class InvestmentType(Enum):
    """Investment type classification"""
    PRODUCT_DEVELOPMENT = "product_development"
    MARKETING = "marketing"
    INFRASTRUCTURE = "infrastructure"
    HUMAN_RESOURCES = "human_resources"
    RESEARCH = "research"
    EXPANSION = "expansion"
    TECHNOLOGY = "technology"

class CashFlowType(Enum):
    """Cash flow type"""
    INITIAL_INVESTMENT = "initial_investment"
    OPERATING_CASH_FLOW = "operating_cash_flow"
    TERMINAL_VALUE = "terminal_value"

@dataclass
class CashFlow:
    """Cash flow item"""
    period: int  # Period number (0 for initial, 1+ for future periods)
    amount: float
    flow_type: CashFlowType
    description: str = ""
    confidence_level: float = 0.8  # Confidence in this estimate (0-1)

@dataclass
class Investment:
    """Investment analysis structure"""
    name: str
    investment_type: InvestmentType
    description: str = ""
    cash_flows: List[CashFlow] = field(default_factory=list)
    discount_rate: float = 0.1  # 10% default discount rate
    analysis_period_years: int = 5
    currency: str = "CNY"
    created_at: datetime = field(default_factory=datetime.now)
    
    @property
    def initial_investment(self) -> float:
        """Get initial investment amount (negative)"""
        initial_flows = [cf for cf in self.cash_flows if cf.period == 0]
        return sum(cf.amount for cf in initial_flows)
    
    @property
    def total_cash_inflows(self) -> float:
        """Get total positive cash flows"""
        return sum(cf.amount for cf in self.cash_flows if cf.amount > 0)
    
    @property
    def total_cash_outflows(self) -> float:
        """Get total negative cash flows"""
        return sum(cf.amount for cf in self.cash_flows if cf.amount < 0)

class ROICalculator:
    """ROI and financial analysis calculator"""
    
    def __init__(self):
        self.investments: Dict[str, Investment] = {}
    
    def create_investment(
        self,
        name: str,
        investment_type: InvestmentType,
        description: str = "",
        discount_rate: float = 0.1,
        analysis_period_years: int = 5,
        currency: str = "CNY"
    ) -> Investment:
        """Create a new investment for analysis"""
        investment = Investment(
            name=name,
            investment_type=investment_type,
            description=description,
            discount_rate=discount_rate,
            analysis_period_years=analysis_period_years,
            currency=currency
        )
        
        self.investments[name] = investment
        logger.info(f"Created investment analysis: {name}")
        return investment
    
    def add_cash_flow(
        self,
        investment_name: str,
        period: int,
        amount: float,
        flow_type: CashFlowType,
        description: str = "",
        confidence_level: float = 0.8
    ) -> bool:
        """Add cash flow to investment"""
        if investment_name not in self.investments:
            logger.error(f"Investment not found: {investment_name}")
            return False
        
        cash_flow = CashFlow(
            period=period,
            amount=amount,
            flow_type=flow_type,
            description=description,
            confidence_level=confidence_level
        )
        
        self.investments[investment_name].cash_flows.append(cash_flow)
        logger.info(f"Added cash flow to {investment_name}: Period {period}, Amount {amount}")
        return True
    
    def calculate_simple_roi(self, investment_name: str) -> Dict[str, Any]:
        """Calculate simple ROI"""
        if investment_name not in self.investments:
            return {"error": "Investment not found"}
        
        investment = self.investments[investment_name]
        
        total_gains = investment.total_cash_inflows
        total_costs = abs(investment.total_cash_outflows)
        
        if total_costs == 0:
            return {"error": "No investment costs found"}
        
        simple_roi = ((total_gains - total_costs) / total_costs) * 100
        net_profit = total_gains - total_costs
        
        return {
            "investment_name": investment_name,
            "total_investment": total_costs,
            "total_returns": total_gains,
            "net_profit": net_profit,
            "simple_roi_percentage": simple_roi,
            "roi_ratio": total_gains / total_costs if total_costs > 0 else 0
        }
    
    def calculate_npv(self, investment_name: str) -> Dict[str, Any]:
        """Calculate Net Present Value (NPV)"""
        if investment_name not in self.investments:
            return {"error": "Investment not found"}
        
        investment = self.investments[investment_name]
        discount_rate = investment.discount_rate
        
        npv = 0
        cash_flow_details = []
        
        # Sort cash flows by period
        sorted_flows = sorted(investment.cash_flows, key=lambda x: x.period)
        
        for cf in sorted_flows:
            if cf.period == 0:
                # Initial investment (no discounting)
                present_value = cf.amount
            else:
                # Discount future cash flows
                present_value = cf.amount / ((1 + discount_rate) ** cf.period)
            
            npv += present_value
            
            cash_flow_details.append({
                "period": cf.period,
                "cash_flow": cf.amount,
                "present_value": present_value,
                "description": cf.description
            })
        
        return {
            "investment_name": investment_name,
            "npv": npv,
            "discount_rate": discount_rate * 100,
            "cash_flow_details": cash_flow_details,
            "npv_assessment": "正面" if npv > 0 else "负面",
            "recommendation": "建议投资" if npv > 0 else "不建议投资"
        }
    
    def calculate_irr(self, investment_name: str) -> Dict[str, Any]:
        """Calculate Internal Rate of Return (IRR)"""
        if investment_name not in self.investments:
            return {"error": "Investment not found"}
        
        investment = self.investments[investment_name]
        
        # Prepare cash flow array
        max_period = max(cf.period for cf in investment.cash_flows)
        cash_flows = [0] * (max_period + 1)
        
        for cf in investment.cash_flows:
            cash_flows[cf.period] += cf.amount
        
        # Use numpy_financial to calculate IRR
        try:
            irr = npf.irr(cash_flows)
            irr_percentage = irr * 100 if irr is not None else None
            
            # Compare with discount rate
            hurdle_rate = investment.discount_rate * 100
            
            if irr_percentage is not None:
                if irr_percentage > hurdle_rate:
                    assessment = "优秀"
                    recommendation = "强烈建议投资"
                elif irr_percentage > hurdle_rate * 0.8:
                    assessment = "良好"
                    recommendation = "建议投资"
                else:
                    assessment = "不佳"
                    recommendation = "不建议投资"
            else:
                assessment = "无法计算"
                recommendation = "需要更多数据"
            
            return {
                "investment_name": investment_name,
                "irr_percentage": irr_percentage,
                "hurdle_rate_percentage": hurdle_rate,
                "cash_flows": cash_flows,
                "assessment": assessment,
                "recommendation": recommendation
            }
            
        except Exception as e:
            logger.error(f"IRR calculation failed: {e}")
            return {
                "investment_name": investment_name,
                "error": "IRR calculation failed",
                "cash_flows": cash_flows
            }
    
    def _calculate_irr_newton(self, cash_flows: List[float], max_iterations: int = 100) -> Optional[float]:
        """Calculate IRR using Newton-Raphson method"""
        def npv_function(rate):
            return sum(cf / ((1 + rate) ** i) for i, cf in enumerate(cash_flows))
        
        def npv_derivative(rate):
            return sum(-i * cf / ((1 + rate) ** (i + 1)) for i, cf in enumerate(cash_flows))
        
        # Initial guess
        rate = 0.1
        
        for _ in range(max_iterations):
            npv = npv_function(rate)
            if abs(npv) < 1e-6:  # Convergence threshold
                return rate
            
            derivative = npv_derivative(rate)
            if abs(derivative) < 1e-10:  # Avoid division by zero
                break
            
            rate = rate - npv / derivative
            
            # Prevent negative rates
            if rate < -0.99:
                rate = -0.99
        
        return None
    
    def calculate_payback_period(self, investment_name: str) -> Dict[str, Any]:
        """Calculate payback period"""
        if investment_name not in self.investments:
            return {"error": "Investment not found"}
        
        investment = self.investments[investment_name]
        
        # Get initial investment (should be negative)
        initial_investment = abs(investment.initial_investment)
        
        if initial_investment == 0:
            return {"error": "No initial investment found"}
        
        # Calculate cumulative cash flows
        cumulative_flows = []
        cumulative_sum = -initial_investment  # Start with negative initial investment
        
        # Sort cash flows by period (excluding period 0)
        future_flows = sorted([cf for cf in investment.cash_flows if cf.period > 0], 
                            key=lambda x: x.period)
        
        payback_period = None
        
        for cf in future_flows:
            cumulative_sum += cf.amount
            cumulative_flows.append({
                "period": cf.period,
                "cash_flow": cf.amount,
                "cumulative": cumulative_sum
            })
            
            # Check if we've recovered the investment
            if cumulative_sum >= 0 and payback_period is None:
                # Linear interpolation for more precise payback period
                if len(cumulative_flows) > 1:
                    prev_cumulative = cumulative_flows[-2]["cumulative"]
                    current_flow = cf.amount
                    fraction = abs(prev_cumulative) / current_flow
                    payback_period = cf.period - 1 + fraction
                else:
                    payback_period = cf.period
        
        return {
            "investment_name": investment_name,
            "initial_investment": initial_investment,
            "payback_period_years": payback_period,
            "payback_period_months": payback_period * 12 if payback_period else None,
            "cumulative_cash_flows": cumulative_flows,
            "assessment": self._assess_payback_period(payback_period)
        }
    
    def _assess_payback_period(self, payback_period: Optional[float]) -> str:
        """Assess payback period"""
        if payback_period is None:
            return "投资无法在分析期内回收"
        elif payback_period <= 1:
            return "优秀 - 1年内回收投资"
        elif payback_period <= 2:
            return "良好 - 2年内回收投资"
        elif payback_period <= 3:
            return "一般 - 3年内回收投资"
        else:
            return "较差 - 回收期超过3年"
    
    def sensitivity_analysis(
        self,
        investment_name: str,
        sensitivity_ranges: Dict[str, List[float]]  # {"discount_rate": [-0.02, 0.02], "cash_flows": [-0.2, 0.2]}
    ) -> Dict[str, Any]:
        """Perform sensitivity analysis on investment"""
        if investment_name not in self.investments:
            return {"error": "Investment not found"}
        
        investment = self.investments[investment_name]
        base_npv = self.calculate_npv(investment_name)["npv"]
        
        sensitivity_results = {}
        
        for variable, range_values in sensitivity_ranges.items():
            variable_results = []
            
            for change in range_values:
                if variable == "discount_rate":
                    # Temporarily change discount rate
                    original_rate = investment.discount_rate
                    investment.discount_rate = original_rate + change
                    new_npv = self.calculate_npv(investment_name)["npv"]
                    investment.discount_rate = original_rate  # Restore
                    
                elif variable == "cash_flows":
                    # Temporarily adjust all positive cash flows
                    original_flows = []
                    for cf in investment.cash_flows:
                        original_flows.append(cf.amount)
                        if cf.amount > 0:  # Only adjust positive cash flows
                            cf.amount = cf.amount * (1 + change)
                    
                    new_npv = self.calculate_npv(investment_name)["npv"]
                    
                    # Restore original values
                    for i, cf in enumerate(investment.cash_flows):
                        cf.amount = original_flows[i]
                
                else:
                    continue
                
                impact = new_npv - base_npv
                impact_percentage = (impact / abs(base_npv)) * 100 if base_npv != 0 else 0
                
                variable_results.append({
                    "change": change,
                    "new_npv": new_npv,
                    "impact": impact,
                    "impact_percentage": impact_percentage
                })
            
            sensitivity_results[variable] = variable_results
        
        return {
            "investment_name": investment_name,
            "base_npv": base_npv,
            "sensitivity_analysis": sensitivity_results
        }
    
    def compare_investments(self, investment_names: List[str]) -> Dict[str, Any]:
        """Compare multiple investments"""
        if not investment_names:
            return {"error": "No investments provided"}
        
        comparison_results = []
        
        for name in investment_names:
            if name not in self.investments:
                continue
            
            roi_result = self.calculate_simple_roi(name)
            npv_result = self.calculate_npv(name)
            irr_result = self.calculate_irr(name)
            payback_result = self.calculate_payback_period(name)
            
            comparison_results.append({
                "investment_name": name,
                "simple_roi": roi_result.get("simple_roi_percentage", 0),
                "npv": npv_result.get("npv", 0),
                "irr": irr_result.get("irr_percentage", 0),
                "payback_period": payback_result.get("payback_period_years", float('inf')),
                "initial_investment": abs(self.investments[name].initial_investment)
            })
        
        # Rank investments
        if comparison_results:
            # Rank by NPV (primary criterion)
            npv_ranking = sorted(comparison_results, key=lambda x: x["npv"], reverse=True)
            
            # Rank by IRR
            irr_ranking = sorted(comparison_results, key=lambda x: x["irr"] or 0, reverse=True)
            
            # Rank by payback period (shorter is better)
            payback_ranking = sorted(comparison_results, key=lambda x: x["payback_period"])
            
            return {
                "comparison_results": comparison_results,
                "rankings": {
                    "by_npv": [inv["investment_name"] for inv in npv_ranking],
                    "by_irr": [inv["investment_name"] for inv in irr_ranking],
                    "by_payback": [inv["investment_name"] for inv in payback_ranking]
                },
                "recommendation": npv_ranking[0]["investment_name"] if npv_ranking else None
            }
        
        return {"error": "No valid investments found"}
    
    def generate_investment_report(self, investment_name: str) -> Dict[str, Any]:
        """Generate comprehensive investment analysis report"""
        if investment_name not in self.investments:
            return {"error": "Investment not found"}
        
        investment = self.investments[investment_name]
        
        # Calculate all metrics
        simple_roi = self.calculate_simple_roi(investment_name)
        npv_analysis = self.calculate_npv(investment_name)
        irr_analysis = self.calculate_irr(investment_name)
        payback_analysis = self.calculate_payback_period(investment_name)
        
        # Risk assessment
        risk_assessment = self._assess_investment_risk(investment)
        
        # Overall recommendation
        overall_score = self._calculate_investment_score(simple_roi, npv_analysis, irr_analysis, payback_analysis)
        
        return {
            "investment_name": investment_name,
            "investment_type": investment.investment_type.value,
            "description": investment.description,
            "analysis_summary": {
                "simple_roi": simple_roi,
                "npv_analysis": npv_analysis,
                "irr_analysis": irr_analysis,
                "payback_analysis": payback_analysis
            },
            "risk_assessment": risk_assessment,
            "overall_score": overall_score,
            "final_recommendation": self._generate_final_recommendation(overall_score)
        }
    
    def _assess_investment_risk(self, investment: Investment) -> Dict[str, Any]:
        """Assess investment risk level"""
        risk_factors = []
        risk_score = 0  # 0-100, higher is riskier
        
        # Cash flow concentration risk
        positive_flows = [cf for cf in investment.cash_flows if cf.amount > 0]
        if len(positive_flows) <= 2:
            risk_factors.append("现金流来源集中")
            risk_score += 20
        
        # Time concentration risk
        if positive_flows:
            periods = [cf.period for cf in positive_flows]
            if max(periods) - min(periods) <= 1:
                risk_factors.append("收益时间集中")
                risk_score += 15
        
        # Confidence level risk
        avg_confidence = np.mean([cf.confidence_level for cf in investment.cash_flows])
        if avg_confidence < 0.7:
            risk_factors.append("预测置信度较低")
            risk_score += 25
        
        # Investment type risk
        high_risk_types = [InvestmentType.RESEARCH, InvestmentType.PRODUCT_DEVELOPMENT]
        if investment.investment_type in high_risk_types:
            risk_factors.append("投资类型风险较高")
            risk_score += 20
        
        # Determine risk level
        if risk_score >= 60:
            risk_level = "高风险"
        elif risk_score >= 30:
            risk_level = "中等风险"
        else:
            risk_level = "低风险"
        
        return {
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "average_confidence": avg_confidence
        }
    
    def _calculate_investment_score(self, roi, npv, irr, payback) -> Dict[str, Any]:
        """Calculate overall investment score"""
        score = 0
        max_score = 100
        
        # NPV score (40 points)
        if npv.get("npv", 0) > 0:
            score += 40
        elif npv.get("npv", 0) > -1000000:  # Not too negative
            score += 20
        
        # IRR score (30 points)
        irr_pct = irr.get("irr_percentage", 0)
        if irr_pct and irr_pct > 20:
            score += 30
        elif irr_pct and irr_pct > 10:
            score += 20
        elif irr_pct and irr_pct > 0:
            score += 10
        
        # Payback period score (20 points)
        payback_years = payback.get("payback_period_years")
        if payback_years and payback_years <= 2:
            score += 20
        elif payback_years and payback_years <= 3:
            score += 15
        elif payback_years and payback_years <= 5:
            score += 10
        
        # ROI score (10 points)
        roi_pct = roi.get("simple_roi_percentage", 0)
        if roi_pct > 50:
            score += 10
        elif roi_pct > 20:
            score += 7
        elif roi_pct > 0:
            score += 5
        
        return {
            "score": score,
            "max_score": max_score,
            "percentage": (score / max_score) * 100
        }
    
    def _generate_final_recommendation(self, overall_score: Dict[str, Any]) -> str:
        """Generate final investment recommendation"""
        score_pct = overall_score["percentage"]
        
        if score_pct >= 80:
            return "强烈推荐投资 - 各项指标表现优秀"
        elif score_pct >= 60:
            return "推荐投资 - 整体表现良好"
        elif score_pct >= 40:
            return "谨慎考虑 - 存在一定风险，需要进一步分析"
        else:
            return "不推荐投资 - 风险过高或回报不足"

# Global ROI calculator instance
roi_calculator = ROICalculator()
