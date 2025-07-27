#!/usr/bin/env python3
"""
DREAM Business Analysis AI - Vector Database Rebuild Script
Rebuild the knowledge base vector database from source files
"""

import asyncio
import sys
import shutil
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

async def rebuild_vector_database():
    """Rebuild the vector database from knowledge base files"""
    print("🔄 Rebuilding DREAM Business Analysis Knowledge Base")
    print("=" * 60)
    
    try:
        from app.rag_engine import RAGEngine
        import yaml
        
        # Load config
        config_path = Path(__file__).parent / "config" / "ollama_config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        print("📋 Configuration loaded:")
        print(f"   Vector DB: {config['vector_db']['type']}")
        print(f"   Collection: {config['vector_db']['collection_name']}")
        print(f"   Embedding Model: {config['embedding']['model']}")
        print(f"   Chunk Size: {config['embedding']['chunk_size']}")
        
        # Clear existing vector database
        vectordb_path = Path(__file__).parent / config['vector_db']['persist_directory']
        if vectordb_path.exists():
            print(f"\n🗑️  Clearing existing vector database at {vectordb_path}")
            shutil.rmtree(vectordb_path)
        
        # Initialize RAG engine
        print("\n🚀 Initializing RAG engine...")
        rag_engine = RAGEngine(config)
        await rag_engine.initialize()
        
        # Check knowledge base files
        data_path = Path(__file__).parent / "data"
        
        print(f"\n📚 Scanning knowledge base files in {data_path}")
        
        file_counts = {
            "frameworks": 0,
            "case_studies": 0,
            "templates": 0,
            "benchmarks": 0
        }
        
        for category in file_counts.keys():
            category_path = data_path / category
            if category_path.exists():
                files = list(category_path.rglob("*.md")) + list(category_path.rglob("*.txt"))
                file_counts[category] = len(files)
                print(f"   {category}: {len(files)} files")
        
        total_files = sum(file_counts.values())
        
        if total_files == 0:
            print("\n⚠️  No knowledge base files found!")
            print("   Creating sample knowledge base files...")
            create_sample_knowledge_base()
            
            # Rescan after creating sample files
            for category in file_counts.keys():
                category_path = data_path / category
                if category_path.exists():
                    files = list(category_path.rglob("*.md")) + list(category_path.rglob("*.txt"))
                    file_counts[category] = len(files)
            
            total_files = sum(file_counts.values())
        
        print(f"\n📊 Total files to process: {total_files}")
        
        # Rebuild knowledge base
        print("\n🔄 Rebuilding vector database...")
        await rag_engine.rebuild_knowledge_base()
        
        # Verify the rebuild
        print("\n✅ Verifying vector database...")
        
        # Test search functionality
        test_queries = [
            "DREAM框架",
            "假设验证",
            "单位经济学",
            "商业模式"
        ]
        
        for query in test_queries:
            results = await rag_engine.search_knowledge(query, k=2)
            print(f"   Query '{query}': {len(results)} results found")
            
            if results:
                # Show sample result
                sample = results[0]
                content_preview = sample['content'][:100] + "..." if len(sample['content']) > 100 else sample['content']
                print(f"     Sample: {content_preview}")
        
        # Get final statistics
        if hasattr(rag_engine.vectorstore, '_collection'):
            doc_count = rag_engine.vectorstore._collection.count()
            print(f"\n📈 Vector database statistics:")
            print(f"   Total document chunks: {doc_count}")
            print(f"   Collection name: {config['vector_db']['collection_name']}")
            print(f"   Storage location: {vectordb_path}")
        
        print("\n🎉 Vector database rebuild completed successfully!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Vector database rebuild failed: {e}")
        print("   Check the error messages above for troubleshooting")
        return False

