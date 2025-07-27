#!/usr/bin/env python3
"""
DREAM Business Analysis AI - Dependency Installation Helper
Automated dependency installation and environment setup
"""

import subprocess
import sys
import os
from pathlib import Path

def print_banner():
    """Print installation banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🛠️  DREAM Business Analysis AI                        ║
    ║        Dependency Installation Helper                        ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def check_python_version():
    """Check Python version compatibility"""
    print("🐍 Checking Python version...")
    
    if sys.version_info < (3, 8):
        print(f"❌ Python {sys.version.split()[0]} detected")
        print("   DREAM Business Analysis AI requires Python 3.8 or higher")
        print("   Please upgrade Python and try again")
        return False
    
    print(f"✅ Python {sys.version.split()[0]} is compatible")
    return True

def check_pip():
    """Check if pip is available"""
    print("\n📦 Checking pip availability...")
    
    try:
        result = subprocess.run([sys.executable, "-m", "pip", "--version"], 
                              capture_output=True, text=True, check=True)
        print(f"✅ pip is available: {result.stdout.strip()}")
        return True
    except subprocess.CalledProcessError:
        print("❌ pip is not available")
        print("   Please install pip and try again")
        return False

def upgrade_pip():
    """Upgrade pip to latest version"""
    print("\n⬆️  Upgrading pip...")
    
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "--upgrade", "pip"], 
                      check=True)
        print("✅ pip upgraded successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"⚠️  pip upgrade failed: {e}")
        print("   Continuing with current pip version...")
        return False

def install_requirements():
    """Install requirements from requirements.txt"""
    print("\n📋 Installing dependencies from requirements.txt...")
    
    requirements_file = Path(__file__).parent / "requirements.txt"
    
    if not requirements_file.exists():
        print("❌ requirements.txt not found")
        return False
    
    try:
        # Install requirements
        subprocess.run([
            sys.executable, "-m", "pip", "install", 
            "-r", str(requirements_file)
        ], check=True)
        
        print("✅ All dependencies installed successfully")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Dependency installation failed: {e}")
        print("\n🔧 Troubleshooting tips:")
        print("   1. Check your internet connection")
        print("   2. Try running: pip install --upgrade pip")
        print("   3. Consider using a virtual environment")
        print("   4. On some systems, try: pip3 instead of pip")
        return False

def install_openrouter_dependencies():
    """Install additional dependencies for OpenRouter support"""
    print("\n🌐 Installing OpenRouter Dependencies...")
    
    # List of additional packages needed for OpenRouter
    openrouter_packages = [
        "langchain-openai==0.1.25",
        "python-dotenv==1.0.1"  # Already in requirements but ensure it's installed
    ]
    
    success_count = 0
    
    for package in openrouter_packages:
        print(f"📦 Installing {package}...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", package], check=True)
            print(f"✅ {package} installed successfully")
            success_count += 1
        except subprocess.CalledProcessError:
            print(f"❌ Failed to install {package}")
    
    if success_count == len(openrouter_packages):
        print("🎉 All OpenRouter dependencies installed successfully!")
        
        # Check if .env file exists
        env_file = Path(__file__).parent.parent / ".env"
        if not env_file.exists():
            print("\n⚠️  Creating .env file template...")
            with open(env_file, 'w') as f:
                f.write("OPENROUTER_API_KEY=your_openrouter_api_key_here\n")
            print(f"✅ Created {env_file}")
            print("📝 Please edit the .env file and add your actual OpenRouter API key")
        else:
            print(f"\n✅ .env file already exists at {env_file}")
        
        print("\n🚀 You can now use OpenRouter with:")
        print("   python start_streamlit.py --openrouter")
        
        return True
    else:
        print("❌ Some OpenRouter dependencies failed to install.")
        return False

def verify_installation(include_openrouter=False):
    """Verify that key dependencies are installed correctly"""
    print("\n🔍 Verifying installation...")
    
    key_packages = [
        ("fastapi", "FastAPI web framework"),
        ("uvicorn", "ASGI server"),
        ("langchain", "LangChain framework"),
        ("chromadb", "Vector database"),
        ("sentence_transformers", "Embedding models"),
        ("pydantic", "Data validation"),
        ("yaml", "YAML configuration", "PyYAML"),
        ("requests", "HTTP client"),
        ("numpy", "Numerical computing"),
        ("pandas", "Data analysis")
    ]
    
    # Add OpenRouter packages if requested
    if include_openrouter:
        key_packages.extend([
            ("langchain_openai", "LangChain OpenAI integration"),
            ("dotenv", "Environment variables", "python-dotenv")
        ])
    
    failed_packages = []
    
    for package_info in key_packages:
        if len(package_info) == 3:
            import_name, description, pip_name = package_info
        else:
            import_name, description = package_info
            pip_name = import_name
        
        try:
            if import_name == "yaml":
                import yaml
            else:
                __import__(import_name)
            print(f"✅ {description}")
        except ImportError:
            print(f"❌ {description} - Failed to import {import_name}")
            failed_packages.append(pip_name)
    
    if failed_packages:
        print(f"\n⚠️  Some packages failed to import: {', '.join(failed_packages)}")
        print("   Try reinstalling these packages manually:")
        for package in failed_packages:
            print(f"     pip install {package}")
        return False
    
    print("\n🎉 All key dependencies verified successfully!")
    return True

def create_virtual_environment():
    """Offer to create a virtual environment"""
    print("\n🔒 Virtual Environment Setup")
    
    # Check if already in virtual environment
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Already running in a virtual environment")
        return True
    
    response = input("Would you like to create a virtual environment? (recommended) [y/N]: ")
    
    if response.lower() in ['y', 'yes']:
        venv_path = Path(__file__).parent / "venv"
        
        try:
            print("Creating virtual environment...")
            subprocess.run([sys.executable, "-m", "venv", str(venv_path)], check=True)
            
            # Determine activation script path
            if os.name == 'nt':  # Windows
                activate_script = venv_path / "Scripts" / "activate.bat"
                activate_command = str(activate_script)
            else:  # Unix/Linux/macOS
                activate_script = venv_path / "bin" / "activate"
                activate_command = f"source {activate_script}"
            
            print(f"✅ Virtual environment created at: {venv_path}")
            print(f"\n🔄 To activate the virtual environment, run:")
            print(f"   {activate_command}")
            print(f"\n   Then run this script again to install dependencies")
            
            return False  # Don't continue installation, user needs to activate venv first
            
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to create virtual environment: {e}")
            print("   Continuing with system Python...")
            return True
    
    return True

def check_ollama():
    """Check if Ollama is installed and provide instructions"""
    print("\n🤖 Checking Ollama (LLM Backend)...")
    
    try:
        import requests
        response = requests.get("http://localhost:11434/api/version", timeout=5)
        if response.status_code == 200:
            print("✅ Ollama is running and accessible")
            return True
    except:
        pass
    
    print("⚠️  Ollama is not running or not installed")
    print("\n📖 Ollama Setup Instructions:")
    print("   1. Install Ollama from: https://ollama.ai/")
    print("   2. Start Ollama service: ollama serve")
    print("   3. Pull recommended model: ollama pull qwen2.5:7b")
    print("   4. Verify installation: ollama list")
    print("\n   Note: The system will work without Ollama, but AI analysis features will be disabled")
    
    return False

def show_next_steps(openrouter_installed=False):
    """Show next steps after installation"""
    print("\n🚀 Installation Complete! Next Steps:")
    print("=" * 50)
    
    print("\n1. 🤖 Choose your LLM Backend:")
    if openrouter_installed:
        print("   Option A - OpenRouter (Cloud API):")
        print("     - Edit dream/.env and add your OpenRouter API key")
        print("     - Start with: python start_streamlit.py --openrouter")
        print("   Option B - Ollama (Local):")
    else:
        print("   Ollama (Local):")
    print("     - Install from: https://ollama.ai/")
    print("     - Run: ollama pull qwen2.5:7b")
    print("     - Start with: python start_streamlit.py")
    
    print("\n2. 🗄️  Initialize the knowledge base:")
    print("   python update_knowledge_base.py")
    
    print("\n3. 🧪 Test the system:")
    if openrouter_installed:
        print("   python test_openrouter.py")
    print("   python example_analysis.py")
    
    print("\n4. 🚀 Start the Streamlit application:")
    if openrouter_installed:
        print("   python start_streamlit.py --openrouter  # For OpenRouter")
    print("   python start_streamlit.py                # For Ollama")
    
    print("\n5. 🌐 Access the application:")
    print("   - Streamlit UI: http://localhost:8501")
    
    print("\n💡 Tips:")
    print("   - Use a virtual environment for better isolation")
    print("   - Check the README.md for detailed documentation")
    if openrouter_installed:
        print("   - OpenRouter offers both free and paid models")
        print("   - Free models work well for basic analysis")

def main():
    """Main installation function"""
    print_banner()
    
    # System checks
    if not check_python_version():
        sys.exit(1)
    
    if not check_pip():
        sys.exit(1)
    
    # Virtual environment setup
    if not create_virtual_environment():
        print("\n👋 Please activate your virtual environment and run this script again")
        sys.exit(0)
    
    # Upgrade pip
    upgrade_pip()
    
    # Install dependencies
    if not install_requirements():
        sys.exit(1)
    
    # Ask about OpenRouter installation
    print("\n🌐 LLM Backend Options:")
    print("   1. Ollama (Local) - Free, runs on your machine")
    print("   2. OpenRouter (Cloud API) - Requires API key, includes free models")
    print("   3. Both - Maximum flexibility")
    
    openrouter_installed = False
    choice = input("\nWhich would you like to install? [1/2/3]: ").strip()
    
    if choice in ['2', '3']:
        if install_openrouter_dependencies():
            openrouter_installed = True
        else:
            print("⚠️  OpenRouter installation failed, continuing with Ollama only")
    
    # Verify installation
    if not verify_installation(include_openrouter=openrouter_installed):
        print("\n⚠️  Installation completed with some issues")
        print("   The system may still work, but some features might be limited")
    
    # Check Ollama (unless user chose OpenRouter only)
    if choice != '2':
        check_ollama()
    
    # Show next steps
    show_next_steps(openrouter_installed=openrouter_installed)
    
    print("\n🎉 Setup completed successfully!")
    print("   You're ready to start using DREAM Business Analysis AI!")

if __name__ == "__main__":
    main()