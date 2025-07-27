"""
DREAM Business Analysis AI - LLM Provider
Unified LLM provider that supports both Ollama and OpenRouter
"""

import os
from typing import Dict, Any, Optional
from langchain_ollama import OllamaLLM
from langchain_openai import ChatOpenAI
from langchain_core.language_models.base import BaseLanguageModel
import logging

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
        """Initialize the appropriate LLM based on environment variables"""
        provider = os.getenv("LLM_PROVIDER", "ollama").lower()
        
        if provider == "openrouter":
            self._initialize_openrouter()
        else:
            self._initialize_ollama()
    
    def _initialize_ollama(self):
        """Initialize Ollama LLM"""
        try:
            self.llm = OllamaLLM(
                base_url=self.config["ollama"]["base_url"],
                model=self.config["ollama"]["model"],
                temperature=self.config["ollama"]["temperature"],
                num_predict=self.config["ollama"]["max_tokens"],
                timeout=self.config["ollama"]["timeout"]
            )
            self.provider_type = "ollama"
            logger.info(f"✅ Ollama LLM initialized with model: {self.config['ollama']['model']}")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Ollama LLM: {e}")
            raise
    
    def _initialize_openrouter(self):
        """Initialize OpenRouter LLM"""
        try:
            api_key = os.getenv("OPENROUTER_API_KEY")
            # Use a more reliable free model
            model = os.getenv("OPENROUTER_MODEL", "meta-llama/llama-3.1-8b-instruct:free")
            
            if not api_key:
                raise ValueError("OPENROUTER_API_KEY environment variable is required")
            
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
            
            if self.provider_type == "openrouter":
                # For ChatOpenAI, we need to format the prompt as messages
                from langchain_core.messages import HumanMessage
                
                messages = [HumanMessage(content=prompt)]
                logger.info(f"📤 Sending request to OpenRouter...")
                
                response = self.llm.invoke(messages)
                logger.info(f"📥 Received response from OpenRouter")
                
                # Debug response structure
                # logger.info(f"🔍 Response type: {type(response)}")
                # logger.info(f"🔍 Response attributes: {dir(response)}")
                
                result = response.content if hasattr(response, 'content') else str(response)
                
                if not result:
                    logger.warning(f"⚠️ Empty response received from OpenRouter")
                    logger.info(f"🔍 Full response object: {response}")
                    return "Error: Empty response from OpenRouter API"
                
                logger.info(f"✅ Response received, length: {len(result)}")
                return result
            else:
                # For Ollama, direct string invocation
                result = self.llm.invoke(prompt)
                logger.info(f"✅ Ollama response received, length: {len(result)}")
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
                # For ChatOpenAI, we need to format the prompt as messages
                from langchain_core.messages import HumanMessage
                
                messages = [HumanMessage(content=prompt)]
                logger.info(f"📤 Sending async request to OpenRouter...")
                
                response = await self.llm.ainvoke(messages)
                logger.info(f"📥 Received async response from OpenRouter")
                
                # Debug response structure
                logger.info(f"🔍 Response type: {type(response)}")
                
                result = response.content if hasattr(response, 'content') else str(response)
                
                if not result:
                    logger.warning(f"⚠️ Empty async response received from OpenRouter")
                    logger.info(f"🔍 Full response object: {response}")
                    return "Error: Empty response from OpenRouter API"
                
                logger.info(f"✅ Async response received, length: {len(result)}")
                return result
            else:
                # For Ollama, direct string invocation
                result = await self.llm.ainvoke(prompt)
                logger.info(f"✅ Ollama async response received, length: {len(result)}")
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
                "model": os.getenv("OPENROUTER_MODEL", "qwen/qwen3-235b-a22b-2507:free"),
                "type": "API"
            }
        else:
            return {
                "provider": "Ollama",
                "model": self.config["ollama"]["model"],
                "type": "Local"
            }