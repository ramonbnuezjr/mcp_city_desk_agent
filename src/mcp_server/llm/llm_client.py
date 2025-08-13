import logging
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
import time
import json
from datetime import datetime

from ..config.settings import settings

logger = logging.getLogger(__name__)

class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    async def invoke(self, prompt: str, context: Optional[str] = None, 
                    model_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Invoke the LLM with a prompt and optional context"""
        pass
    
    @abstractmethod
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the model"""
        pass

class OpenAIProvider(LLMProvider):
    """OpenAI GPT-4o-mini provider"""
    
    def __init__(self):
        self.api_key = settings.openai_api_key
        self.model = settings.openai_model
        self.base_url = "https://api.openai.com/v1"
        
    async def invoke(self, prompt: str, context: Optional[str] = None, 
                    model_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Invoke OpenAI API"""
        if not self.api_key:
            raise ValueError("OpenAI API key not configured")
        
        start_time = time.time()
        
        try:
            from openai import AsyncOpenAI
            
            # Initialize OpenAI client
            client = AsyncOpenAI(api_key=self.api_key)
            
            # Build the full prompt with context
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\nQuery: {prompt}"
            
            # Default parameters
            default_params = {
                "model": self.model,
                "messages": [{"role": "user", "content": full_prompt}],
                "max_tokens": 1000,
                "temperature": 0.1
            }
            
            # Override with custom parameters
            if model_params:
                default_params.update(model_params)
            
            # Make API call
            response = await client.chat.completions.create(**default_params)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            result = {
                "provider": "openai",
                "model": self.model,
                "response": response.choices[0].message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens
                },
                "execution_time_ms": execution_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"OpenAI API call successful: {result['usage']['total_tokens']} tokens in {execution_time}ms")
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"OpenAI API call failed: {e}")
            raise Exception(f"OpenAI API error: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get OpenAI model information"""
        return {
            "provider": "openai",
            "model": self.model,
            "context_window": "128k tokens",
            "capabilities": ["text-generation", "chat", "reasoning"],
            "cost_per_1k_tokens": "~$0.01-0.03"
        }

class GoogleGeminiProvider(LLMProvider):
    """Google Gemini 2.5 Pro provider"""
    
    def __init__(self):
        self.api_key = settings.google_gemini_api_key
        self.model = settings.google_gemini_model
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        
    async def invoke(self, prompt: str, context: Optional[str] = None, 
                    model_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Invoke Google Gemini API"""
        if not self.api_key:
            raise ValueError("Google Gemini API key not configured")
        
        start_time = time.time()
        
        try:
            import google.generativeai as genai
            
            # Configure Gemini
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model)
            
            # Build the full prompt with context
            full_prompt = prompt
            if context:
                full_prompt = f"Context: {context}\n\nQuery: {prompt}"
            
            # Default parameters (Gemini-specific)
            generation_config = {
                "temperature": 0.1,
                "max_output_tokens": 1000
            }
            
            # Override with custom parameters
            if model_params:
                generation_config.update(model_params)
            
            # Make API call with generation config
            response = await model.generate_content_async(full_prompt, generation_config=generation_config)
            
            execution_time = int((time.time() - start_time) * 1000)
            
            result = {
                "provider": "google_gemini",
                "model": self.model,
                "response": response.text,
                "usage": {
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0),
                    "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0),
                    "total_tokens": getattr(response.usage_metadata, 'total_token_count', 0)
                },
                "execution_time_ms": execution_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Google Gemini API call successful in {execution_time}ms")
            return result
            
        except Exception as e:
            execution_time = int((time.time() - start_time) * 1000)
            logger.error(f"Google Gemini API call failed: {e}")
            raise Exception(f"Google Gemini API error: {str(e)}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get Google Gemini model information"""
        return {
            "provider": "google_gemini",
            "model": self.model,
            "context_window": "2M tokens",
            "capabilities": ["text-generation", "reasoning", "multimodal"],
            "cost_per_1k_tokens": "~$0.005-0.015"
        }

class LLMClient:
    """Main LLM client with provider management and cost tracking"""
    
    def __init__(self):
        self.providers = {}
        self.usage_stats = {
            "total_calls": 0,
            "total_tokens": 0,
            "total_cost_estimate": 0.0,
            "provider_usage": {}
        }
        
        # Initialize available providers
        self._init_providers()
    
    def _init_providers(self):
        """Initialize available LLM providers"""
        try:
            if settings.openai_api_key:
                self.providers["openai"] = OpenAIProvider()
                self.usage_stats["provider_usage"]["openai"] = {
                    "calls": 0,
                    "tokens": 0,
                    "cost": 0.0
                }
                logger.info("OpenAI provider initialized")
            
            if settings.google_gemini_api_key:
                self.providers["google_gemini"] = GoogleGeminiProvider()
                self.usage_stats["provider_usage"]["google_gemini"] = {
                    "calls": 0,
                    "tokens": 0,
                    "cost": 0.0
                }
                logger.info("Google Gemini provider initialized")
            
            if not self.providers:
                logger.warning("No LLM providers configured")
                
        except Exception as e:
            logger.error(f"Failed to initialize LLM providers: {e}")
    
    async def invoke(self, provider: str, prompt: str, context: Optional[str] = None,
                    model_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Invoke a specific LLM provider"""
        if provider not in self.providers:
            raise ValueError(f"Provider '{provider}' not available. Available: {list(self.providers.keys())}")
        
        try:
            result = await self.providers[provider].invoke(prompt, context, model_params)
            
            # Update usage statistics
            self._update_usage_stats(provider, result)
            
            return result
            
        except Exception as e:
            logger.error(f"LLM invocation failed for {provider}: {e}")
            raise
    
    async def invoke_with_fallback(self, primary_provider: str, prompt: str, 
                                 context: Optional[str] = None,
                                 model_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Invoke with automatic fallback to other providers"""
        providers_to_try = [primary_provider] + [p for p in self.providers.keys() if p != primary_provider]
        
        for provider in providers_to_try:
            try:
                result = await self.invoke(provider, prompt, context, model_params)
                result["fallback_used"] = provider != primary_provider
                return result
            except Exception as e:
                logger.warning(f"Provider {provider} failed, trying next: {e}")
                continue
        
        raise Exception("All LLM providers failed")
    
    async def cross_validate(self, prompt: str, context: Optional[str] = None,
                           model_params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get responses from multiple providers for validation"""
        if len(self.providers) < 2:
            raise ValueError("Need at least 2 providers for cross-validation")
        
        results = {}
        for provider in self.providers.keys():
            try:
                results[provider] = await self.invoke(provider, prompt, context, model_params)
            except Exception as e:
                results[provider] = {"error": str(e)}
        
        return {
            "cross_validation": True,
            "timestamp": datetime.utcnow().isoformat(),
            "results": results,
            "summary": {
                "providers_tested": len(results),
                "successful_responses": len([r for r in results.values() if "error" not in r]),
                "failed_responses": len([r for r in results.values() if "error" in r])
            }
        }
    
    def _update_usage_stats(self, provider: str, result: Dict[str, Any]):
        """Update usage statistics and cost tracking"""
        self.usage_stats["total_calls"] += 1
        self.usage_stats["total_tokens"] += result.get("usage", {}).get("total_tokens", 0)
        
        # Update provider-specific stats
        if provider in self.usage_stats["provider_usage"]:
            self.usage_stats["provider_usage"][provider]["calls"] += 1
            self.usage_stats["provider_usage"][provider]["tokens"] += result.get("usage", {}).get("total_tokens", 0)
            
            # Estimate cost (rough estimates)
            if provider == "openai":
                cost_per_1k = 0.02  # Rough estimate
            elif provider == "google_gemini":
                cost_per_1k = 0.01  # Rough estimate
            else:
                cost_per_1k = 0.01
            
            tokens = result.get("usage", {}).get("total_tokens", 0)
            cost = (tokens / 1000) * cost_per_1k
            
            self.usage_stats["provider_usage"][provider]["cost"] += cost
            self.usage_stats["total_cost_estimate"] += cost
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get current usage statistics"""
        return self.usage_stats.copy()
    
    def get_available_providers(self) -> List[str]:
        """Get list of available providers"""
        return list(self.providers.keys())
    
    def get_provider_info(self, provider: str) -> Optional[Dict[str, Any]]:
        """Get information about a specific provider"""
        if provider in self.providers:
            return self.providers[provider].get_model_info()
        return None

# Global LLM client instance
llm_client = LLMClient()
