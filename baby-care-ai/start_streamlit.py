#!/usr/bin/env python3
"""
BabyCareAI Streamlit启动脚本
Simple startup script for BabyCareAI Streamlit app
"""

import os
import sys
import subprocess
from pathlib import Path

def print_banner():
    """打印启动横幅"""
    banner = """
🍼 BabyCareAI Streamlit App
============================
专业、温暖的AI育儿助手
Professional & Caring AI Parenting Assistant
============================
"""
    print(banner)

def check_dependencies():
    """检查依赖包"""
    print("📦 检查依赖包...")
    
    required_packages = [
        "streamlit",
        "langchain",
        "langchain-openai",
        "chromadb",
        "sentence-transformers"
    ]
    
    missing = []
    for package in required_packages:
        try:
            __import__(package.replace("-", "_"))
        except ImportError:
            missing.append(package)
    
    if missing:
        print(f"❌ 缺少依赖包: {', '.join(missing)}")
        print("💡 安装依赖: pip install -r requirements.txt")
        return False
    
    print("✅ 所有依赖包已安装")
    return True

def check_config():
    """检查配置"""
    print("⚙️ 检查配置...")
    
    # Check if config files exist
    config_files = [
        "config/ollama_config.yaml",
        "config/custom_prompt.txt"
    ]
    
    for config_file in config_files:
        if not os.path.exists(config_file):
            print(f"⚠️ 配置文件不存在: {config_file}")
    
    # Check LLM provider configuration
    provider = os.getenv("LLM_PROVIDER", "openrouter")
    print(f"🤖 LLM提供商: {provider}")
    
    if provider == "openrouter":
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            print("⚠️ 未设置 OPENROUTER_API_KEY")
            print("💡 请设置环境变量或在 Streamlit secrets 中配置")
        else:
            print("✅ OpenRouter API Key 已配置")
    
    return True

def start_streamlit():
    """启动Streamlit应用"""
    print("🚀 启动 BabyCareAI Streamlit 应用...")
    
    try:
        # Set default port
        port = os.getenv("STREAMLIT_PORT", "8501")
        
        print(f"🌐 应用将在以下地址启动:")
        print(f"   本地访问: http://localhost:{port}")
        print(f"   网络访问: http://0.0.0.0:{port}")
        print("\n按 Ctrl+C 停止应用")
        print("-" * 50)
        
        # Start Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", "streamlit_app.py",
            "--server.port", port,
            "--server.address", "0.0.0.0",
            "--server.headless", "true"
        ]
        
        subprocess.run(cmd)
        
    except KeyboardInterrupt:
        print("\n👋 应用已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")

def main():
    """主函数"""
    print_banner()
    
    # 检查依赖
    if not check_dependencies():
        return
    
    # 检查配置
    check_config()
    
    print("-" * 30)
    
    # 启动应用
    start_streamlit()

if __name__ == "__main__":
    main()