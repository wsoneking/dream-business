#!/usr/bin/env python3
"""
BabyCareAI 使用示例
演示如何与育儿顾问系统交互
"""

import requests
import json
import time
from typing import Dict, Any

# API基础URL
BASE_URL = "http://localhost:8000/api/v1"

def check_system_health():
    """检查系统健康状态"""
    print("🔍 检查系统状态...")
    try:
        response = requests.get(f"{BASE_URL}/health", timeout=10)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ 系统状态: {result['status']}")
            print(f"✅ 初始化状态: {'已初始化' if result['initialized'] else '未初始化'}")
            return result['initialized']
        else:
            print(f"❌ 系统检查失败，状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ 无法连接到系统: {str(e)}")
        print("💡 请确保系统正在运行: python start.py")
        return False

def ask_question(question: str, baby_info: Dict[str, Any] = None):
    """向系统提问"""
    print(f"\n❓ 问题: {question}")
    
    if baby_info:
        print(f"👶 宝宝信息: {baby_info}")
    
    try:
        payload = {"question": question}
        if baby_info:
            payload["baby_info"] = baby_info
        
        print("🤔 AI思考中...")
        response = requests.post(
            f"{BASE_URL}/ask",
            json=payload,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n🤖 AI回答:")
            print(f"{result['answer']}")
            
            if result.get('sources'):
                print(f"\n📚 参考来源 ({len(result['sources'])} 个):")
                for i, source in enumerate(result['sources'][:2], 1):
                    print(f"   {i}. {source['content'][:100]}...")
            
            return result
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {str(e)}")
        return None

def ask_simple_question(question: str):
    """简单提问（不使用RAG）"""
    print(f"\n❓ 简单问题: {question}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/ask-simple",
            json={"question": question},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\n🤖 AI回答:")
            print(f"{result['answer']}")
            return result
        else:
            print(f"❌ 请求失败，状态码: {response.status_code}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 请求失败: {str(e)}")
        return None

def get_example_questions():
    """获取示例问题"""
    try:
        response = requests.get(f"{BASE_URL}/example-questions")
        if response.status_code == 200:
            return response.json()
        return None
    except:
        return None

def interactive_demo():
    """交互式演示"""
    print("\n🎯 交互式演示模式")
    print("输入 'quit' 退出，输入 'help' 查看帮助")
    
    while True:
        print("\n" + "-" * 50)
        question = input("❓ 请输入您的问题: ").strip()
        
        if question.lower() == 'quit':
            print("👋 再见！")
            break
        elif question.lower() == 'help':
            print("""
📖 帮助信息:
- 直接输入问题，如：新生儿一天要喂几次奶？
- 输入 'quit' 退出
- 输入 'baby' 设置宝宝信息
- 输入 'examples' 查看示例问题
            """)
            continue
        elif question.lower() == 'baby':
            print("👶 请输入宝宝信息:")
            age = input("年龄 (如: 2个月): ").strip()
            weight = input("体重 (如: 5.5kg): ").strip()
            gender = input("性别 (男/女): ").strip()
            
            baby_info = {}
            if age: baby_info['age'] = age
            if weight: baby_info['weight'] = weight
            if gender: baby_info['gender'] = gender
            
            print(f"✅ 宝宝信息已设置: {baby_info}")
            continue
        elif question.lower() == 'examples':
            examples = get_example_questions()
            if examples:
                print("\n📝 示例问题:")
                for category in examples['examples']:
                    print(f"\n{category['category']}:")
                    for q in category['questions']:
                        print(f"  - {q}")
            continue
        elif not question:
            print("⚠️  请输入问题")
            continue
        
        # 提问
        ask_question(question)

def main():
    """主演示函数"""
    print("🍼 BabyCareAI 使用示例")
    print("=" * 50)
    
    # 检查系统状态
    if not check_system_health():
        return
    
    print("\n🎬 开始演示...")
    
    # 示例1: 基础问题
    print("\n" + "=" * 50)
    print("📝 示例1: 基础育儿问题")
    ask_question("新生儿一天要喂几次奶？")
    
    time.sleep(2)
    
    # 示例2: 带宝宝信息的问题
    print("\n" + "=" * 50)
    print("📝 示例2: 个性化问题（带宝宝信息）")
    baby_info = {
        "age": "3个月",
        "weight": "6kg",
        "gender": "女"
    }
    ask_question("我的宝宝睡眠不规律，经常夜醒，怎么办？", baby_info)
    
    time.sleep(2)
    
    # 示例3: 健康问题
    print("\n" + "=" * 50)
    print("📝 示例3: 健康相关问题")
    baby_info = {
        "age": "2个月",
        "weight": "5.5kg",
        "gender": "男"
    }
    ask_question("宝宝发烧了，体温38.2度，应该怎么处理？", baby_info)
    
    time.sleep(2)
    
    # 示例4: 简单问答
    print("\n" + "=" * 50)
    print("📝 示例4: 简单问答（不使用知识库）")
    ask_simple_question("你好，请介绍一下你自己")
    
    time.sleep(2)
    
    # 示例5: 英文问题
    print("\n" + "=" * 50)
    print("📝 示例5: 英文问题测试（多语言支持）")
    baby_info_en = {
        "age": "3 months",
        "weight": "6kg",
        "gender": "female"
    }
    ask_question("How often should I feed my 3-month-old baby?", baby_info_en)
    
    time.sleep(2)
    
    # 获取系统统计
    print("\n" + "=" * 50)
    print("📊 系统统计信息")
    try:
        response = requests.get(f"{BASE_URL}/knowledge-stats")
        if response.status_code == 200:
            stats = response.json()
            print(f"📚 知识库文档数量: {stats['document_count']}")
            print(f"📊 系统状态: {stats['status']}")
        
        # 获取示例问题
        examples = get_example_questions()
        if examples:
            total_examples = sum(len(cat['questions']) for cat in examples['examples'])
            print(f"❓ 示例问题数量: {total_examples}")
            
    except Exception as e:
        print(f"⚠️  获取统计信息失败: {str(e)}")
    
    # 交互式演示
    print("\n" + "=" * 50)
    choice = input("🎯 是否进入交互式演示模式？(y/n): ").strip().lower()
    if choice == 'y':
        interactive_demo()
    else:
        print("\n✅ 演示完成！")
        print("💡 您可以:")
        print("   - 访问 http://localhost:8000 查看系统主页")
        print("   - 访问 http://localhost:8000/docs 查看API文档")
        print("   - 运行 python example_usage.py 重新演示")

if __name__ == "__main__":
    main()