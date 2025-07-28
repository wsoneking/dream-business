"""
DREAM Business Analysis AI - LLM Provider
Unified LLM provider that supports both Ollama and OpenRouter
"""

import os
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_core.language_models.base import BaseLanguageModel
import logging
import streamlit as st

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class LLMProvider:
    """Unified LLM provider supporting both Ollama and OpenRouter"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.llm = None
        self.provider_type = None
        self._initialize_llm()
    
    def _initialize_llm(self):
        """Initialize the appropriate LLM based on environment variables or Streamlit secrets"""
        # Try to get provider from Streamlit secrets first, then environment variables
        provider = self._get_secret_or_env("LLM_PROVIDER", "openrouter").lower()
        
        if provider == "openrouter":
            self._initialize_openrouter()
        else:
            # For cloud deployment, we'll default to OpenRouter
            logger.warning("⚠️ Ollama not supported in cloud deployment, falling back to OpenRouter")
            self._initialize_openrouter()
    
    def _get_secret_or_env(self, key: str, default: str = None) -> str:
        """Get value from Streamlit secrets or environment variables"""
        try:
            # Try Streamlit secrets first
            if hasattr(st, 'secrets') and key in st.secrets.get("llm", {}):
                return st.secrets["llm"][key]
        except Exception:
            pass
        
        # Fall back to environment variables
        return os.getenv(key, default)
    
    def _initialize_openrouter(self):
        """Initialize OpenRouter LLM"""
        try:
            api_key = self._get_secret_or_env("OPENROUTER_API_KEY")
            model = self._get_secret_or_env("OPENROUTER_MODEL", "qwen/qwen3-14b:free")
            
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY is required. Please set it in Streamlit secrets or environment variables.")
            
            logger.info(f"🔄 Initializing OpenRouter with model: {model}")
            
            self.llm = ChatOpenAI(
                model=model,
                openai_api_key=api_key,
                openai_api_base="https://openrouter.ai/api/v1",
                temperature=self.config["ollama"]["temperature"],
                max_tokens=self.config["ollama"]["max_tokens"],
                timeout=self.config["ollama"]["timeout"],
                default_headers={
                    "HTTP-Referer": "https://github.com/dream-business-analysis",
                    "X-Title": "DREAM Business Analysis AI"
                }
            )
            self.provider_type = "openrouter"
            logger.info(f"✅ OpenRouter LLM initialized with model: {model}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenRouter LLM: {e}")
            raise
    
    def invoke(self, prompt: str) -> str:
        """Invoke the LLM with a prompt"""
        try:
            logger.info(f"🔄 Invoking {self.provider_type} LLM with prompt length: {len(prompt)}")
            
            # For ChatOpenAI (OpenRouter), we need to format the prompt as messages
            from langchain_core.messages import HumanMessage
            
            messages = [HumanMessage(content=prompt)]
            logger.info(f"📤 Sending request to OpenRouter...")
            
            response = self.llm.invoke(messages)
            logger.info(f"📥 Received response from OpenRouter")
            
            result = response.content if hasattr(response, 'content') else str(response)
            
            if not result:
                logger.warning(f"⚠️ Empty response received from OpenRouter")
                logger.info(f"🔍 Full response object: {response}")
                return "Error: Empty response from OpenRouter API"
            
            logger.info(f"✅ Response received, length: {len(result)}")
            return result
        except Exception as e:
            logger.error(f"❌ LLM invocation failed: {e}")
            logger.error(f"❌ Exception type: {type(e)}")
            raise
    
    
    async def ainvoke(self, prompt: str) -> str:
        """Async invoke the LLM with a prompt"""
        try:
            logger.info(f"🔄 Async invoking {self.provider_type} LLM with prompt length: {len(prompt)}")
            
            # For ChatOpenAI (OpenRouter), we need to format the prompt as messages
            from langchain_core.messages import HumanMessage
            
            messages = [HumanMessage(content=prompt)]
            logger.info(f"📤 Sending async request to OpenRouter...")
            
            response = await self.llm.ainvoke(messages)
            logger.info(f"📥 Received async response from OpenRouter")
            
            result = response.content if hasattr(response, 'content') else str(response)
            
            if not result:
                logger.warning(f"⚠️ Empty async response received from OpenRouter")
                logger.info(f"🔍 Full response object: {response}")
                return "Error: Empty response from OpenRouter API"
            
            logger.info(f"✅ Async response received, length: {len(result)}")
            return result
        except Exception as e:
            logger.error(f"❌ Async LLM invocation failed: {e}")
            logger.error(f"❌ Exception type: {type(e)}")
            raise
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider"""
        return {
            "provider": "OpenRouter",
            "model": self._get_secret_or_env("OPENROUTER_MODEL", "qwen/qwen3-14b:free"),
            "type": "API"
        }