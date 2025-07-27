#!/usr/bin/env python3
"""
DREAM Business Analysis AI - Knowledge Base Update Script
Update frameworks, templates, case studies, and benchmarks from class notes using LLM analysis
"""

import asyncio
import sys
import shutil
import json
import re
import yaml
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

from langchain_ollama import OllamaLLM
from langchain_core.prompts import PromptTemplate

class LLMContentGenerator:
    """Generate knowledge base content using LLM analysis of class notes"""
    
    def __init__(self, class_notes_path: Path, config_path: Path):
        self.class_notes_path = class_notes_path
        self.config_path = config_path
        self.llm = None
        self.processed_content = {}
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the Ollama LLM"""
        try:
            # Load configuration
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            
            self.llm = OllamaLLM(
                base_url=config["ollama"]["base_url"],
                model=config["ollama"]["model"],
                temperature=config["ollama"]["temperature"],
                num_predict=config["ollama"]["max_tokens"],
                timeout=config["ollama"]["timeout"]
            )
            print("✅ LLM initialized successfully")
        except Exception as e:
            print(f"❌ Failed to initialize LLM: {e}")
            raise
        
    def load_class_notes(self) -> Dict[str, str]:
        """Load all class notes files"""
        notes = {}
        
        if not self.class_notes_path.exists():
            print(f"⚠️  Class notes directory not found: {self.class_notes_path}")
            return notes
            
        for file_path in self.class_notes_path.glob("*.txt"):
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                    notes[file_path.stem] = content
                    print(f"📖 Loaded: {file_path.name}")
            except Exception as e:
                print(f"❌ Error loading {file_path.name}: {e}")
                
        return notes
    
    async def extract_dream_framework(self, notes: Dict[str, str]) -> str:
        """Extract and structure DREAM framework from class notes using LLM"""
        
        # Combine all relevant notes
        all_notes = "\n\n".join([f"=== {filename} ===\n{content}"
                                for filename, content in notes.items()])
        
        prompt_template = PromptTemplate(
            input_variables=["notes"],
            template="""
基于以下课程笔记内容，请生成一个完整的DREAM商业分析框架详解文档。

课程笔记内容：
{notes}

请按照以下结构生成框架文档：

# DREAM商业分析框架详解

## 框架概述
- 基于课程笔记总结DREAM框架的核心理念和价值
- 说明DREAM五个维度的含义和相互关系

## 第一步：需求分析 (Demand)
- 基于笔记中的需求分析内容，详细阐述需求分析的核心原则、分析要素和验证方法

## 第二步：解决方案分析 (Resolution)
- 基于solution.txt和相关内容，详细说明产品内核定义、价值评估和验证策略

## 第三步：商业模式分析 (Earning)
- 基于商业模式相关内容，说明单位经济学建模、三大核心能力和健康度评估标准

## 第四步：增长分析 (Acquisition)
- 基于AARRR和增长相关内容，说明获客策略和规模化机制

## 第五步：壁垒分析 (Moat)
- 基于竞争优势相关内容，说明护城河构建策略

## 假设驱动方法论
- 基于assumption_driven.txt内容，详细说明关键假设三步法和验证方法分类

## 应用原则
- 总结框架应用的核心原则和注意事项

请确保：
1. 内容完全基于提供的课程笔记
2. 保持中文表达的专业性和准确性
3. 结构清晰，逻辑连贯
4. 包含具体的方法和工具
5. 在文档末尾添加更新时间

生成的内容应该是一个完整的Markdown文档。
"""
        )
        
        formatted_prompt = prompt_template.format(notes=all_notes)
        result = self.llm.invoke(formatted_prompt)
        
        return result
    
    async def extract_hypothesis_methodology(self, notes: Dict[str, str]) -> str:
        """Extract hypothesis-driven methodology from class notes using LLM"""
        
        # Focus on assumption-driven and key assumption breakdown notes
        relevant_notes = {
            'assumption_driven': notes.get('assumption_driven', ''),
            'key_assumption_break_down': notes.get('key_assumption_break_down', ''),
            'business_course_notes_summary': notes.get('business_course_notes_summary', '')
        }
        
        combined_notes = "\n\n".join([f"=== {filename} ===\n{content}"
                                     for filename, content in relevant_notes.items() if content])
        
        prompt_template = PromptTemplate(
            input_variables=["notes"],
            template="""