def create_sample_knowledge_base():
    """Create sample knowledge base files if none exist"""
    
    # Ensure directories exist
    data_path = Path(__file__).parent / "data"
    for subdir in ["frameworks", "case_studies", "templates", "benchmarks"]:
        (data_path / subdir).mkdir(parents=True, exist_ok=True)
    
    # DREAM Framework documentation
    dream_framework_content = """# DREAM商业分析框架详解

DREAM框架是一套系统化的商业分析方法论，专为中国市场设计，帮助创业者、投资人和商业专业人士进行全面的商业案例分析。

## 框架概述

DREAM代表五个核心分析维度：
- **D**emand (需求)
- **R**esolution (解决方案)  
- **E**arning (商业模式)
- **A**cquisition (增长)
- **M**oat (壁垒)

## 第一步：需求分析 (Demand)

### 目标用户分析
- 早期用户识别和画像构建
- 用户细分和优先级排序
- 用户需求层次分析
- 用户行为模式研究

### 市场规模评估
- TAM (Total Addressable Market) - 总体可获得市场
- SAM (Serviceable Addressable Market) - 可服务获得市场
- SOM (Serviceable Obtainable Market) - 可获得市场份额
- 市场增长趋势和驱动因素

### 需求验证方法
- 问题-解决方案匹配度评估
- 痛点严重程度分析（频率 × 强度）
- 替代方案评估和竞争分析
- 用户真实需求验证实验设计

## 第二步：解决方案分析 (Resolution)

### 产品内核定义
- 最小可行解决方案 (MVS) 识别
- 核心功能优先级矩阵
- 产品开发路线图规划
- 技术可行性评估

### 价值主张设计
- 核心价值主张阐述
- 用户价值计算公式：(新体验-旧体验) - 替换成本
- 价值传递机制设计
- 价值感知优化策略

### 竞争差异化
- 竞争对手解决方案对比分析
- 差异化优势识别和强化
- 产品-市场匹配度评估
- 独特卖点 (USP) 定义

## 第三步：商业模式分析 (Earning)

### 单位经济学建模
- 单位模型定义和选择标准
- 单位收入计算和预测
- 成本结构分析（固定成本 vs 变动成本）
- 贡献边际评估和优化

### 收入模式设计
- 一次性收费模式
- 订阅/会员制模式
- 佣金/分成模式
- 广告收入模式
- 免费增值模式
- 多元化收入流组合

### 财务可行性分析
- 盈亏平衡分析
- 现金流预测（3-5年）
- 规模化经济学效应
- 敏感性分析和压力测试

## 第四步：增长分析 (Acquisition)

### 获客策略设计
- 获客渠道识别和评估
- 客户获取成本 (CAC) 分析
- 客户生命周期价值 (LTV) 计算
- LTV/CAC 比率优化

### AARRR漏斗分析
- **Acquisition** (获取): 用户获取策略和渠道
- **Activation** (激活): 用户激活机制和转化率
- **Retention** (留存): 用户留存策略和留存率
- **Revenue** (收入): 收入优化和ARPU提升
- **Referral** (推荐): 推荐机制和病毒系数

### 规模化机制
- 增长循环设计和优化
- 病毒式传播机制构建
- 网络效应利用策略
- 市场扩张和渗透计划

## 第五步：壁垒分析 (Moat)

### 竞争优势识别
- 核心竞争力分析
- 独特资源和能力盘点
- 技术壁垒评估
- 品牌价值和用户认知

### 护城河构建
- 网络效应分析和强化
- 规模效应评估和利用
- 转换成本分析和提升
- 数据护城河构建策略

### 进入壁垒分析
- 资本要求评估
- 监管壁垒分析
- 技术门槛评估
- 市场准入难度

### 可持续性评估
- 长期竞争优势维护
- 护城河加深策略
- 防御性措施设计
- 竞争威胁应对预案

## DREAM框架应用原则

### 系统性原则
- 按照D-R-E-A-M顺序进行系统分析
- 各环节相互关联，形成闭环
- 避免孤立分析单个维度

### 假设驱动原则
- 每个分析环节都要识别关键假设
- 设计验证实验测试假设
- 基于验证结果迭代优化

### 数据支撑原则
- 定性分析与定量分析相结合
- 使用行业基准数据对比
- 建立数据收集和分析机制

### 迭代优化原则
- 商业模式是动态演进的
- 定期回顾和更新分析结果
- 根据市场反馈调整策略

## 成功案例应用

DREAM框架已成功应用于多个行业的商业分析：
- 互联网和移动应用
- SaaS和企业服务
- 电商和零售
- 教育和培训
- 金融科技
- 健康医疗

通过系统化的DREAM分析，能够显著提高商业决策的质量和成功概率。
"""

    # Hypothesis validation methodology
    hypothesis_content = """# 假设驱动的商业分析方法论

## 方法论概述

假设驱动分析是DREAM框架的核心方法论，通过系统化的假设识别、优先级评估和快速验证，帮助商业决策者在不确定性环境中做出更好的决策。

## 假设识别三步法

### 第一步：加法环节 - 假设拆解

目标：拆解出尽量多的商业假设，确保分析的全面性。

#### 用户需求假设
- 目标用户群体假设
- 用户痛点和需求假设
- 需求紧迫性和频率假设
- 用户支付意愿假设
- 用户行为模式假设

#### 解决方案假设
- 产品功能有效性假设
- 技术可行性假设
- 用户体验假设
- 产品-市场匹配假设
- 竞争差异化假设

#### 商业模式假设
- 收入模式可行性假设
- 定价策略合理性假设
- 成本结构假设
- 单位经济学假设
- 规模化可能性假设

#### 增长假设
- 获客渠道有效性假设
- 转化率假设
- 留存率假设
- 病毒传播假设
- 市场扩张假设

#### 竞争假设
- 竞争优势持续性假设
- 市场进入壁垒假设
- 竞争对手反应假设
- 护城河构建假设

### 第二步：减法环节 - 关键假设筛选

目标：从众多假设中筛选出最关键的假设，集中资源进行验证。

#### 筛选标准

**影响业务关键路径**
- 假设的成立与否直接影响商业模式的核心环节
- 对整体业务成功具有决定性作用
- 影响多个业务环节的连锁假设

**大幅提升业务表现**
- 假设验证成功能显著提升业务指标
- 对收入、成本、用户增长有重大影响
- 能够创造竞争优势的假设

**能力资源匹配**
- 团队有能力和资源去验证这个假设
- 验证成本在可承受范围内
- 验证时间窗口合理

**时间窗口适宜**
- 市场时机和竞争环境适合验证
- 能够在合理时间内得到验证结果
- 不会错过关键的市场机会

### 第三步：验证环节 - 快速学习验证

目标：设计高效的验证方法，快速获得假设验证结果。

#### 验证方法分类

**靠常识验证**
- 适用场景：行业通用规律、基础商业逻辑
- 验证方法：行业经验和基准数据对比、专家判断和理论分析

**靠调研验证**
- 适用场景：用户需求、市场状况、竞争情况
- 验证方法：用户深度访谈、问卷调查、竞品分析

**靠实验验证**
- 适用场景：产品功能、商业模式、增长策略
- 验证方法：MVP测试、A/B测试、试点项目

通过系统化的假设驱动分析，能够显著提高商业决策的科学性和成功率。
"""

    # Unit economics template
    unit_economics_content = """# 单位经济学建模指南

## 单位定义
- 明确定义分析单位（用户、交易、产品等）
- 确保单位的可测量性和一致性
- 考虑单位的业务意义和可操作性

## 收入模型
- 一次性收费模式
- 订阅/会员模式
- 佣金/分成模式
- 广告收入模式
- 免费增值模式

## 成本结构
- 固定成本：不随业务量变化的成本
- 变动成本：随业务量变化的成本
- 半变动成本：部分固定部分变动的成本

## 关键指标
- 单位收入 (Revenue per Unit)
- 单位成本 (Cost per Unit)
- 贡献边际 (Contribution Margin)
- 客户获取成本 (CAC)
- 客户生命周期价值 (LTV)
- LTV/CAC比率

## 健康度评估
- 贡献边际 > 0
- LTV/CAC > 3
- 回收期 < 12个月
- 成本结构合理平衡

## 优化策略
- 提高单位收入：优化定价、增值服务
- 降低单位成本：规模效应、流程优化
- 改善获客效率：渠道优化、转化提升
- 延长客户生命周期：提升留存、增加复购
"""
    
    # Write sample files
    sample_files = {
        "data/frameworks/dream_framework_detailed.md": dream_framework_content,
        "data/frameworks/hypothesis_driven_methodology.md": hypothesis_content,
        "data/templates/unit_economics_modeling.md": unit_economics_content
    }
    
    for file_path, content in sample_files.items():
        Path(file_path).parent.mkdir(parents=True, exist_ok=True)
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
    
    print("✅ Sample knowledge base created")

async def main():
    """Main function"""
    success = await rebuild_vector_database()
    
    if success:
        print("\n🚀 Next steps:")
        print("   1. Start the server: python start.py")
        print("   2. Test the system: python test_system.py")
        print("   3. Try examples: python example_analysis.py")
    else:
        print("\n❌ Please fix the errors above and try again")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())