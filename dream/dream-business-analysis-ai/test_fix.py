#!/usr/bin/env python3
"""
Test script to verify the FieldInfo fix
"""

import asyncio
import yaml
from pathlib import Path
from app.business_analyzer import DreamBusinessAnalyzer
from app.rag_engine import RAGEngine

async def test_business_analyzer():
    """Test the business analyzer with a simple case"""
    
    # Load config
    config_path = Path(__file__).parent / "config" / "ollama_config.yaml"
    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)
    
    print("🔧 Initializing components...")
    
    # Initialize RAG Engine
    rag_engine = RAGEngine(config)
    await rag_engine.initialize()
    print("✅ RAG Engine initialized")
    
    # Initialize Business Analyzer
    business_analyzer = DreamBusinessAnalyzer(config, rag_engine)
    print("✅ Business Analyzer initialized")
    
    # Test case
    test_case = """
    商业案例：智能健身教练APP
    业务类型：移动应用
    
    详细描述：
    一款基于AI的个人健身教练应用，为用户提供个性化的健身计划、实时动作指导、进度跟踪和营养建议。
    
    产品特色：
    - AI动作识别和纠正技术
    - 个性化训练计划生成
    - 实时健身数据分析
    - 社区互动和挑战功能
    - 智能营养建议系统
    
    目标用户：
    - 25-40岁城市白领
    - 有健身需求但缺乏专业指导
    - 愿意为健康投资的中高收入人群
    """
    
    print("🧠 Testing Demand Analysis...")
    try:
        result = await business_analyzer.analyze_demand(test_case)
        if result['status'] == 'success':
            print("✅ Demand analysis successful!")
            print(f"Analysis preview: {result['analysis'][:200]}...")
        else:
            print(f"❌ Demand analysis failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Demand analysis exception: {e}")
    
    print("🧠 Testing Resolution Analysis...")
    try:
        result = await business_analyzer.analyze_resolution(test_case)
        if result['status'] == 'success':
            print("✅ Resolution analysis successful!")
            print(f"Analysis preview: {result['analysis'][:200]}...")
        else:
            print(f"❌ Resolution analysis failed: {result.get('error', 'Unknown error')}")
    except Exception as e:
        print(f"❌ Resolution analysis exception: {e}")

if __name__ == "__main__":
    asyncio.run(test_business_analyzer())