基于以下课程笔记内容，请生成一个完整的假设驱动商业分析方法论文档。

相关笔记内容：
{notes}

请按照以下结构生成方法论文档：

# 假设驱动商业分析方法论

## 方法论概述
- 基于笔记内容阐述假设驱动分析的核心理念和价值

## 假设识别三步法
### 第一步：加法环节 - 假设拆解
- 基于商业画布九要素进行假设拆解
- 说明价值假设和增长假设的分类

### 第二步：减法环节 - 关键假设筛选
- 基于关键假设ABCD模型进行筛选
- 说明优先级评估标准

### 第三步：验证环节 - 快速学习验证
- 详细说明三种验证方法：靠常识、靠调研、靠实验

## 业务拆解与假设管理
- 基于业务公式ABC模型
- 详细说明十大业务拆解范式
- 假设管理五环节流程

## 转化率优化方法
- 基于笔记中的转化率hill climbing内容

请确保：
1. 完全基于提供的课程笔记内容
2. 保持专业性和实用性
3. 结构清晰，便于理解和应用
4. 包含具体的方法和工具
5. 在文档末尾添加更新时间

生成的内容应该是一个完整的Markdown文档。
"""
        )
        
        formatted_prompt = prompt_template.format(notes=combined_notes)
        result = self.llm.invoke(formatted_prompt)
        
        return result
    
    async def extract_scientific_decision_framework(self, notes: Dict[str, str]) -> str:
        """Extract scientific decision-making framework using LLM"""
        
        scientific_decision = notes.get('scientific_decision', '')
        business_summary = notes.get('business_course_notes_summary', '')
        
        combined_notes = f"""=== scientific_decision ===
{scientific_decision}

=== business_course_notes_summary ===
{business_summary}"""
        
        prompt_template = PromptTemplate(
            input_variables=["notes"],
            template="""
基于以下课程笔记内容，请生成一个完整的科学决策框架文档。

相关笔记内容：
{notes}

请按照以下结构生成科学决策框架文档：

# 科学决策框架

## 决策评估习惯层次
- 基于笔记中的决策成熟度五个层次进行详细说明

## 科学决策三维框架
### 1. 宽度 (Breadth) - 全面考虑
- 关键收益项分析
- 关键成本项分析

### 2. 深度 (Depth) - 分析层次
- 从定性到定量的渐进式分析深化
- 分析层次递进

### 3. 高度 (Height) - 战略视角
- 四个战略维度的详细说明

## 稀缺机会窗口分析
- 基于笔记中的五类关键窗口期进行详细说明

## 决策评估三维度
- 基于笔记中的核心决策问题和三个关键维度

请确保：
1. 完全基于提供的课程笔记内容
2. 保持专业性和实用性
3. 结构清晰，便于理解和应用
4. 包含具体的决策工具和方法
5. 在文档末尾添加更新时间

生成的内容应该是一个完整的Markdown文档。
"""
        )
        
        formatted_prompt = prompt_template.format(notes=combined_notes)
        result = self.llm.invoke(formatted_prompt)
        
        return result
    
    async def generate_unit_economics_template(self, notes: Dict[str, str]) -> str:
        """Generate enhanced unit economics template using LLM"""
        
        business_summary = notes.get('business_course_notes_summary', '')
        earning_related = notes.get('assumption_driven', '')
        
        combined_notes = f"""=== business_course_notes_summary ===
{business_summary}

=== assumption_driven ===
{earning_related}"""
        
        prompt_template = PromptTemplate(
            input_variables=["notes"],
            template="""
基于以下课程笔记内容，请生成一个完整的单位经济学建模指南文档。

相关笔记内容：
{notes}

请按照以下结构生成单位经济学指南：

# 单位经济学建模完整指南

## 概述
- 基于笔记内容说明单位经济学的重要性和应用价值

## 单位模型定义
- 基于笔记中关于单位模型的内容，说明什么是单位模型
- 单位选择标准和常见单位类型

## 收入模型设计
- 基于商业模式相关内容，详细说明各种收入模式分类
- 每种模式的适用场景和特点

## 成本结构分析
- 基于笔记中的成本分析内容，说明成本分类方法
- 固定成本、变动成本、半变动成本的特点

