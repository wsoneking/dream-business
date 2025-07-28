#!/usr/bin/env python3
"""
BabyCareAI 系统测试脚本
用于验证系统各个组件是否正常工作
"""

import os
import sys
import requests
import time
import yaml
from pathlib import Path

def check_file_exists(file_path: str) -> bool:
    """检查文件是否存在"""
    return os.path.exists(file_path)

def check_directory_exists(dir_path: str) -> bool:
    """检查目录是否存在"""
    return os.path.isdir(dir_path)

def test_ollama_connection():
    """测试 Ollama 连接"""
    print("🔍 测试 Ollama 连接...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print(f"✅ Ollama 连接成功，可用模型: {[m['name'] for m in models]}")
                return True
            else:
                print("⚠️  Ollama 连接成功，但没有可用模型")
                return False
        else:
            print(f"❌ Ollama 连接失败，状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Ollama 连接失败: {str(e)}")
        print("💡 请确保 Ollama 服务正在运行: ollama serve")
        return False

def test_file_structure():
    """测试文件结构"""
    print("\n📁 检查文件结构...")
    
    required_files = [
        "requirements.txt",
        "config/ollama_config.yaml",
        "config/custom_prompt.txt",
        "app/main.py",
        "app/chain.py",
        "app/rag_engine.py",
        "api/routes.py",
        "README.md"
    ]
    
    required_dirs = [
        "app",
        "api", 
        "config",
        "data",
        "data/knowledge",
        "data/faq",
        "app/prompt_templates"
    ]
    
    all_good = True
    
    # 检查文件
    for file_path in required_files:
        if check_file_exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - 文件不存在")
            all_good = False
    
    # 检查目录
    for dir_path in required_dirs:
        if check_directory_exists(dir_path):
            print(f"✅ {dir_path}/")
        else:
            print(f"❌ {dir_path}/ - 目录不存在")
            all_good = False
    
    return all_good

def test_config_files():
    """测试配置文件"""
    print("\n⚙️  检查配置文件...")
    
    try:
        # 检查 YAML 配置
        with open("config/ollama_config.yaml", 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            print("✅ ollama_config.yaml 格式正确")
            
            # 检查必要的配置项
            required_keys = ['ollama', 'vector_db', 'embedding', 'api']
            for key in required_keys:
                if key in config:
                    print(f"✅ 配置项 '{key}' 存在")
                else:
                    print(f"❌ 配置项 '{key}' 缺失")
                    return False
        
        # 检查自定义提示词
        with open("config/custom_prompt.txt", 'r', encoding='utf-8') as f:
            prompt = f.read().strip()
            if prompt:
                print("✅ custom_prompt.txt 内容正常")
            else:
                print("❌ custom_prompt.txt 内容为空")
                return False
        
        return True
        
    except Exception as e:
        print(f"❌ 配置文件检查失败: {str(e)}")
        return False

def test_knowledge_base():
    """测试知识库文件"""
    print("\n📚 检查知识库...")
    
    knowledge_files = list(Path("data/knowledge").glob("*.md"))
    faq_files = list(Path("data/faq").glob("*.txt"))
    
    if knowledge_files:
        print(f"✅ 找到 {len(knowledge_files)} 个知识库文件:")
        for file in knowledge_files:
            print(f"   - {file.name}")
    else:
        print("⚠️  没有找到知识库文件 (.md)")
    
    if faq_files:
        print(f"✅ 找到 {len(faq_files)} 个FAQ文件:")
        for file in faq_files:
            print(f"   - {file.name}")
    else:
        print("⚠️  没有找到FAQ文件 (.txt)")
    
    return len(knowledge_files) > 0 or len(faq_files) > 0

def test_dependencies():
    """测试Python依赖"""
    print("\n📦 检查Python依赖...")
    
    # Map package names to their import names
    package_mapping = {
        "fastapi": "fastapi",
        "uvicorn": "uvicorn",
        "langchain": "langchain",
        "chromadb": "chromadb",
        "sentence-transformers": "sentence_transformers",
        "pydantic": "pydantic",
        "PyYAML": "yaml"
    }
    
    missing_packages = []
    
    for package_name, import_name in package_mapping.items():
        try:
            __import__(import_name.replace("-", "_"))
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - 未安装")
            missing_packages.append(package_name)
    
    if missing_packages:
        print(f"\n💡 请安装缺失的包: pip install {' '.join(missing_packages)}")
        return False
    
    return True

def test_api_server():
    """测试API服务器"""
    print("\n🌐 测试API服务器...")
    
    # 检查服务器是否运行
    try:
        response = requests.get("http://localhost:8000/api/v1/health", timeout=5)
        if response.status_code == 200:
            result = response.json()
            print(f"✅ API服务器运行正常")
            print(f"   状态: {result.get('status', 'unknown')}")
            print(f"   初始化: {result.get('initialized', False)}")
            return True
        else:
            print(f"⚠️  API服务器响应异常，状态码: {response.status_code}")
            return False
    except requests.exceptions.RequestException:
        print("❌ API服务器未运行")
        print("💡 请启动服务器: python app/main.py")
        return False

def test_simple_query():
    """测试简单查询"""
    print("\n🤖 测试简单查询...")
    
    try:
        response = requests.post(
            "http://localhost:8000/api/v1/ask-simple",
            json={"question": "你好"},
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("✅ 简单查询测试成功")
            print(f"   回答: {result.get('answer', '')[:100]}...")
            return True
        else:
            print(f"❌ 简单查询失败，状态码: {response.status_code}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"❌ 简单查询失败: {str(e)}")
        return False

def main():
    """主测试函数"""
    print("🍼 BabyCareAI 系统测试")
    print("=" * 50)
    
    tests = [
        ("文件结构", test_file_structure),
        ("配置文件", test_config_files),
        ("知识库", test_knowledge_base),
        ("Python依赖", test_dependencies),
        ("Ollama连接", test_ollama_connection),
    ]
    
    # 运行基础测试
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        if test_func():
            passed += 1
        else:
            print(f"\n❌ {test_name} 测试失败")
    
    print(f"\n📊 基础测试结果: {passed}/{total} 通过")
    
    # 如果基础测试通过，进行API测试
    if passed == total:
        print("\n🚀 基础测试全部通过，进行API测试...")
        
        api_tests = [
            ("API服务器", test_api_server),
            ("简单查询", test_simple_query),
        ]
        
        api_passed = 0
        for test_name, test_func in api_tests:
            if test_func():
                api_passed += 1
        
        print(f"\n📊 API测试结果: {api_passed}/{len(api_tests)} 通过")
        
        if api_passed == len(api_tests):
            print("\n🎉 所有测试通过！系统运行正常！")
            print("\n📖 访问 http://localhost:8000 查看系统主页")
            print("📚 访问 http://localhost:8000/docs 查看API文档")
        else:
            print("\n⚠️  部分API测试失败，请检查服务器状态")
    else:
        print("\n⚠️  基础测试未全部通过，请先解决基础问题")
    
    print("\n" + "=" * 50)

if __name__ == "__main__":
    main()