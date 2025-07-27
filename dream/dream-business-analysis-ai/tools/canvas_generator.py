"""
DREAM Business Analysis AI - Business Canvas Generator
Business model canvas generation and analysis tools
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class CanvasType(Enum):
    """Business canvas types"""
    BUSINESS_MODEL = "business_model"
    LEAN = "lean"
    VALUE_PROPOSITION = "value_proposition"
    DREAM_FRAMEWORK = "dream_framework"

@dataclass
class CanvasElement:
    """Canvas element structure"""
    name: str
    content: List[str] = field(default_factory=list)
    description: str = ""
    importance: int = 5  # 1-10 scale
    confidence: float = 0.8  # 0-1 scale
    
@dataclass
class BusinessCanvas:
    """Business canvas structure"""
    name: str
    canvas_type: CanvasType
    description: str = ""
    elements: Dict[str, CanvasElement] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    business_case_id: str = ""

class CanvasGenerator:
    """Business canvas generator and manager"""
    
    def __init__(self):
        self.canvases: Dict[str, BusinessCanvas] = {}
        self.canvas_templates = self._initialize_templates()
    
    def _initialize_templates(self) -> Dict[CanvasType, Dict[str, str]]:
        """Initialize canvas templates"""
        return {
            CanvasType.BUSINESS_MODEL: {
                "key_partners": "关键合作伙伴 - 谁是我们的关键合作伙伴？谁是我们的关键供应商？",
                "key_activities": "关键业务 - 我们的价值主张需要哪些关键业务？",
                "key_resources": "核心资源 - 我们的价值主张需要哪些核心资源？",
                "value_propositions": "价值主张 - 我们向客户传递什么价值？",
                "customer_relationships": "客户关系 - 我们与客户建立什么类型的关系？",
                "channels": "渠道通路 - 通过哪些渠道接触客户？",
                "customer_segments": "客户细分 - 我们为谁创造价值？",
                "cost_structure": "成本结构 - 商业模式中的主要成本是什么？",
                "revenue_streams": "收入来源 - 客户愿意为什么付费？"
            },
            CanvasType.LEAN: {
                "problem": "问题 - 需要解决的前3个问题",
                "solution": "解决方案 - 针对问题的前3个功能",
                "key_metrics": "关键指标 - 衡量成功的关键指标",
                "unique_value_proposition": "独特价值主张 - 单一、清晰、引人注目的信息",
                "unfair_advantage": "竞争优势 - 无法轻易复制或购买的优势",
                "channels": "渠道 - 接触客户的路径",
                "customer_segments": "客户细分 - 目标客户群体",
                "cost_structure": "成本结构 - 客户获取成本、分销成本、主机成本等",
                "revenue_streams": "收入流 - 收入模式、生命周期价值、收入、毛利润"
            },
            CanvasType.VALUE_PROPOSITION: {
                "customer_jobs": "客户任务 - 客户试图完成的任务",
                "pain_points": "痛点 - 客户在完成任务时遇到的困难",
                "gain_creators": "收益创造 - 产品如何创造客户收益",
                "pain_relievers": "痛点缓解 - 产品如何缓解客户痛点",
                "products_services": "产品和服务 - 提供的产品和服务清单"
            },
            CanvasType.DREAM_FRAMEWORK: {
                "demand": "需求 (Demand) - 目标用户分析、使用场景识别、真实市场需求验证",
                "resolution": "解决方案 (Resolution) - 价值主张设计、产品内核定义、最小可行解决方案",
                "earning": "商业模式 (Earning) - 商业模式可行性、单位经济模型、可持续盈利能力",
                "acquisition": "增长 (Acquisition) - 增长策略、客户获取、规模化机制",
                "moat": "壁垒 (Moat) - 竞争优势、进入壁垒、可防御性分析"
            }
        }
    
    def create_canvas(
        self,
        name: str,
        canvas_type: CanvasType,
        business_case_id: str = "",
        description: str = ""
    ) -> BusinessCanvas:
        """Create a new business canvas"""
        canvas = BusinessCanvas(
            name=name,
            canvas_type=canvas_type,
            description=description,
            business_case_id=business_case_id
        )
        
        # Initialize with template elements
        template = self.canvas_templates.get(canvas_type, {})
        for element_name, element_description in template.items():
            canvas.elements[element_name] = CanvasElement(
                name=element_name,
                description=element_description
            )
        
        self.canvases[name] = canvas
        logger.info(f"Created {canvas_type.value} canvas: {name}")
        return canvas
    
    def add_canvas_content(
        self,
        canvas_name: str,
        element_name: str,
        content: List[str],
        importance: int = 5,
        confidence: float = 0.8
    ) -> bool:
        """Add content to canvas element"""
        if canvas_name not in self.canvases:
            logger.error(f"Canvas not found: {canvas_name}")
            return False
        
        canvas = self.canvases[canvas_name]
        
        if element_name not in canvas.elements:
            # Create new element if it doesn't exist
            canvas.elements[element_name] = CanvasElement(name=element_name)
        
        element = canvas.elements[element_name]
        element.content.extend(content)
        element.importance = importance
        element.confidence = confidence
        
        canvas.updated_at = datetime.now()
        
        logger.info(f"Added content to {canvas_name}.{element_name}")
        return True
    
    def generate_business_model_canvas(
        self,
        business_case: str,
        analysis_data: Optional[Dict[str, Any]] = None
    ) -> BusinessCanvas:
        """Generate business model canvas from business case"""
        canvas_name = f"BMC_{hash(business_case) % 10000}"
        canvas = self.create_canvas(
            name=canvas_name,
            canvas_type=CanvasType.BUSINESS_MODEL,
            description=f"Business Model Canvas for: {business_case[:100]}..."
        )
        
        # If analysis data is provided, populate canvas
        if analysis_data:
            self._populate_bmc_from_analysis(canvas, analysis_data)
        else:
            # Generate basic structure from business case
            self._populate_bmc_from_case(canvas, business_case)
        
        return canvas
    
    def _populate_bmc_from_analysis(self, canvas: BusinessCanvas, analysis_data: Dict[str, Any]):
        """Populate BMC from DREAM analysis data"""
        # Extract information from DREAM analysis
        if "demand" in analysis_data:
            demand_data = analysis_data["demand"]
            # Customer segments from demand analysis
            self.add_canvas_content(
                canvas.name,
                "customer_segments",
                ["基于需求分析的目标客户群体", "早期采用者", "主要用户群体"]
            )
        
        if "resolution" in analysis_data:
            resolution_data = analysis_data["resolution"]
            # Value propositions from resolution analysis
            self.add_canvas_content(
                canvas.name,
                "value_propositions",
                ["核心价值主张", "差异化优势", "用户价值创造"]
            )
        
        if "earning" in analysis_data:
            earning_data = analysis_data["earning"]
            # Revenue streams and cost structure
            self.add_canvas_content(
                canvas.name,
                "revenue_streams",
                ["主要收入来源", "定价模式", "收入多样化"]
            )
            self.add_canvas_content(
                canvas.name,
                "cost_structure",
                ["固定成本", "变动成本", "关键成本驱动因素"]
            )
        
        if "acquisition" in analysis_data:
            acquisition_data = analysis_data["acquisition"]
            # Channels and customer relationships
            self.add_canvas_content(
                canvas.name,
                "channels",
                ["获客渠道", "分销渠道", "沟通渠道"]
            )
            self.add_canvas_content(
                canvas.name,
                "customer_relationships",
                ["客户关系类型", "客户维护策略", "社区建设"]
            )
        
        if "moat" in analysis_data:
            moat_data = analysis_data["moat"]
            # Key resources, activities, and partners
            self.add_canvas_content(
                canvas.name,
                "key_resources",
                ["核心资源", "独特资产", "关键能力"]
            )
            self.add_canvas_content(
                canvas.name,
                "key_activities",
                ["关键业务活动", "核心流程", "价值创造活动"]
            )
            self.add_canvas_content(
                canvas.name,
                "key_partners",
                ["战略合作伙伴", "供应商", "关键联盟"]
            )
    
    def _populate_bmc_from_case(self, canvas: BusinessCanvas, business_case: str):
        """Populate BMC with basic structure from business case"""
        # This would use NLP or AI to extract basic information
        # For now, provide template structure
        
        self.add_canvas_content(
            canvas.name,
            "customer_segments",
            ["待分析的目标客户群体", "基于商业案例的初步客户定义"]
        )
        
        self.add_canvas_content(
            canvas.name,
            "value_propositions",
            ["待定义的核心价值主张", "基于商业案例的价值假设"]
        )
        
        # Add placeholder content for other elements
        for element_name in canvas.elements:
            if not canvas.elements[element_name].content:
                self.add_canvas_content(
                    canvas.name,
                    element_name,
                    [f"待分析的{element_name}内容"]
                )
    
    def generate_dream_canvas(
        self,
        business_case: str,
        dream_analysis: Dict[str, Any]
    ) -> BusinessCanvas:
        """Generate DREAM framework canvas"""
        canvas_name = f"DREAM_{hash(business_case) % 10000}"
        canvas = self.create_canvas(
            name=canvas_name,
            canvas_type=CanvasType.DREAM_FRAMEWORK,
            description=f"DREAM Framework Canvas for: {business_case[:100]}..."
        )
        
        # Populate with DREAM analysis results
        dream_components = ["demand", "resolution", "earning", "acquisition", "moat"]
        
        for component in dream_components:
            if component in dream_analysis:
                analysis_text = dream_analysis[component]
                # Extract key points from analysis (simplified)
                key_points = self._extract_key_points(analysis_text)
                
                self.add_canvas_content(
                    canvas.name,
                    component,
                    key_points,
                    importance=8,
                    confidence=0.9
                )
        
        return canvas
    
    def _extract_key_points(self, analysis_text: str, max_points: int = 5) -> List[str]:
        """Extract key points from analysis text"""
        # Simplified extraction - in practice, this would use NLP
        lines = analysis_text.split('\n')
        key_points = []
        
        for line in lines:
            line = line.strip()
            if line and (line.startswith('-') or line.startswith('•') or line.startswith('*')):
                key_points.append(line.lstrip('-•* '))
                if len(key_points) >= max_points:
                    break
        
        if not key_points:
            # Fallback: take first few sentences
            sentences = analysis_text.split('。')
            key_points = [s.strip() + '。' for s in sentences[:max_points] if s.strip()]
        
        return key_points[:max_points]
    
    def validate_canvas(self, canvas_name: str) -> Dict[str, Any]:
        """Validate canvas completeness and quality"""
        if canvas_name not in self.canvases:
            return {"error": "Canvas not found"}
        
        canvas = self.canvases[canvas_name]
        validation_results = {
            "canvas_name": canvas_name,
            "canvas_type": canvas.canvas_type.value,
            "completeness_score": 0,
            "quality_score": 0,
            "issues": [],
            "recommendations": []
        }
        
        total_elements = len(canvas.elements)
        completed_elements = 0
        total_quality_score = 0
        
        for element_name, element in canvas.elements.items():
            # Check completeness
            if element.content and any(content.strip() for content in element.content):
                completed_elements += 1
                
                # Check quality
                content_quality = self._assess_content_quality(element)
                total_quality_score += content_quality
                
                if content_quality < 0.5:
                    validation_results["issues"].append(f"{element_name}: 内容质量需要改进")
            else:
                validation_results["issues"].append(f"{element_name}: 缺少内容")
        
        # Calculate scores
        validation_results["completeness_score"] = (completed_elements / total_elements) * 100 if total_elements > 0 else 0
        validation_results["quality_score"] = (total_quality_score / total_elements) * 100 if total_elements > 0 else 0
        
        # Generate recommendations
        if validation_results["completeness_score"] < 80:
            validation_results["recommendations"].append("完善缺失的画布元素内容")
        
        if validation_results["quality_score"] < 70:
            validation_results["recommendations"].append("提高内容质量，增加具体细节")
        
        # Canvas-specific validations
        if canvas.canvas_type == CanvasType.BUSINESS_MODEL:
            validation_results.update(self._validate_bmc_specific(canvas))
        
        return validation_results
    
    def _assess_content_quality(self, element: CanvasElement) -> float:
        """Assess content quality of canvas element"""
        if not element.content:
            return 0.0
        
        quality_score = 0.0
        
        # Check for placeholder content
        placeholder_indicators = ["待分析", "待定义", "待完善", "TBD", "TODO"]
        has_placeholder = any(indicator in content for content in element.content for indicator in placeholder_indicators)
        
        if not has_placeholder:
            quality_score += 0.3
        
        # Check content length and detail
        total_length = sum(len(content) for content in element.content)
        if total_length > 50:
            quality_score += 0.3
        
        # Check number of items
        if len(element.content) >= 2:
            quality_score += 0.2
        
        # Factor in confidence score
        quality_score += element.confidence * 0.2
        
        return min(quality_score, 1.0)
    
    def _validate_bmc_specific(self, canvas: BusinessCanvas) -> Dict[str, Any]:
        """Business Model Canvas specific validation"""
        bmc_validation = {
            "bmc_specific_issues": [],
            "bmc_recommendations": []
        }
        
        # Check value proposition clarity
        vp_element = canvas.elements.get("value_propositions")
        if vp_element and vp_element.content:
            if len(vp_element.content) > 5:
                bmc_validation["bmc_specific_issues"].append("价值主张过于复杂，建议聚焦核心价值")
        
        # Check customer-value alignment
        cs_element = canvas.elements.get("customer_segments")
        if cs_element and vp_element:
            if len(cs_element.content) > 3 and len(vp_element.content) > 3:
                bmc_validation["bmc_recommendations"].append("确保客户细分与价值主张的对应关系")
        
        # Check revenue-cost balance
        revenue_element = canvas.elements.get("revenue_streams")
        cost_element = canvas.elements.get("cost_structure")
        if revenue_element and cost_element:
            if len(cost_element.content) > len(revenue_element.content):
                bmc_validation["bmc_specific_issues"].append("成本结构复杂度高于收入来源，需要优化")
        
        return bmc_validation
    
    def compare_canvases(self, canvas_names: List[str]) -> Dict[str, Any]:
        """Compare multiple canvases"""
        if len(canvas_names) < 2:
            return {"error": "Need at least 2 canvases to compare"}
        
        comparison_results = {
            "canvases": [],
            "common_elements": [],
            "differences": [],
            "recommendations": []
        }
        
        canvas_data = {}
        all_elements = set()
        
        # Collect canvas data
        for name in canvas_names:
            if name in self.canvases:
                canvas = self.canvases[name]
                validation = self.validate_canvas(name)
                
                canvas_info = {
                    "name": name,
                    "type": canvas.canvas_type.value,
                    "completeness": validation["completeness_score"],
                    "quality": validation["quality_score"],
                    "elements": list(canvas.elements.keys())
                }
                
                comparison_results["canvases"].append(canvas_info)
                canvas_data[name] = canvas
                all_elements.update(canvas.elements.keys())
        
        # Find common elements
        if len(canvas_data) > 1:
            common_elements = set(list(canvas_data.values())[0].elements.keys())
            for canvas in canvas_data.values():
                common_elements &= set(canvas.elements.keys())
            comparison_results["common_elements"] = list(common_elements)
        
        # Analyze differences
        for element in all_elements:
            element_analysis = {"element": element, "variations": []}
            
            for name, canvas in canvas_data.items():
                if element in canvas.elements:
                    content_summary = canvas.elements[element].content[:2]  # First 2 items
                    element_analysis["variations"].append({
                        "canvas": name,
                        "content_preview": content_summary
                    })
            
            if len(element_analysis["variations"]) > 1:
                comparison_results["differences"].append(element_analysis)
        
        return comparison_results
    
    def export_canvas(self, canvas_name: str, format: str = "json") -> str:
        """Export canvas in specified format"""
        if canvas_name not in self.canvases:
            return json.dumps({"error": "Canvas not found"})
        
        canvas = self.canvases[canvas_name]
        
        if format == "json":
            export_data = {
                "name": canvas.name,
                "type": canvas.canvas_type.value,
                "description": canvas.description,
                "created_at": canvas.created_at.isoformat(),
                "updated_at": canvas.updated_at.isoformat(),
                "business_case_id": canvas.business_case_id,
                "elements": {}
            }
            
            for element_name, element in canvas.elements.items():
                export_data["elements"][element_name] = {
                    "content": element.content,
                    "description": element.description,
                    "importance": element.importance,
                    "confidence": element.confidence
                }
            
            return json.dumps(export_data, indent=2, ensure_ascii=False)
        
        elif format == "markdown":
            return self._export_canvas_markdown(canvas)
        
        else:
            return json.dumps({"error": "Unsupported format"})
    
    def _export_canvas_markdown(self, canvas: BusinessCanvas) -> str:
        """Export canvas as markdown"""
        md_content = f"# {canvas.name}\n\n"
        md_content += f"**类型**: {canvas.canvas_type.value}\n"
        md_content += f"**描述**: {canvas.description}\n"
        md_content += f"**创建时间**: {canvas.created_at.strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        
        for element_name, element in canvas.elements.items():
            md_content += f"## {element_name}\n\n"
            if element.description:
                md_content += f"*{element.description}*\n\n"
            
            if element.content:
                for item in element.content:
                    md_content += f"- {item}\n"
                md_content += "\n"
            else:
                md_content += "*待完善*\n\n"
        
        return md_content
    
    def generate_canvas_report(self, canvas_name: str) -> Dict[str, Any]:
        """Generate comprehensive canvas report"""
        if canvas_name not in self.canvases:
            return {"error": "Canvas not found"}
        
        canvas = self.canvases[canvas_name]
        validation = self.validate_canvas(canvas_name)
        
        # Element analysis
        element_analysis = []
        for element_name, element in canvas.elements.items():
            element_analysis.append({
                "name": element_name,
                "content_count": len(element.content),
                "importance": element.importance,
                "confidence": element.confidence,
                "quality_score": self._assess_content_quality(element) * 100
            })
        
        # Overall assessment
        overall_score = (validation["completeness_score"] + validation["quality_score"]) / 2
        
        if overall_score >= 80:
            assessment = "优秀 - 画布完整且质量高"
        elif overall_score >= 60:
            assessment = "良好 - 画布基本完整，质量可接受"
        elif overall_score >= 40:
            assessment = "一般 - 画布需要进一步完善"
        else:
            assessment = "需要改进 - 画布完整度和质量都需要提升"
        
        return {
            "canvas_name": canvas_name,
            "canvas_type": canvas.canvas_type.value,
            "description": canvas.description,
            "validation_results": validation,
            "element_analysis": element_analysis,
            "overall_score": overall_score,
            "assessment": assessment,
            "next_steps": self._generate_next_steps(canvas, validation)
        }
    
    def _generate_next_steps(self, canvas: BusinessCanvas, validation: Dict[str, Any]) -> List[str]:
        """Generate next steps for canvas improvement"""
        next_steps = []
        
        if validation["completeness_score"] < 100:
            next_steps.append("完善所有画布元素的内容")
        
        if validation["quality_score"] < 80:
            next_steps.append("提高内容质量，增加具体细节和实例")
        
        # Check for low-confidence elements
        low_confidence_elements = [
            name for name, element in canvas.elements.items()
            if element.confidence < 0.6
        ]
        
        if low_confidence_elements:
            next_steps.append(f"验证和提高以下元素的可信度: {', '.join(low_confidence_elements)}")
        
        if canvas.canvas_type == CanvasType.BUSINESS_MODEL:
            next_steps.append("验证客户细分与价值主张的匹配度")
            next_steps.append("确认收入模式与成本结构的平衡")
        
        if not next_steps:
            next_steps.append("画布质量良好，可以开始实施和验证")
        
        return next_steps

# Global canvas generator instance
canvas_generator = CanvasGenerator()