## 关键指标体系
- 基于笔记中的核心指标内容，详细说明：
  - 核心财务指标（单位收入、成本、贡献边际等）
  - 用户生命周期指标（CAC、LTV、回收期等）

## 健康度评估标准
- 基于行业经验和笔记内容，提供健康度评估标准

## 优化策略框架
- 基于笔记内容，提供收入优化、成本优化、获客效率优化策略

请确保：
1. 完全基于提供的课程笔记内容
2. 保持专业性和实用性
3. 结构清晰，便于理解和应用
4. 包含具体的计算公式和评估标准
5. 在文档末尾添加更新时间

生成的内容应该是一个完整的Markdown文档。
"""
        )
        
        formatted_prompt = prompt_template.format(notes=combined_notes)
        result = self.llm.invoke(formatted_prompt)
        
        return result

class KnowledgeBaseUpdater:
    """Update knowledge base from class notes"""
    
    def __init__(self, project_root: Path):
        self.project_root = project_root
        self.class_notes_path = project_root.parent / "class_notes"
        self.data_path = project_root / "data"
        self.config_path = project_root / "config" / "ollama_config.yaml"
        self.generator = LLMContentGenerator(self.class_notes_path, self.config_path)
        
    async def update_knowledge_base(self):
        """Main function to update knowledge base"""
        print("🔄 Updating DREAM Business Analysis Knowledge Base from Class Notes")
        print("=" * 70)
        
        # Load class notes
        print("\n📚 Loading class notes...")
        notes = self.generator.load_class_notes()
        
        if not notes:
            print("❌ No class notes found. Please check the class_notes directory.")
            return False
            
        print(f"✅ Loaded {len(notes)} class note files")
        
        # Create directories
        self._ensure_directories()
        
        # Generate content from class notes
        print("\n🔄 Generating knowledge base content...")
        
        # Update frameworks
        await self._update_frameworks(notes)
        
        # Update templates
        await self._update_templates(notes)
        
        # Update case studies
        await self._update_case_studies(notes)
        
        # Update benchmarks
        await self._update_benchmarks(notes)
        
        # Rebuild vector database
        print("\n🔄 Rebuilding vector database...")
        success = await self._rebuild_vector_database()
        
        if success:
            print("\n🎉 Knowledge base update completed successfully!")
            print("\n📊 Updated content:")
            self._show_update_summary()
            return True
        else:
            print("\n❌ Vector database rebuild failed")
            return False
    
    def _ensure_directories(self):
        """Ensure all required directories exist"""
        directories = ["frameworks", "templates", "case_studies", "benchmarks"]
        for directory in directories:
            (self.data_path / directory).mkdir(parents=True, exist_ok=True)
    
    async def _update_frameworks(self, notes: Dict[str, str]):
        """Update framework files"""
        print("  📋 Updating frameworks...")
        
        # DREAM Framework
        dream_content = await self.generator.extract_dream_framework(notes)
        dream_path = self.data_path / "frameworks" / "dream_framework_detailed.md"
        with open(dream_path, 'w', encoding='utf-8') as f:
            f.write(dream_content)
        print(f"    ✅ Updated: {dream_path.name}")
        
        # Hypothesis Methodology
        hypothesis_content = await self.generator.extract_hypothesis_methodology(notes)
        hypothesis_path = self.data_path / "frameworks" / "hypothesis_driven_methodology.md"
        with open(hypothesis_path, 'w', encoding='utf-8') as f:
            f.write(hypothesis_content)
        print(f"    ✅ Updated: {hypothesis_path.name}")
        
        # Scientific Decision Framework
        decision_content = await self.generator.extract_scientific_decision_framework(notes)
        decision_path = self.data_path / "frameworks" / "scientific_decision_framework.md"
        with open(decision_path, 'w', encoding='utf-8') as f:
            f.write(decision_content)
        print(f"    ✅ Created: {decision_path.name}")
    
    async def _update_templates(self, notes: Dict[str, str]):
        """Update template files"""
        print("  📝 Updating templates...")
        
        # Unit Economics Template
        unit_economics_content = await self.generator.generate_unit_economics_template(notes)
        unit_economics_path = self.data_path / "templates" / "unit_economics_modeling.md"
        with open(unit_economics_path, 'w', encoding='utf-8') as f:
            f.write(unit_economics_content)
        print(f"    ✅ Updated: {unit_economics_path.name}")
        
        # Business Canvas Template
        canvas_content = await self._generate_business_canvas_template(notes)
        canvas_path = self.data_path / "templates" / "business_canvas_template.md"
        with open(canvas_path, 'w', encoding='utf-8') as f:
            f.write(canvas_content)
        print(f"    ✅ Created: {canvas_path.name}")
        
        # Hypothesis Testing Template
        hypothesis_template = await self._generate_hypothesis_testing_template(notes)
        hypothesis_path = self.data_path / "templates" / "hypothesis_testing_template.md"
        with open(hypothesis_path, 'w', encoding='utf-8') as f:
            f.write(hypothesis_template)
        print(f"    ✅ Created: {hypothesis_path.name}")
    
    async def _update_case_studies(self, notes: Dict[str, str]):
        """Update case study files"""
        print("  📖 Updating case studies...")
        
        # Generate example case studies based on frameworks
        case_study = await self._generate_example_case_study(notes)
        case_path = self.data_path / "case_studies" / "saas_platform_analysis.json"
        with open(case_path, 'w', encoding='utf-8') as f:
            json.dump(case_study, f, ensure_ascii=False, indent=2)
        print(f"    ✅ Created: {case_path.name}")
    
    async def _update_benchmarks(self, notes: Dict[str, str]):
        """Update benchmark files"""
        print("  📊 Updating benchmarks...")
        
        # Industry benchmarks
        benchmarks = await self._generate_industry_benchmarks(notes)
        benchmark_path = self.data_path / "benchmarks" / "industry_benchmarks.md"
        with open(benchmark_path, 'w', encoding='utf-8') as f:
            f.write(benchmarks)
        print(f"    ✅ Created: {benchmark_path.name}")
    
    async def _generate_business_canvas_template(self, notes: Dict[str, str]) -> str:
        """Generate business canvas template using LLM"""
        
        relevant_notes = {
            'assumption_driven': notes.get('assumption_driven', ''),
            'business_course_notes_summary': notes.get('business_course_notes_summary', ''),
            'key_assumption_break_down': notes.get('key_assumption_break_down', '')
        }
        
        combined_notes = "\n\n".join([f"=== {filename} ===\n{content}"
                                     for filename, content in relevant_notes.items() if content])
        
        prompt_template = PromptTemplate(
            input_variables=["notes"],
            template="""
