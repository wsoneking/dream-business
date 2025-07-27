#!/usr/bin/env python3
"""
Test script to debug OpenRouter API connection
"""

import os
import sys
import yaml
import logging
from pathlib import Path

# Add the app directory to the path
sys.path.append(str(Path(__file__).parent / "app"))

from llm_provider import LLMProvider

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def load_config():
    """Load configuration from YAML file"""
    config_path = Path(__file__).parent / "config" / "ollama_config.yaml"
    with open(config_path, 'r') as f:
        return yaml.safe_load(f)

def test_openrouter():
    """Test OpenRouter API connection"""
    try:
        # Load environment variables
        from dotenv import load_dotenv
        load_dotenv(Path(__file__).parent.parent / ".env")
        
        logger.info("🔄 Loading configuration...")
        config = load_config()
        
        logger.info("🔄 Initializing LLM Provider...")
        llm_provider = LLMProvider(config)
        
        # Get provider info
        provider_info = llm_provider.get_provider_info()
        logger.info(f"📋 Provider Info: {provider_info}")
        
        # Test with a simple prompt
        test_prompt = "Hello! Please respond with 'OpenRouter is working correctly' if you can see this message."
        
        logger.info("🔄 Testing simple prompt...")
        logger.info(f"📤 Prompt: {test_prompt}")
        
        response = llm_provider.invoke(test_prompt)
        
        logger.info(f"📥 Response: {response}")
        logger.info(f"📏 Response length: {len(response)}")
        
        if response and len(response) > 0:
            logger.info("✅ OpenRouter is working correctly!")
        else:
            logger.error("❌ OpenRouter returned empty response")
            
        return response
        
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        logger.error(f"❌ Exception type: {type(e)}")
        import traceback
        logger.error(f"❌ Traceback: {traceback.format_exc()}")
        return None

if __name__ == "__main__":
    print("🧪 Testing OpenRouter API Connection...")
    print("=" * 50)
    
    result = test_openrouter()
    
    print("=" * 50)
    if result:
        print("✅ Test completed successfully!")
        print(f"Response: {result}")
    else:
        print("❌ Test failed!")