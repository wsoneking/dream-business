#!/usr/bin/env python3
"""
DREAM Business Analysis AI - Example Analysis
Demonstrate the system with real business analysis examples
"""

import asyncio
import json
import sys
from pathlib import Path

# Add the project root to Python path
sys.path.append(str(Path(__file__).parent))

async def example_complete_dream_analysis():
    """Example of complete DREAM framework analysis"""
    print("🎯 Complete DREAM Framework Analysis Example")
    print("=" * 60)
    
    business_case = """
    商业案例：智能停车解决方案

    背景：
    在中国一线城市，停车难是一个普遍问题。我们计划开发一个智能停车平台，
    连接停车场、车主和城市管理部门，通过IoT设备、移动应用和数据分析
    提供智能停车服务。

    核心功能：
    1. 实时停车位查询和预订
    2. 智能导航到停车位
    3. 无感支付和自动计费
    4. 停车场运营优化
    5. 城市停车数据分析

    目标市场：
    - 一线城市的车主（C端）
    - 商业停车场运营商（B端）
    - 城市交通管理部门（G端）
    """
    
    print("📋 Business Case:")
    print(business_case)
    
    try:
        from app.business_analyzer import DreamBusinessAnalyzer
        from app.rag_engine import RAGEngine
        import yaml
        
        # Load config
        config_path = Path(__file__).parent / "config" / "ollama_config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Initialize components
        rag_engine = RAGEngine(config)
        await rag_engine.initialize()
        
        analyzer = DreamBusinessAnalyzer(config, rag_engine)
        
        print("\n🔍 Running DREAM Analysis...")
        
        # Complete DREAM analysis
        result = await analyzer.analyze_complete_dream(business_case)
        
        if result["status"] == "success":
            print("\n📊 DREAM Analysis Results:")
            print("-" * 40)
            print(result["analysis"])
        else:
            print(f"❌ Analysis failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Example failed: {e}")
        print("   Make sure the system is properly set up and Ollama is running")

async def example_hypothesis_generation():
    """Example of hypothesis generation"""
    print("\n💡 Hypothesis Generation Example")
    print("=" * 60)
    
    business_case = """
    商业案例：在线教育平台 - 职业技能培训

    我们计划创建一个专注于职业技能培训的在线教育平台，
    主要面向希望提升职业技能的在职人员。平台将提供：
    - 实用的职业技能课程（编程、设计、营销等）
    - 项目实战和作品集指导
    - 行业导师一对一辅导
    - 就业推荐和职业规划服务
    """
    
    print("📋 Business Case:")
    print(business_case)
    
    try:
        from app.business_analyzer import DreamBusinessAnalyzer
        from app.rag_engine import RAGEngine
        import yaml
        
        # Load config
        config_path = Path(__file__).parent / "config" / "ollama_config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        # Initialize components
        rag_engine = RAGEngine(config)
        await rag_engine.initialize()
        
        analyzer = DreamBusinessAnalyzer(config, rag_engine)
        
        print("\n🧠 Generating Business Hypotheses...")
        
        # Generate hypotheses
        result = await analyzer.generate_hypotheses(business_case)
        
        if result["status"] == "success":
            print("\n💡 Generated Hypotheses:")
            print("-" * 40)
            print(result["analysis"])
        else:
            print(f"❌ Hypothesis generation failed: {result.get('error', 'Unknown error')}")
            
    except Exception as e:
        print(f"❌ Example failed: {e}")

