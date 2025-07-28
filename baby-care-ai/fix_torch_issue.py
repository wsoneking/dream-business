#!/usr/bin/env python3
"""
Fix PyTorch compatibility issues
This script addresses the torch.classes error that can occur with certain PyTorch versions
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a command and return success status"""
    try:
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Success: {command}")
            return True
        else:
            print(f"❌ Failed: {command}")
            print(f"Error: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Exception running {command}: {e}")
        return False

def check_torch_installation():
    """Check current PyTorch installation"""
    try:
        import torch
        print(f"Current PyTorch version: {torch.__version__}")
        
        # Test for the specific error
        try:
            # This is a common operation that triggers the torch.classes error
            from sentence_transformers import SentenceTransformer
            model = SentenceTransformer('all-MiniLM-L6-v2')
            print("✅ SentenceTransformers working correctly")
            return True
        except Exception as e:
            if "torch.classes" in str(e) or "__path__._path" in str(e):
                print(f"❌ Detected torch.classes error: {e}")
                return False
            else:
                print(f"⚠️ Other error: {e}")
                return False
    except ImportError:
        print("❌ PyTorch not installed")
        return False

def fix_torch_installation():
    """Fix PyTorch installation"""
    print("🔧 Attempting to fix PyTorch installation...")
    
    # Strategy 1: Reinstall PyTorch with specific version
    commands = [
        "pip uninstall torch torchvision torchaudio -y",
        "pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0 --index-url https://download.pytorch.org/whl/cpu",
        "pip install sentence-transformers --upgrade"
    ]
    
    for cmd in commands:
        print(f"Running: {cmd}")
        if not run_command(cmd):
            print(f"Failed to execute: {cmd}")
            return False
    
    return True

def alternative_fix():
    """Alternative fix using conda if available"""
    print("🔧 Trying alternative fix with conda...")
    
    commands = [
        "conda install pytorch torchvision torchaudio cpuonly -c pytorch -y",
        "pip install sentence-transformers --upgrade"
    ]
    
    for cmd in commands:
        print(f"Running: {cmd}")
        if not run_command(cmd):
            print(f"Failed to execute: {cmd}")
            continue
    
    return check_torch_installation()

def main():
    print("🔍 Checking PyTorch installation...")
    
    if check_torch_installation():
        print("✅ PyTorch is working correctly!")
        return
    
    print("🔧 PyTorch needs fixing...")
    
    # Try pip fix first
    if fix_torch_installation():
        if check_torch_installation():
            print("✅ PyTorch fixed successfully!")
            return
    
    # Try conda fix as alternative
    print("🔄 Trying alternative fix...")
    if alternative_fix():
        print("✅ PyTorch fixed with alternative method!")
        return
    
    print("❌ Could not fix PyTorch automatically.")
    print("💡 Manual steps:")
    print("1. Uninstall current PyTorch: pip uninstall torch torchvision torchaudio")
    print("2. Install stable version: pip install torch==2.1.0 torchvision==0.16.0 torchaudio==2.1.0")
    print("3. Reinstall sentence-transformers: pip install sentence-transformers --upgrade")

if __name__ == "__main__":
    main()