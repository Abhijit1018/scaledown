"""
Client for OpenRouter API.
"""

import json
import requests
from typing import List, Dict, Generator, Any

from pulse.exceptions import InferenceError


class OpenRouterClient:
    """
    Client for interacting with OpenRouter API.
    Handles authentication, model selection, and fallback logic.
    """
    
    BASE_URL = "https://openrouter.ai/api/v1"
    
    def __init__(self, api_key: str, default_model: str, fallback_models: List[str] = None):
        self.api_key = api_key
        self.default_model = default_model
        self.fallback_models = fallback_models or []
        
        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://pulse-ai.local",  # Required by OpenRouter for stats
            "X-Title": "Pulse AI Ecosystem"
        }

    def chat(self, messages: List[Dict[str, str]], model: str = None, **kwargs) -> Dict[str, Any]:
        """
        Send a chat completion request with robust fallback.
        """
        # 1. Try specifically requested model first
        target_model = model or self.default_model
        models_to_try = [target_model]
        
        # 2. Append fallback models (avoiding duplicates)
        for fb in self.fallback_models:
            if fb != target_model:
                models_to_try.append(fb)

        print(f"DEBUG: Attempting models: {models_to_try}")

        last_error = None
        for m in models_to_try:
            try:
                # If we are retrying, print a friendly message
                if m != target_model:
                    print(f"⚠️ Primary model rate-limited/failed. Retrying with: {m}...")
                
                return self._make_request(m, messages, **kwargs)
                
            except InferenceError as e:
                last_error = e
                error_str = str(e).lower()
                print(f"❌ Error with model {m}: {e}")
                
                # Dynamic Self-Healing:
                # Retry on:
                # 1. 429 Rate Limits (temporarily busy)
                # 2. 400/404 Invalid Model (model deprecated or ID changed)
                # 3. 5xx Server Errors (upstream outage)
                should_retry = False
                for indicator in ["429", "rate limit", "temporarily", "400", "404", "not a valid model", "not found"]:
                    if indicator in error_str:
                        should_retry = True
                        break
                
                if should_retry:
                    continue  # Try next model
                else:
                    raise e  # Re-raise other errors (e.g. auth, context length)
        
        # If we exhausted all options
        raise InferenceError(f"All models failed. Last error: {last_error}")

    def _make_request(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Dict[str, Any]:
        """Internal method to execute the API call."""
        payload = {
            "model": model,
            "messages": messages,
        }
        
        # Add optional parameters like 'reasoning', 'temperature', etc.
        for key, value in kwargs.items():
            payload[key] = value
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/chat/completions",
                headers=self.headers,
                json=payload,
                timeout=60
            )
            
            # Check for error responses that are valid JSON but contain error info
            if response.status_code != 200:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('error', {}).get('message', response.text)
                    raise InferenceError(f"API Error {response.status_code}: {error_msg}")
                except json.JSONDecodeError:
                    raise InferenceError(f"HTTP Error {response.status_code}: {response.text}")
            
            data = response.json()
            
            if "choices" not in data or not data["choices"]:
                raise InferenceError("Invalid API response: no choices found")
                
            choice = data["choices"][0]
            message = choice.get("message", {})
            content = message.get("content", "")
            reasoning_details = message.get("reasoning_details")
            
            return {
                "content": content,
                "model": data.get("model", model),
                "usage": data.get("usage", {}),
                "reasoning_details": reasoning_details
            }
            
        except requests.exceptions.Timeout:
             raise InferenceError(f"Request timed out for model {model}")
        except requests.exceptions.RequestException as e:
            raise InferenceError(f"Network error: {str(e)}")

    def stream(self, messages: List[Dict[str, str]], model: str = None, **kwargs) -> Generator[str, None, None]:
        """
        Stream chat completion chunks with robust fallback.
        """
        target_model = model or self.default_model
        models_to_try = [target_model]
        
        # Append fallback models
        for fb in self.fallback_models:
            if fb != target_model:
                models_to_try.append(fb)
        
        last_error = None
        
        for m in models_to_try:
            try:
                if m != target_model:
                     # Yield a system notice if we are switching models mid-stream context
                     # (Though we can't easily yield a 'system notice' as text content without confusing the user, 
                     # we'll just log it for now)
                     print(f"⚠️ Streaming fallback: switching to {m}...")

                # Create the generator
                stream_generator = self._make_stream_request(m, messages, **kwargs)
                
                # Yield from the generator
                # If this raises an exception immediately, we catch it below.
                # If it raises halfway through, the stream breaks (hard to recover mid-stream), 
                # but at least initial connection is protected.
                yield from stream_generator
                return

            except InferenceError as e:
                last_error = e
                error_str = str(e).lower()
                
                # Dynamic Self-Healing for Streams:
                # Catch 429 (Rate Limit), 400 (Invalid Model), 404 (Not Found)
                should_retry = False
                for indicator in ["429", "rate limit", "temporarily", "400", "404", "not a valid model", "not found"]:
                    if indicator in error_str:
                        should_retry = True
                        break

                if should_retry:
                    continue
                else:
                    raise e
                    
        raise InferenceError(f"All streaming models failed. Last error: {last_error}")

    def _make_stream_request(self, model: str, messages: List[Dict[str, str]], **kwargs) -> Generator[str, None, None]:
        """Internal method for streaming request."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            **kwargs
        }
        
        try:
            response = requests.post(
                f"{self.BASE_URL}/chat/completions",
                headers=self.headers,
                json=payload,
                stream=True,
                timeout=60
            )
            
            if response.status_code != 200:
                # Try to get error text
                try:
                    error_json = response.json()
                    error_msg = error_json.get('error', {}).get('message', response.text)
                except:
                    error_msg = response.text
                raise InferenceError(f"API Error {response.status_code}: {error_msg}")
                
            for line in response.iter_lines():
                if line:
                    line = line.decode('utf-8')
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            if "choices" in data and data["choices"]:
                                delta = data["choices"][0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                        except json.JSONDecodeError:
                            continue
                            
        except requests.exceptions.RequestException as e:
            raise InferenceError(f"Stream network error: {str(e)}")
