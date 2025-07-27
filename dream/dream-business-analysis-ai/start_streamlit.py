#!/usr/bin/env python3
"""
DREAM Business Analysis AI - Streamlit Launcher
Simple launcher script for the Streamlit UI
"""

import subprocess
import sys
import os
import argparse
from pathlib import Path

def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(description="DREAM Business Analysis AI - Streamlit Launcher")
    parser.add_argument(
        "--openrouter",
        action="store_true",
        help="Use OpenRouter API with default model (qwen/qwen3-14b:free)"
    )
    parser.add_argument(
        "--model",
        type=str,
        default="qwen/qwen3-14b:free",
        help="Specify OpenRouter model to use (only when --openrouter is used)"
    )
    return parser.parse_args()

def main():
    """Launch the Streamlit application"""
    
    print("🎯 DREAM Business Analysis AI - Streamlit UI")
    print("=" * 60)
    
    # Parse command line arguments
    args = parse_arguments()
    
    # Get the current directory
    current_dir = Path(__file__).parent
    streamlit_app = current_dir / "streamlit_app.py"
    
    # Check if streamlit_app.py exists
    if not streamlit_app.exists():
        print("❌ Error: streamlit_app.py not found!")
        sys.exit(1)
    
    # Set environment variables
    os.environ["PYTHONPATH"] = str(current_dir)
    
    # Set LLM provider based on arguments
    if args.openrouter:
        os.environ["LLM_PROVIDER"] = "openrouter"
        os.environ["OPENROUTER_MODEL"] = args.model
        print(f"🌐 Using OpenRouter API with model: {args.model}")
        
        # Load environment variables from .env file
        env_file = current_dir.parent / ".env"
        if env_file.exists():
            from dotenv import load_dotenv
            load_dotenv(env_file)
            if not os.getenv("OPENROUTER_API_KEY"):
                print("❌ Error: OPENROUTER_API_KEY not found in .env file!")
                sys.exit(1)
        else:
            print("❌ Error: .env file not found!")
            sys.exit(1)
    else:
        os.environ["LLM_PROVIDER"] = "ollama"
        print("🏠 Using local Ollama")
    
    print("🚀 Starting Streamlit application...")
    print("📱 Open your browser and go to: http://localhost:8501")
    print("⏹️  Press Ctrl+C to stop the application")
    print("-" * 60)
    
    try:
        # Launch Streamlit
        subprocess.run([
            sys.executable, "-m", "streamlit", "run",
            str(streamlit_app),
            "--server.port=8501",
            "--server.address=localhost",
            "--browser.gatherUsageStats=false"
        ], cwd=current_dir)
        
    except KeyboardInterrupt:
        print("\n🛑 Streamlit application stopped by user")
    except Exception as e:
        print(f"❌ Error starting Streamlit: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()