def example_unit_economics_modeling():
    """Example of unit economics modeling"""
    print("\n💰 Unit Economics Modeling Example")
    print("=" * 60)
    
    try:
        from tools.unit_economics import unit_economics_calculator, RevenueModel, CostType
        
        # Create SaaS business model
        print("📊 Creating SaaS Business Unit Economics Model...")
        
        model = unit_economics_calculator.create_model(
            name="EdTech_SaaS",
            unit_definition="每个付费学员每月",
            currency="CNY"
        )
        
        # Add revenue streams
        unit_economics_calculator.add_revenue_stream(
            "EdTech_SaaS",
            "月度订阅费",
            199.0,
            RevenueModel.SUBSCRIPTION,
            "基础课程访问权限"
        )
        
        unit_economics_calculator.add_revenue_stream(
            "EdTech_SaaS",
            "高级服务费",
            99.0,
            RevenueModel.FREEMIUM,
            "一对一辅导和就业服务"
        )
        
        # Add cost items
        unit_economics_calculator.add_cost_item(
            "EdTech_SaaS",
            "内容制作成本",
            30.0,
            CostType.VARIABLE,
            "课程开发和更新",
            "COGS"
        )
        
        unit_economics_calculator.add_cost_item(
            "EdTech_SaaS",
            "平台运营成本",
            25.0,
            CostType.VARIABLE,
            "服务器、CDN等技术成本",
            "Operations"
        )
        
        unit_economics_calculator.add_cost_item(
            "EdTech_SaaS",
            "客户获取成本",
            80.0,
            CostType.VARIABLE,
            "营销推广和销售成本",
            "CAC"
        )
        
        unit_economics_calculator.add_cost_item(
            "EdTech_SaaS",
            "客户服务成本",
            15.0,
            CostType.VARIABLE,
            "客服和技术支持",
            "Operations"
        )
        
        # Generate comprehensive report
        report = unit_economics_calculator.generate_unit_economics_report("EdTech_SaaS")
        
        print("\n📊 Unit Economics Report:")
        print("-" * 40)
        print(f"模型名称: {report['model_name']}")
        print(f"单位定义: {report['unit_definition']}")
        print(f"分析周期: {report['time_period']}")
        print(f"货币单位: {report['currency']}")
        
        print("\n💰 关键指标:")
        metrics = report['key_metrics']
        print(f"  总收入: ¥{metrics['total_revenue']:.2f}")
        print(f"  总成本: ¥{metrics['total_costs']:.2f}")
        print(f"  贡献边际: ¥{metrics['contribution_margin']:.2f}")
        print(f"  贡献边际率: {metrics['contribution_margin_percentage']:.1f}%")
        print(f"  变动成本: ¥{metrics['variable_costs']:.2f}")
        print(f"  固定成本: ¥{metrics['fixed_costs']:.2f}")
        
        print("\n📈 收入构成:")
        for revenue in report['revenue_breakdown']:
            print(f"  {revenue['name']}: ¥{revenue['amount']:.2f} ({revenue['percentage']:.1f}%)")
        
        print("\n📉 成本构成:")
        for cost in report['cost_breakdown']:
            print(f"  {cost['name']}: ¥{cost['amount']:.2f} ({cost['percentage']:.1f}%)")
        
        print(f"\n🏥 健康评分: {report['health_score']['percentage']:.1f}% - {report['health_score']['status']}")
        print(f"评估: {report['health_score']['description']}")
        
        print("\n💡 优化建议:")
        for recommendation in report['recommendations']:
            print(f"  • {recommendation}")
        
        # Calculate LTV/CAC ratio
        ltv_cac = unit_economics_calculator.calculate_ltv_cac_ratio(
            "EdTech_SaaS",
            customer_lifetime_months=12,
            churn_rate=0.05,
            cac_amount=80.0
        )
        
        print(f"\n📊 LTV/CAC 分析:")
        print(f"  客户生命周期价值 (LTV): ¥{ltv_cac['ltv_method1']:.2f}")
        print(f"  客户获取成本 (CAC): ¥{ltv_cac['cac']:.2f}")
        print(f"  LTV/CAC 比率: {ltv_cac['ltv_cac_ratio1']:.2f}")
        print(f"  回收期: {ltv_cac['payback_period_months']:.1f} 个月")
        print(f"  评估: {ltv_cac['assessment']}")
        
    except Exception as e:
        print(f"❌ Unit economics example failed: {e}")

