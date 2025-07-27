#!/usr/bin/env python3
"""
DREAM Business Analysis AI - Streamlit Launcher
Simple launcher script for the Streamlit UI
"""

import subprocess
import sys
import os
from pathlib import Path

def main():
    """Launch the Streamlit application"""
    
    print("🎯 DREAM Business Analysis AI - Streamlit UI")
    print("=" * 60)
    
    # Get the current directory
    current_dir = Path(__file__).parent
    streamlit_app = current_dir / "streamlit_app.py"
    
    # Check if streamlit_app.py exists
    if not streamlit_app.exists():
        print("❌ Error: streamlit_app.py not found!")
        sys.exit(1)
    
    # Set environment variables
    os.environ["PYTHONPATH"] = str(current_dir)
    
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