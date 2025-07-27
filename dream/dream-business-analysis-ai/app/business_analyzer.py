"""
DREAM Business Analysis AI - Core Business Analyzer
Main engine for DREAM framework business analysis
"""

from typing import Dict, List, Any, Optional
from pathlib import Path
import asyncio
import logging
from langchain_core.prompts import PromptTemplate
from .rag_engine import RAGEngine
from .llm_provider import LLMProvider

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DreamBusinessAnalyzer:
    """Core DREAM framework business analyzer"""
    
    def __init__(self, config: Dict[str, Any], rag_engine: RAGEngine):
        self.config = config
        self.rag_engine = rag_engine
        self.llm_provider = None
        self.business_analyst_prompt = None
        self._initialize_llm()
        self._load_analyst_prompt()
    
    def _initialize_llm(self):
        """Initialize the LLM provider"""
        try:
            self.llm_provider = LLMProvider(self.config)
            provider_info = self.llm_provider.get_provider_info()
            logger.info(f"✅ LLM Provider initialized: {provider_info['provider']} ({provider_info['model']})")
        except Exception as e:
            logger.error(f"❌ Failed to initialize LLM provider: {e}")
            raise
    
    def _load_analyst_prompt(self):
        """Load the business analyst personality prompt"""
        try:
            prompt_path = Path(__file__).parent.parent / "config" / "business_analyst_prompt.txt"
            with open(prompt_path, 'r', encoding='utf-8') as f:
                self.business_analyst_prompt = f.read()
            logger.info("✅ Business analyst prompt loaded")
        except Exception as e:
            logger.error(f"❌ Failed to load analyst prompt: {e}")
            raise
    
    async def analyze_complete_dream(self, business_case: str, context: Optional[str] = None) -> Dict[str, Any]:
        """Complete DREAM framework analysis"""
        try:
            # Get relevant knowledge base context
            kb_context = await self.rag_engine.search_knowledge(business_case, k=5)
            context_text = "\n".join([result["content"] for result in kb_context])
            
            # Create analysis prompt
            prompt_template = PromptTemplate(
                input_variables=["business_case", "context", "analyst_prompt"],
                template="""
{analyst_prompt}

相关知识库内容：
{context}

请对以下商业案例进行完整的DREAM框架分析：

商业案例：{business_case}

请严格按照DREAM五步法进行分析：

## 第一步：需求分析 (Demand)
### 目标用户细分
### 需求验证
### 市场规模评估

## 第二步：解决方案分析 (Resolution)  
### 产品内核定义
### 价值主张评估
### 竞争差异化

## 第三步：商业模式分析 (Earning)
### 单位经济学建模
### 财务可行性分析
### 盈利能力评估

## 第四步：增长分析 (Acquisition)
### 获客策略分析
### AARRR漏斗分析
### 规模化机制

## 第五步：壁垒分析 (Moat)
### 竞争优势识别
### 护城河构建
### 可持续性评估

## 关键假设识别
请识别并列出3-5个最关键的商业假设，并建议验证方法。

## 行动建议
请提供具体的下一步行动建议和成功指标。
"""
            )
            
            # Generate analysis using LLM provider
            formatted_prompt = prompt_template.format(
                business_case=business_case,
                context=context_text,
                analyst_prompt=self.business_analyst_prompt
            )
            result = self.llm_provider.invoke(formatted_prompt)
            
            return {
                "analysis_type": "complete_dream",
                "business_case": business_case,
                "analysis": result,
                "knowledge_sources": len(kb_context),
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"❌ Complete DREAM analysis failed: {e}")
            return {
                "analysis_type": "complete_dream",
                "business_case": business_case,
                "error": str(e),
                "status": "error"
            }
    
    async def analyze_demand(self, business_case: str) -> Dict[str, Any]:
        """Analyze Demand component of DREAM framework"""
        try:
            # Get demand-specific context
            context = await self.rag_engine.get_dream_framework_context("demand")
            
            prompt_template = PromptTemplate(
                input_variables=["business_case", "context", "analyst_prompt"],
                template="""
{analyst_prompt}

相关框架知识：
{context}

请专门针对以下商业案例进行需求分析 (Demand)：

商业案例：{business_case}

请详细分析：

## 目标用户细分
- 早期用户识别和画像
- 细分用户群体定义
- 用户需求层次分析

## 市场规模评估
- TAM (Total Addressable Market) 估算
- SAM (Serviceable Addressable Market) 分析
- SOM (Serviceable Obtainable Market) 预测

## 需求验证
- 问题-解决方案匹配度评估
- 痛点严重程度分析
- 替代方案评估
- 用户真实需求验证方法

## 关键假设
请识别需求分析中的3个关键假设并建议验证方法。
"""
            )
            
            formatted_prompt = prompt_template.format(
                business_case=business_case,
                context=context,
                analyst_prompt=self.business_analyst_prompt
            )
            result = self.llm_provider.invoke(formatted_prompt)
            
            return {
                "analysis_type": "demand",
                "business_case": business_case,
                "analysis": result,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"❌ Demand analysis failed: {e}")
            return {
                "analysis_type": "demand",
                "business_case": business_case,
                "error": str(e),
                "status": "error"
            }
    
    async def analyze_resolution(self, business_case: str) -> Dict[str, Any]:
        """Analyze Resolution component of DREAM framework"""
        try:
            context = await self.rag_engine.get_dream_framework_context("resolution")
            
            prompt_template = PromptTemplate(
                input_variables=["business_case", "context", "analyst_prompt"],
                template="""
{analyst_prompt}

相关框架知识：
{context}

请专门针对以下商业案例进行解决方案分析 (Resolution)：

商业案例：{business_case}

请详细分析：

## 产品内核定义
- 最小可行解决方案识别
- 核心功能优先级矩阵
- 产品开发路线图

## 价值主张设计
- 核心价值主张阐述
- 用户价值计算：(新体验-旧体验) - 替换成本
- 价值传递机制

## 竞争差异化分析
- 竞争对手解决方案对比
- 差异化优势识别
- 产品市场匹配度评估

## 关键假设
请识别解决方案分析中的3个关键假设并建议验证方法。
"""
            )
            
            formatted_prompt = prompt_template.format(
                business_case=business_case,
                context=context,
                analyst_prompt=self.business_analyst_prompt
            )
            result = self.llm_provider.invoke(formatted_prompt)
            
            return {
                "analysis_type": "resolution",
                "business_case": business_case,
                "analysis": result,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"❌ Resolution analysis failed: {e}")
            return {
                "analysis_type": "resolution",
                "business_case": business_case,
                "error": str(e),
                "status": "error"
            }
    
    async def analyze_earning(self, business_case: str) -> Dict[str, Any]:
        """Analyze Earning component of DREAM framework"""
        try:
            context = await self.rag_engine.get_dream_framework_context("earning")
            
            prompt_template = PromptTemplate(
                input_variables=["business_case", "context", "analyst_prompt"],
                template="""
{analyst_prompt}

相关框架知识：
{context}

请专门针对以下商业案例进行商业模式分析 (Earning)：

商业案例：{business_case}

请详细分析：

## 单位经济学建模
- 单位模型定义和选择
- 单位收入计算
- 成本结构分析
- 贡献边际评估

## 商业模式设计
- 收入模式分析
- 定价策略评估
- 商业模式可行性

## 财务可行性分析
- 盈亏平衡分析
- 现金流预测
- 规模化经济学
- 敏感性分析

## 关键假设
请识别商业模式分析中的3个关键假设并建议验证方法。
"""
            )
            
            formatted_prompt = prompt_template.format(
                business_case=business_case,
                context=context,
                analyst_prompt=self.business_analyst_prompt
            )
            result = self.llm_provider.invoke(formatted_prompt)
            
            return {
                "analysis_type": "earning",
                "business_case": business_case,
                "analysis": result,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"❌ Earning analysis failed: {e}")
            return {
                "analysis_type": "earning",
                "business_case": business_case,
                "error": str(e),
                "status": "error"
            }
    
    async def analyze_acquisition(self, business_case: str) -> Dict[str, Any]:
        """Analyze Acquisition component of DREAM framework"""
        try:
            context = await self.rag_engine.get_dream_framework_context("acquisition")
            
            prompt_template = PromptTemplate(
                input_variables=["business_case", "context", "analyst_prompt"],
                template="""
{analyst_prompt}

相关框架知识：
{context}

请专门针对以下商业案例进行增长分析 (Acquisition)：

商业案例：{business_case}

请详细分析：

## 获客策略分析
- 获客渠道识别和评估
- 客户获取成本 (CAC) 分析
- 客户生命周期价值 (LTV) 计算
- LTV/CAC 比率评估

## AARRR漏斗分析
- Acquisition (获取) 策略
- Activation (激活) 机制
- Retention (留存) 策略
- Revenue (收入) 优化
- Referral (推荐) 机制

## 规模化机制
- 增长循环设计
- 病毒式传播机制
- 市场扩张策略
- 增长假设验证

## 关键假设
请识别增长分析中的3个关键假设并建议验证方法。
"""
            )
            
            formatted_prompt = prompt_template.format(
                business_case=business_case,
                context=context,
                analyst_prompt=self.business_analyst_prompt
            )
            result = self.llm_provider.invoke(formatted_prompt)
            
            return {
                "analysis_type": "acquisition",
                "business_case": business_case,
                "analysis": result,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"❌ Acquisition analysis failed: {e}")
            return {
                "analysis_type": "acquisition",
                "business_case": business_case,
                "error": str(e),
                "status": "error"
            }
    
    async def analyze_moat(self, business_case: str) -> Dict[str, Any]:
        """Analyze Moat component of DREAM framework"""
        try:
            context = await self.rag_engine.get_dream_framework_context("moat")
            
            prompt_template = PromptTemplate(
                input_variables=["business_case", "context", "analyst_prompt"],
                template="""
{analyst_prompt}

相关框架知识：
{context}

请专门针对以下商业案例进行壁垒分析 (Moat)：

商业案例：{business_case}

请详细分析：

## 竞争优势识别
- 核心竞争力分析
- 独特资源和能力
- 技术壁垒评估
- 品牌价值分析

## 护城河构建策略
- 网络效应分析
- 规模效应评估
- 转换成本分析
- 数据护城河

## 进入壁垒分析
- 资本要求
- 监管壁垒
- 技术门槛
- 市场准入难度

## 可持续性评估
- 长期竞争优势维护
- 护城河加深策略
- 防御性措施
- 竞争威胁应对

## 关键假设
请识别壁垒分析中的3个关键假设并建议验证方法。
"""
            )
            
            formatted_prompt = prompt_template.format(
                business_case=business_case,
                context=context,
                analyst_prompt=self.business_analyst_prompt
            )
            result = self.llm_provider.invoke(formatted_prompt)
            
            return {
                "analysis_type": "moat",
                "business_case": business_case,
                "analysis": result,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"❌ Moat analysis failed: {e}")
            return {
                "analysis_type": "moat",
                "business_case": business_case,
                "error": str(e),
                "status": "error"
            }
    
    async def generate_hypotheses(self, business_case: str) -> Dict[str, Any]:
        """Generate key business hypotheses for validation"""
        try:
            context = await self.rag_engine.get_hypothesis_validation_context()
            
            prompt_template = PromptTemplate(
                input_variables=["business_case", "context", "analyst_prompt"],
                template="""
{analyst_prompt}

假设验证方法论：
{context}

请为以下商业案例生成关键假设：

商业案例：{business_case}

请按照假设识别三步法进行：

## 第一步：加法环节 - 拆解假设
请列出所有可能的商业假设（至少10个），涵盖：
- 用户需求假设
- 解决方案假设
- 商业模式假设
- 增长假设
- 竞争假设

## 第二步：减法环节 - 筛选关键假设
从上述假设中筛选出5个最关键的假设，评估标准：
- 影响业务关键路径的假设
- 可以大幅提升业务的假设
- 历史验证过的、能力资源够得上的假设

## 第三步：验证环节 - 验证方法设计
为每个关键假设设计验证方法：
1. **靠常识**: 用行业经验和基准回答
2. **靠调研**: 通过对手和专家访谈回答
3. **靠实验**: 设计实验测试，小步快跑，低成本试错

## 假设优先级矩阵
请用影响度和确信度对关键假设进行优先级排序。
"""
            )
            
            formatted_prompt = prompt_template.format(
                business_case=business_case,
                context=context,
                analyst_prompt=self.business_analyst_prompt
            )
            result = self.llm_provider.invoke(formatted_prompt)
            
            return {
                "analysis_type": "hypothesis_generation",
                "business_case": business_case,
                "analysis": result,
                "status": "success"
            }
            
        except Exception as e:
            logger.error(f"❌ Hypothesis generation failed: {e}")
            return {
                "analysis_type": "hypothesis_generation",
                "business_case": business_case,
                "error": str(e),
                "status": "error"
            }