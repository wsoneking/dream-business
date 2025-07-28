#!/usr/bin/env python3
"""
BabyCareAI - Dependency Installation Script
Installs all required dependencies with proper error handling
"""

import subprocess
import sys
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_command(command, description):
    """Run a command with error handling"""
    logger.info(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ {description} completed successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False

def main():
    """Main installation process"""
    logger.info("🚀 Starting BabyCareAI dependency installation...")
    
    # Upgrade pip first
    if not run_command(f"{sys.executable} -m pip install --upgrade pip", "Upgrading pip"):
        logger.error("Failed to upgrade pip, continuing anyway...")
    
    # Install dependencies from requirements.txt
    if not run_command(f"{sys.executable} -m pip install -r requirements.txt", "Installing dependencies"):
        logger.error("❌ Failed to install dependencies from requirements.txt")
        return False
    
    # Verify critical imports
    logger.info("🔍 Verifying critical imports...")
    
    critical_imports = [
        ("streamlit", "Streamlit web framework"),
        ("langchain", "LangChain framework"),
        ("chromadb", "ChromaDB vector database"),
        ("sentence_transformers", "Sentence transformers for embeddings"),
        ("yaml", "YAML configuration parser")
    ]
    
    failed_imports = []
    for module, description in critical_imports:
        try:
            __import__(module)
            logger.info(f"✅ {description} imported successfully")
        except ImportError as e:
            logger.error(f"❌ Failed to import {module}: {e}")
            failed_imports.append(module)
    
    if failed_imports:
        logger.error(f"❌ Failed to import critical modules: {failed_imports}")
        logger.info("🔄 Attempting to install failed modules individually...")
        
        for module in failed_imports:
            if module == "yaml":
                module = "PyYAML"
            run_command(f"{sys.executable} -m pip install --upgrade {module}", f"Installing {module}")
    
    # Create necessary directories
    logger.info("📁 Creating necessary directories...")
    directories = [
        "data/vectordb",
        "data/knowledge",
        "data/faq",
        "config"
    ]
    
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        logger.info(f"✅ Directory created/verified: {directory}")
    
    logger.info("🎉 Installation completed!")
    logger.info("🚀 You can now run the application with: streamlit run streamlit_app.py")

if __name__ == "__main__":
    main()