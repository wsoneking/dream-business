#!/usr/bin/env python3
"""
BabyCareAI 系统启动脚本
简化系统启动流程
"""

import os
import sys
import subprocess
import time
import requests
import yaml
from pathlib import Path

def print_banner():
    """打印启动横幅"""
    banner = """
🍼 BabyCareAI 育儿顾问系统
================================
基于 Ollama 本地大模型和 LangChain 构建
为新手父母提供专业、温暖的育儿指导
================================
"""
    print(banner)

def check_python_version():
    """检查Python版本"""
    if sys.version_info < (3, 8):
        print("❌ Python版本过低，需要Python 3.8+")
        print(f"   当前版本: {sys.version}")
        return False
    print(f"✅ Python版本: {sys.version.split()[0]}")
    return True

def check_ollama_service():
    """检查Ollama服务"""
    print("🔍 检查Ollama服务...")
    try:
        response = requests.get("http://localhost:11434/api/tags", timeout=5)
        if response.status_code == 200:
            models = response.json().get("models", [])
            if models:
                print(f"✅ Ollama服务运行正常，可用模型:")
                for model in models:
                    print(f"   - {model['name']}")
                return True
            else:
                print("⚠️  Ollama服务运行，但没有可用模型")
                print("💡 请拉取模型: ollama pull llama3")
                return False
        else:
            print("❌ Ollama服务异常")
            return False
    except requests.exceptions.RequestException:
        print("❌ Ollama服务未运行")
        print("💡 请启动Ollama服务:")
        print("   1. 安装Ollama: https://ollama.ai/")
        print("   2. 启动服务: ollama serve")
        print("   3. 拉取模型: ollama pull llama3")
        return False

def check_dependencies():
    """检查依赖包"""
    print("📦 检查依赖包...")
    
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
    
    missing = []
    for package_name, import_name in package_mapping.items():
        try:
            __import__(import_name.replace("-", "_"))
        except ImportError:
            missing.append(package_name)
    
    if missing:
        print(f"❌ 缺少依赖包: {', '.join(missing)}")
        print("💡 安装依赖: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def check_config():
    """检查配置文件"""
    print("⚙️  检查配置文件...")
    
    # Get the current script directory (should be project root)
    project_root = Path(__file__).parent
    
    config_files = [
        "config/ollama_config.yaml",
        "config/custom_prompt.txt"
    ]
    
    for config_file in config_files:
        config_path = project_root / config_file
        if not config_path.exists():
            print(f"❌ 配置文件不存在: {config_path}")
            return False
    
    # 检查配置内容
    try:
        config_path = project_root / "config/ollama_config.yaml"
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            model_name = config.get('ollama', {}).get('model', 'llama3')
            print(f"✅ 配置文件正常，使用模型: {model_name}")
            return True
    except Exception as e:
        print(f"❌ 配置文件格式错误: {str(e)}")
        return False

def check_knowledge_base():
    """检查知识库"""
    print("📚 检查知识库...")
    
    knowledge_dir = Path("data/knowledge")
    faq_dir = Path("data/faq")
    
    knowledge_files = list(knowledge_dir.glob("*.md")) if knowledge_dir.exists() else []
    faq_files = list(faq_dir.glob("*.txt")) if faq_dir.exists() else []
    
    if knowledge_files or faq_files:
        print(f"✅ 知识库文件: {len(knowledge_files)} 个MD文件, {len(faq_files)} 个FAQ文件")
        return True
    else:
        print("⚠️  没有找到知识库文件")
        print("💡 系统将使用基础知识库运行")
        return True

def initialize_vectordb():
    """初始化向量数据库"""
    print("🔄 初始化向量数据库...")
    
    vectordb_dir = Path("data/vectordb")
    if vectordb_dir.exists():
        print("✅ 向量数据库已存在")
        return True
    
    print("📊 首次运行，正在构建向量数据库...")
    try:
        from app.rag_engine import RAGEngine
        rag_engine = RAGEngine()
        data_dirs = ["data/knowledge", "data/faq"]
        success = rag_engine.initialize_rag(data_dirs, force_rebuild=True)
        
        if success:
            print("✅ 向量数据库构建完成")
            return True
        else:
            print("⚠️  向量数据库构建失败，将在运行时重试")
            return True
    except Exception as e:
        print(f"⚠️  向量数据库预构建失败: {str(e)}")
        print("💡 系统将在启动时自动构建")
        return True

def start_server():
    """启动服务器"""
    print("🚀 启动BabyCareAI服务器...")
    
    try:
        # Get the current script directory (should be project root)
        project_root = Path(__file__).parent
        config_path = project_root / "config/ollama_config.yaml"
        
        # 加载配置
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        api_config = config.get("api", {})
        host = api_config.get("host", "0.0.0.0")
        port = api_config.get("port", 8000)
        
        print(f"🌐 服务器启动地址: http://localhost:{port}")
        print("📖 API文档: http://localhost:{}/docs".format(port))
        print("🔍 系统状态: http://localhost:{}/api/v1/health".format(port))
        print("\n按 Ctrl+C 停止服务器")
        print("-" * 50)
        
        # 启动服务器 - 使用模块路径而不是直接导入
        import uvicorn
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=False,  # Disable reload to prevent inotify instance limit issues
            log_level="info"
        )
        
    except KeyboardInterrupt:
        print("\n👋 服务器已停止")
    except Exception as e:
        print(f"❌ 服务器启动失败: {str(e)}")
        return False
    
    return True

def main():
    """主函数"""
    print_banner()
    
    # 系统检查
    checks = [
        ("Python版本", check_python_version),
        ("依赖包", check_dependencies),
        ("配置文件", check_config),
        ("知识库", check_knowledge_base),
        ("Ollama服务", check_ollama_service),
    ]
    
    print("🔍 系统检查中...")
    print("-" * 30)
    
    all_passed = True
    for check_name, check_func in checks:
        if not check_func():
            all_passed = False
            break
        time.sleep(0.5)  # 稍微延迟，让输出更清晰
    
    if not all_passed:
        print("\n❌ 系统检查失败，请解决上述问题后重试")
        print("💡 运行 'python test_system.py' 进行详细诊断")
        return
    
    print("\n✅ 系统检查通过！")
    print("-" * 30)
    
    # 初始化向量数据库
    initialize_vectordb()
    
    print("-" * 30)
    
    # 启动服务器
    start_server()

if __name__ == "__main__":
    main()