#!/usr/bin/env python3
"""
Test script to verify deployment readiness for Streamlit Community Cloud
"""

import sys
import os
from pathlib import Path
import importlib.util

def test_imports():
    """Test that all required packages can be imported"""
    print("🔍 Testing package imports...")
    
    required_packages = [
        'streamlit',
        'langchain',
        'langchain_openai',
        'chromadb',
        'sentence_transformers',
        'plotly',
        'pandas',
        'numpy',
        'yaml',
        'streamlit_option_menu'
    ]
    
    failed_imports = []
    
    for package in required_packages:
        try:
            __import__(package)
            print(f"  ✅ {package}")
        except ImportError as e:
            print(f"  ❌ {package}: {e}")
            failed_imports.append(package)
    
    if failed_imports:
        print(f"\n❌ Failed to import: {', '.join(failed_imports)}")
        print("💡 Run: pip install -r requirements.txt")
        return False
    else:
        print("\n✅ All required packages imported successfully!")
        return True

def test_file_structure():
    """Test that all required files exist"""
    print("\n🔍 Testing file structure...")
    
    required_files = [
        'streamlit_app.py',
        'requirements.txt',
        'config/ollama_config.yaml',
        '.streamlit/config.toml',
        '.streamlit/secrets.toml',
        'DEPLOYMENT.md',
        '.gitignore'
    ]
    
    missing_files = []
    current_dir = Path(__file__).parent
    
    for file_path in required_files:
        full_path = current_dir / file_path
        if full_path.exists():
            print(f"  ✅ {file_path}")
        else:
            print(f"  ❌ {file_path}")
            missing_files.append(file_path)
    
    if missing_files:
        print(f"\n❌ Missing files: {', '.join(missing_files)}")
        return False
    else:
        print("\n✅ All required files present!")
        return True

def test_app_modules():
    """Test that app modules can be imported"""
    print("\n🔍 Testing app modules...")
    
    app_modules = [
        'app.llm_provider',
        'app.business_analyzer',
        'app.rag_engine'
    ]
    
    failed_modules = []
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))
    
    for module in app_modules:
        try:
            __import__(module)
            print(f"  ✅ {module}")
        except ImportError as e:
            print(f"  ❌ {module}: {e}")
            failed_modules.append(module)
    
    if failed_modules:
        print(f"\n❌ Failed to import modules: {', '.join(failed_modules)}")
        return False
    else:
        print("\n✅ All app modules imported successfully!")
        return True

def test_secrets_template():
    """Test that secrets template is properly configured"""
    print("\n🔍 Testing secrets configuration...")
    
    secrets_file = Path(__file__).parent / '.streamlit' / 'secrets.toml'
    
    if not secrets_file.exists():
        print("  ❌ secrets.toml template not found")
        return False
    
    try:
        with open(secrets_file, 'r') as f:
            content = f.read()
        
        required_keys = ['OPENROUTER_API_KEY', 'LLM_PROVIDER', 'OPENROUTER_MODEL']
        
        for key in required_keys:
            if key in content:
                print(f"  ✅ {key} template found")
            else:
                print(f"  ❌ {key} template missing")
                return False
        
        if 'your_openrouter_api_key_here' in content:
            print("  ⚠️  Remember to replace placeholder API key with real key in Streamlit Cloud")
        
        print("\n✅ Secrets template properly configured!")
        return True
        
    except Exception as e:
        print(f"  ❌ Error reading secrets template: {e}")
        return False

def main():
    """Run all deployment tests"""
    print("🚀 DREAM Business Analysis AI - Deployment Test")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_file_structure,
        test_app_modules,
        test_secrets_template
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        if test():
            passed += 1
        print()
    
    print("=" * 60)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Your app is ready for Streamlit Community Cloud deployment.")
        print("\n📋 Next steps:")
        print("1. Push your code to GitHub")
        print("2. Follow the deployment guide in DEPLOYMENT.md")
        print("3. Configure secrets in Streamlit Cloud dashboard")
        return True
    else:
        print("❌ Some tests failed. Please fix the issues before deploying.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)