基于以下课程笔记内容，请生成一个完整的商业画布分析模板。

相关笔记内容：
{notes}

请按照以下结构生成商业画布模板：

# 商业画布分析模板

## 商业画布九要素
基于DREAM框架和假设驱动方法论，详细说明商业画布的九个核心要素：

### 1. 需求分析
- 基于笔记中的需求分析内容，设计细分用户、需求、核心卖点的分析框架

### 2. 解决方案
- 基于solution.txt内容，设计产品内核和解决方案分析框架

### 3. 商业模式
- 基于商业模式相关内容，设计收入、成本、核心指标的分析框架

### 4. 获客渠道
- 基于AARRR和获客相关内容，设计获客渠道分析框架

### 5. 壁垒
- 基于竞争优势相关内容，设计壁垒分析框架

## 关键假设识别
- 基于假设驱动方法论，设计价值假设和增长假设的识别框架

## 验证计划
- 基于三种验证方法（常识、调研、实验），设计验证计划模板

请确保：
1. 完全基于提供的课程笔记内容
2. 保持模板的实用性和可操作性
3. 结构清晰，便于填写和使用
4. 包含具体的分析要点和指导
5. 在文档末尾添加更新时间

生成的内容应该是一个完整的Markdown模板文档。
"""
        )
        
        formatted_prompt = prompt_template.format(notes=combined_notes)
        result = self.generator.llm.invoke(formatted_prompt)
        
        return result
    
    async def _generate_hypothesis_testing_template(self, notes: Dict[str, str]) -> str:
        """Generate hypothesis testing template using LLM"""
        
        relevant_notes = {
            'assumption_driven': notes.get('assumption_driven', ''),
            'key_assumption_break_down': notes.get('key_assumption_break_down', ''),
            'scientific_decision': notes.get('scientific_decision', '')
        }
        
        combined_notes = "\n\n".join([f"=== {filename} ===\n{content}"
                                     for filename, content in relevant_notes.items() if content])
        
        prompt_template = PromptTemplate(
            input_variables=["notes"],
            template="""