def example_roi_analysis():
    """Example of ROI analysis"""
    print("\n📈 ROI Analysis Example")
    print("=" * 60)
    
    try:
        from tools.roi_calculator import roi_calculator, InvestmentType, CashFlowType
        
        print("💼 Creating Product Development Investment Analysis...")
        
        # Create investment
        investment = roi_calculator.create_investment(
            name="EdTech_Platform_Development",
            investment_type=InvestmentType.PRODUCT_DEVELOPMENT,
            description="在线教育平台开发投资分析",
            discount_rate=0.12,  # 12% discount rate
            analysis_period_years=3
        )
        
        # Add cash flows
        # Initial investment
        roi_calculator.add_cash_flow(
            "EdTech_Platform_Development",
            0,
            -500000,  # 50万初始投资
            CashFlowType.INITIAL_INVESTMENT,
            "平台开发、团队组建、初期运营成本"
        )
        
        # Year 1 cash flows
        roi_calculator.add_cash_flow(
            "EdTech_Platform_Development",
            1,
            150000,  # 15万收入
            CashFlowType.OPERATING_CASH_FLOW,
            "第一年运营收入"
        )
        
        # Year 2 cash flows
        roi_calculator.add_cash_flow(
            "EdTech_Platform_Development",
            2,
            300000,  # 30万收入
            CashFlowType.OPERATING_CASH_FLOW,
            "第二年运营收入"
        )
        
        # Year 3 cash flows
        roi_calculator.add_cash_flow(
            "EdTech_Platform_Development",
            3,
            450000,  # 45万收入
            CashFlowType.OPERATING_CASH_FLOW,
            "第三年运营收入"
        )
        
        # Calculate various metrics
        simple_roi = roi_calculator.calculate_simple_roi("EdTech_Platform_Development")
        npv_analysis = roi_calculator.calculate_npv("EdTech_Platform_Development")
        irr_analysis = roi_calculator.calculate_irr("EdTech_Platform_Development")
        payback_analysis = roi_calculator.calculate_payback_period("EdTech_Platform_Development")
        
        print("\n📊 ROI Analysis Results:")
        print("-" * 40)
        
        print("💰 简单ROI分析:")
        print(f"  总投资: ¥{simple_roi['total_investment']:,.2f}")
        print(f"  总回报: ¥{simple_roi['total_returns']:,.2f}")
        print(f"  净利润: ¥{simple_roi['net_profit']:,.2f}")
        print(f"  ROI: {simple_roi['simple_roi_percentage']:.1f}%")
        
        print(f"\n📈 净现值 (NPV) 分析:")
        print(f"  NPV: ¥{npv_analysis['npv']:,.2f}")
        print(f"  折现率: {npv_analysis['discount_rate']:.1f}%")
        print(f"  评估: {npv_analysis['npv_assessment']}")
        print(f"  建议: {npv_analysis['recommendation']}")
        
        print(f"\n⚡ 内部收益率 (IRR) 分析:")
        if irr_analysis.get('irr_percentage'):
            print(f"  IRR: {irr_analysis['irr_percentage']:.1f}%")
            print(f"  门槛收益率: {irr_analysis['hurdle_rate_percentage']:.1f}%")
            print(f"  评估: {irr_analysis['assessment']}")
            print(f"  建议: {irr_analysis['recommendation']}")
        else:
            print("  IRR计算失败")
        
        print(f"\n⏰ 投资回收期分析:")
        if payback_analysis.get('payback_period_years'):
            print(f"  回收期: {payback_analysis['payback_period_years']:.1f} 年")
            print(f"  回收期: {payback_analysis['payback_period_months']:.0f} 个月")
            print(f"  评估: {payback_analysis['assessment']}")
        else:
            print("  投资无法在分析期内回收")
        
        # Generate comprehensive report
        report = roi_calculator.generate_investment_report("EdTech_Platform_Development")
        
        print(f"\n🎯 综合评估:")
        print(f"  投资评分: {report['overall_score']['percentage']:.1f}%")
        print(f"  风险等级: {report['risk_assessment']['risk_level']}")
        print(f"  最终建议: {report['final_recommendation']}")
        
    except Exception as e:
        print(f"❌ ROI analysis example failed: {e}")

