"""
BabyCareAI - LLM Provider
Unified LLM provider that supports both Ollama and OpenRouter
"""

import os
from typing import Dict, Any, Optional
from langchain_openai import ChatOpenAI
from langchain_ollama import OllamaLLM
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
        elif provider == "ollama":
            self._initialize_ollama()
        else:
            # For cloud deployment, we'll default to OpenRouter
            logger.warning("⚠️ Unknown provider, falling back to OpenRouter")
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
                    "HTTP-Referer": "https://github.com/baby-care-ai",
                    "X-Title": "BabyCareAI"
                }
            )
            self.provider_type = "openrouter"
            logger.info(f"✅ OpenRouter LLM initialized with model: {model}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize OpenRouter LLM: {e}")
            raise
    
    def _initialize_ollama(self):
        """Initialize Ollama LLM"""
        try:
            ollama_config = self.config['ollama']
            logger.info(f"🔄 Initializing Ollama with model: {ollama_config['model']}")
            
            llm_params = {
                'base_url': ollama_config['base_url'],
                'model': ollama_config['model'],
                'temperature': ollama_config['temperature'],
                'num_predict': ollama_config['max_tokens'],
                'timeout': ollama_config['timeout']
            }
            
            # Add system parameter if available
            if 'system' in ollama_config:
                llm_params['system'] = ollama_config['system']
                
            self.llm = OllamaLLM(**llm_params)
            self.provider_type = "ollama"
            logger.info(f"✅ Ollama LLM initialized with model: {ollama_config['model']}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Ollama LLM: {e}")
            raise
    
    def invoke(self, prompt: str) -> str:
        """Invoke the LLM with a prompt"""
        try:
            logger.info(f"🔄 Invoking {self.provider_type} LLM with prompt length: {len(prompt)}")
            
            if self.provider_type == "openrouter":
                # For ChatOpenAI (OpenRouter), we need to format the prompt as messages
                from langchain_core.messages import HumanMessage
                
                messages = [HumanMessage(content=prompt)]
                logger.info(f"📤 Sending request to OpenRouter...")
                
                response = self.llm.invoke(messages)
                logger.info(f"📥 Received response from OpenRouter")
                
                result = response.content if hasattr(response, 'content') else str(response)
            else:
                # For Ollama, direct string invocation
                logger.info(f"📤 Sending request to Ollama...")
                response = self.llm.invoke(prompt)
                result = response
            
            if not result:
                logger.warning(f"⚠️ Empty response received from {self.provider_type}")
                logger.info(f"🔍 Full response object: {response}")
                return f"Error: Empty response from {self.provider_type} API"
            
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
            
            if self.provider_type == "openrouter":
                # For ChatOpenAI (OpenRouter), we need to format the prompt as messages
                from langchain_core.messages import HumanMessage
                
                messages = [HumanMessage(content=prompt)]
                logger.info(f"📤 Sending async request to OpenRouter...")
                
                response = await self.llm.ainvoke(messages)
                logger.info(f"📥 Received async response from OpenRouter")
                
                result = response.content if hasattr(response, 'content') else str(response)
            else:
                # For Ollama, direct string invocation
                logger.info(f"📤 Sending async request to Ollama...")
                response = await self.llm.ainvoke(prompt)
                result = response
            
            if not result:
                logger.warning(f"⚠️ Empty async response received from {self.provider_type}")
                logger.info(f"🔍 Full response object: {response}")
                return f"Error: Empty response from {self.provider_type} API"
            
            logger.info(f"✅ Async response received, length: {len(result)}")
            return result
        except Exception as e:
            logger.error(f"❌ Async LLM invocation failed: {e}")
            logger.error(f"❌ Exception type: {type(e)}")
            raise
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get information about the current provider"""
        if self.provider_type == "openrouter":
            return {
                "provider": "OpenRouter",
                "model": self._get_secret_or_env("OPENROUTER_MODEL", "qwen/qwen3-14b:free"),
                "type": "API"
            }
        else:
            return {
                "provider": "Ollama",
                "model": self.config["ollama"]["model"],
                "type": "Local"
            }