基于以下课程笔记内容，请生成一个完整的假设测试模板。

相关笔记内容：
{notes}

请按照以下结构生成假设测试模板：

# 假设测试模板

## 假设基本信息
- 设计假设的基本信息记录框架

## 假设描述
- 基于笔记内容，设计假设陈述和背景描述框架

## 优先级评估
- 基于关键假设ABCD模型和科学决策框架，设计优先级评估框架
- 包含影响评估、可行性评估、时间窗口等维度

## 验证方案设计
- 基于三种验证方法（常识、调研、实验），设计验证方案框架
- 包含验证目标、方法、资源需求等

## 验证执行
- 设计执行计划和风险控制框架

## 验证结果
- 设计结果收集、分析和结论框架

## 学习总结
- 设计经验教训和知识沉淀框架

请确保：
1. 完全基于提供的课程笔记内容
2. 保持模板的实用性和可操作性
3. 结构清晰，便于填写和使用
4. 包含具体的评估标准和指导
5. 在文档末尾添加更新时间

生成的内容应该是一个完整的Markdown模板文档。
"""
        )
        
        formatted_prompt = prompt_template.format(notes=combined_notes)
        result = self.generator.llm.invoke(formatted_prompt)
        
        return result
    
    async def _generate_example_case_study(self, notes: Dict[str, str]) -> Dict[str, Any]:
        """Generate example case study using LLM"""
        
        all_notes = "\n\n".join([f"=== {filename} ===\n{content}"
                                for filename, content in notes.items()])
        
        prompt_template = PromptTemplate(
            input_variables=["notes"],
            template="""
基于以下课程笔记内容，请生成一个完整的商业分析案例研究，以JSON格式输出。

课程笔记内容：
{notes}

请按照以下JSON结构生成案例研究：

{{
  "case_id": "案例唯一标识",
  "title": "案例标题",
  "industry": "行业分类",
  "business_model": "商业模式类型",
  "analysis_date": "分析日期",
  "dream_analysis": {{
    "demand": {{
      "target_users": "目标用户群体",
      "use_cases": ["使用场景1", "使用场景2"],
      "market_size": {{
        "tam": "总体可获得市场",
        "sam": "可服务市场",
        "som": "可获得份额"
      }},
      "pain_points": ["痛点1", "痛点2"]
    }},
    "resolution": {{
      "product_core": "产品内核定义",
      "value_proposition": "价值主张",
      "mvp_features": ["核心功能1", "核心功能2"],
      "user_value_formula": "用户价值计算公式"
    }},
    "earning": {{
      "revenue_model": "收入模式",
      "pricing": "定价策略",
      "unit_economics": {{
        "arpu": "平均用户收入",
        "cac": "客户获取成本",
        "ltv": "客户生命周期价值",
        "ltv_cac_ratio": "LTV/CAC比率",
        "payback_period": "回收期"
      }},
      "cost_structure": {{
        "fixed_costs": ["固定成本项"],
        "variable_costs": ["变动成本项"]
      }}
    }},
    "acquisition": {{
      "channels": ["获客渠道"],
      "aarrr": {{
        "acquisition": "获客数据",
        "activation": "激活率",
        "retention": "留存率",
        "revenue": "收入转化",
        "referral": "推荐率"
      }}
    }},
    "moat": {{
      "competitive_advantages": ["竞争优势"],
      "barriers": ["进入壁垒"],
      "sustainability": "可持续性描述"
    }}
  }},
  "key_hypotheses": [
    {{
      "type": "假设类型",
      "description": "假设描述",
      "validation_method": "验证方法",
      "result": "验证结果"
    }}
  ],
  "lessons_learned": [
    "经验教训1",
    "经验教训2"
  ]
}}

请确保：
1. 完全基于提供的课程笔记内容
2. 案例具有现实性和可信度
3. 数据合理且符合行业常识
4. 体现DREAM框架的完整应用
5. 包含假设驱动的验证过程