def example_business_canvas():
    """Example of business canvas generation"""
    print("\n🎨 Business Canvas Generation Example")
    print("=" * 60)
    
    try:
        from tools.canvas_generator import canvas_generator, CanvasType
        
        print("🖼️ Creating Business Model Canvas...")
        
        # Create business model canvas
        canvas = canvas_generator.create_canvas(
            name="EdTech_BMC",
            canvas_type=CanvasType.BUSINESS_MODEL,
            description="在线教育平台商业模式画布"
        )
        
        # Populate canvas with content
        canvas_content = {
            "customer_segments": [
                "在职白领（25-35岁）",
                "应届毕业生",
                "职业转换者",
                "自由职业者"
            ],
            "value_propositions": [
                "实用的职业技能提升",
                "灵活的学习时间安排",
                "项目实战经验",
                "就业指导和推荐",
                "行业导师指导"
            ],
            "channels": [
                "移动应用和网站",
                "社交媒体营销",
                "企业合作推广",
                "口碑推荐",
                "线下活动和讲座"
            ],
            "customer_relationships": [
                "个性化学习体验",
                "社区互动和讨论",
                "导师一对一指导",
                "学习进度跟踪",
                "就业服务支持"
            ],
            "revenue_streams": [
                "课程订阅费用",
                "高级服务费用",
                "企业培训服务",
                "认证考试费用",
                "就业推荐佣金"
            ],
            "key_resources": [
                "优质课程内容",
                "技术平台和系统",
                "行业专家导师",
                "用户数据和算法",
                "品牌和声誉"
            ],
            "key_activities": [
                "课程内容开发",
                "平台技术维护",
                "用户获取和留存",
                "导师管理和培训",
                "就业服务运营"
            ],
            "key_partners": [
                "行业专家和导师",
                "企业客户",
                "技术服务提供商",
                "就业服务机构",
                "教育内容供应商"
            ],
            "cost_structure": [
                "内容开发成本",
                "技术开发和维护",
                "营销推广费用",
                "人员薪酬",
                "平台运营成本"
            ]
        }
        
        # Add content to canvas
        for element_name, content_list in canvas_content.items():
            canvas_generator.add_canvas_content(
                "EdTech_BMC",
                element_name,
                content_list,
                importance=8,
                confidence=0.8
            )
        
        # Validate canvas
        validation = canvas_generator.validate_canvas("EdTech_BMC")
        
        print("\n📊 Canvas Validation Results:")
        print("-" * 40)
        print(f"完整度评分: {validation['completeness_score']:.1f}%")
        print(f"质量评分: {validation['quality_score']:.1f}%")
        
        if validation['issues']:
            print("\n⚠️ 发现问题:")
            for issue in validation['issues']:
                print(f"  • {issue}")
        
        if validation['recommendations']:
            print("\n💡 改进建议:")
            for rec in validation['recommendations']:
                print(f"  • {rec}")
        
        # Generate comprehensive report
        report = canvas_generator.generate_canvas_report("EdTech_BMC")
        
        print(f"\n🎯 Canvas 综合评估:")
        print(f"  总体评分: {report['overall_score']:.1f}%")
        print(f"  评估结果: {report['assessment']}")
        
        print(f"\n📋 下一步行动:")
        for step in report['next_steps']:
            print(f"  • {step}")
        
        # Export canvas
        print(f"\n📄 Canvas Export (JSON format):")
        print("-" * 40)
        export_json = canvas_generator.export_canvas("EdTech_BMC", "json")
        canvas_data = json.loads(export_json)
        
        print(f"Canvas Name: {canvas_data['name']}")
        print(f"Type: {canvas_data['type']}")
        print(f"Elements: {len(canvas_data['elements'])}")
        
        # Show sample element
        vp_element = canvas_data['elements']['value_propositions']
        print(f"\nSample Element - Value Propositions:")
        for i, item in enumerate(vp_element['content'], 1):
            print(f"  {i}. {item}")
        
    except Exception as e:
        print(f"❌ Business canvas example failed: {e}")

async def main():
    """Main example function"""
    print("🎯 DREAM Business Analysis AI - Examples")
    print("=" * 80)
    
    examples = [
        ("Complete DREAM Analysis", example_complete_dream_analysis()),
        ("Hypothesis Generation", example_hypothesis_generation()),
        ("Unit Economics Modeling", lambda: example_unit_economics_modeling()),
        ("ROI Analysis", lambda: example_roi_analysis()),
        ("Business Canvas", lambda: example_business_canvas())
    ]
    
    for example_name, example_func in examples:
        try:
            print(f"\n{'='*20} {example_name} {'='*20}")
            
            if asyncio.iscoroutine(example_func):
                await example_func
            else:
                example_func()
                
            print(f"\n✅ {example_name} completed successfully")
            
        except Exception as e:
            print(f"❌ {example_name} failed: {e}")
        
        print("\n" + "-" * 80)
    
    print("\n🎉 All examples completed!")
    print("\n🚀 Next steps:")
    print("   1. Start the server: python start.py")
    print("   2. Try the API endpoints with these examples")
    print("   3. Build your own business analysis workflows")

if __name__ == "__main__":
    asyncio.run(main())