只返回JSON格式的内容，不要包含其他说明文字。
"""
        )
        
        formatted_prompt = prompt_template.format(notes=all_notes)
        result = self.generator.llm.invoke(formatted_prompt)
        
        # Parse the JSON result
        try:
            import json
            case_study = json.loads(result)
            return case_study
        except json.JSONDecodeError:
            # Fallback to a basic structure if JSON parsing fails
            return {
                "case_id": "llm_generated_001",
                "title": "LLM生成的商业分析案例",
                "industry": "基于课程笔记生成",
                "business_model": "动态生成",
                "analysis_date": datetime.now().strftime('%Y-%m-%d'),
                "dream_analysis": {"note": "LLM生成的分析内容"},
                "key_hypotheses": [],
                "lessons_learned": ["基于课程笔记的LLM分析"]
            }
    
    async def _generate_industry_benchmarks(self, notes: Dict[str, str]) -> str:
        """Generate industry benchmarks using LLM"""
        
        business_summary = notes.get('business_course_notes_summary', '')
        assumption_driven = notes.get('assumption_driven', '')
        
        combined_notes = f"""=== business_course_notes_summary ===
{business_summary}

=== assumption_driven ===
{assumption_driven}"""
        
        prompt_template = PromptTemplate(
            input_variables=["notes"],
            template="""
基于以下课程笔记内容，请生成一个完整的行业基准数据文档。

相关笔记内容：
{notes}

请按照以下结构生成行业基准数据：

# 行业基准数据

## 核心商业指标基准
- 基于笔记中的单位经济学和商业模式内容，提供关键商业指标的行业基准

## SaaS行业基准
- 基于笔记内容和行业常识，提供SaaS行业的关键指标基准
- 包含LTV/CAC、留存率、转化率等核心指标

## 电商行业基准
- 提供电商行业的关键指标基准
- 包含复购率、转化率、客单价等指标

## 平台业务基准
- 提供平台业务的关键指标基准
- 包含网络效应、双边市场、用户活跃度等指标

## 移动应用基准
- 提供移动应用的关键指标基准
- 包含下载转化、留存率、变现指标等

## 其他重要行业基准
- 根据笔记内容，补充其他相关行业的基准数据

## 基准数据应用指导
- 基于笔记中的基准分析方法，说明如何正确使用基准数据进行商业分析

请确保：
1. 基于提供的课程笔记内容和行业常识
2. 数据具有参考价值和现实意义
3. 结构清晰，便于查阅和使用
4. 包含具体的数值范围和评估标准
5. 在文档末尾添加更新时间和数据来源说明

生成的内容应该是一个完整的Markdown文档。
"""
        )
        
        formatted_prompt = prompt_template.format(notes=combined_notes)
        result = self.generator.llm.invoke(formatted_prompt)
        
        return result
    
    async def _rebuild_vector_database(self):
        """Rebuild vector database"""
        try:
            # Try to use the existing rebuild script
            import subprocess
            result = subprocess.run([
                sys.executable, "rebuild_vectordb_only.py"
            ], cwd=self.project_root, capture_output=True, text=True)
            
            if result.returncode == 0:
                print("✅ Vector database rebuilt successfully")
                return True
            else:
                print(f"❌ Vector database rebuild failed: {result.stderr}")
                print("💡 You can manually run: python rebuild_vectordb.py")
                return False
                
        except Exception as e:
            print(f"❌ Error rebuilding vector database: {e}")
            print("💡 You can manually run: python rebuild_vectordb.py")
            return False
    
    def _show_update_summary(self):
        """Show summary of updated content"""
        frameworks_count = len(list((self.data_path / "frameworks").glob("*.md")))
        templates_count = len(list((self.data_path / "templates").glob("*.md")))
        case_studies_count = len(list((self.data_path / "case_studies").glob("*.json")))
        benchmarks_count = len(list((self.data_path / "benchmarks").glob("*.md")))
        
        print(f"   📋 Frameworks: {frameworks_count} files")
        print(f"   📝 Templates: {templates_count} files")
        print(f"   📖 Case Studies: {case_studies_count} files")
        print(f"   📊 Benchmarks: {benchmarks_count} files")
        print(f"   📚 Total: {frameworks_count + templates_count + case_studies_count + benchmarks_count} files")

async def main():
    """Main function"""
    project_root = Path(__file__).parent
    updater = KnowledgeBaseUpdater(project_root)
    
    success = await updater.update_knowledge_base()
    
    if success:
        print("\n🚀 Next steps:")
        print("   1. Review updated content in data/ directory")
        print("   2. Test the system: python test_system.py")
        print("   3. Start the application: python start_streamlit.py")
    else:
        print("\n❌ Please fix the errors above and try again")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
