"""
The Brain: Central Orchestrator for Pulse Ecosystem.
Integrates Memory, ScaleDown, and OpenRouter.
"""

import time
from typing import List, Dict, Generator, Union

from scaledown import ScaleDownCompressor
from scaledown.exceptions import APIError as ScaleDownAPIError

from pulse.config import PulseConfig
from pulse.core.memory import Memory
from pulse.core.openrouter_client import OpenRouterClient
from pulse.exceptions import ConfigurationError, ContextOptimizationError, InferenceError


class Brain:
    """
    The intelligence core of Pulse.
    
    Responsibility:
    1. Manage conversation state via Memory.
    2. Optimize context usage via ScaleDown.
    3. Generate responses via OpenRouter.
    """
    
    def __init__(self, config: PulseConfig):
        self.config = config
        
        # Initialize components
        self.memory = Memory(config.db_path, config.encryption_key)
        
        self.llm = OpenRouterClient(
            api_key=config.openrouter_api_key,
            default_model=config.default_model,
            fallback_models=config.fallback_models
        )
        
        # Initialize ScaleDown if API key is present
        self.compressor = None
        if config.scaledown_api_key:
            import scaledown as sd
            sd.set_api_key(config.scaledown_api_key)
            self.compressor = ScaleDownCompressor(
                target_model="gpt-4o",  # ScaleDown target model for compression
                rate=config.compression_rate
            )
            
        # Skill Registry
        from pulse.skills.system_skills import TimeSkill, SystemInfoSkill
        self.skills = [TimeSkill(), SystemInfoSkill()]

    
    def think(self, user_input: str, system_prompt: str = None) -> str:
        """
        Process user input and return a response (synchronous).
        """
        # 1. Add user message to memory
        self.memory.add("user", user_input)
        
        # 2. Prepare context
        context_messages = self._prepare_context(system_prompt)
        
        # 3. Check for skills
        for skill in self.skills:
            for cmd in skill.commands:
                if cmd.lower() in user_input.lower():
                    print(f"Executing Skill: {skill.name}")
                    result = skill.execute({"user_input": user_input})
                    self.memory.add("assistant", result, metadata={"skill": skill.name})
                    return result
        
        # 4. Call LLM
        start_time = time.time()
        # Enable reasoning for models that support it
        result = self.llm.chat(context_messages, reasoning={"enabled": True})
        latency = (time.time() - start_time) * 1000
        
        response_content = result["content"]
        
        # 4. Save response to memory
        metadata = {
            "model": result.get("model"),
            "latency_ms": latency,
            "usage": result.get("usage"),
            "reasoning_details": result.get("reasoning_details")
        }
        self.memory.add("assistant", response_content, metadata)
        
        return response_content

    def stream_thought(self, user_input: str, system_prompt: str = None) -> Generator[str, None, None]:
        """
        Stream the thought process (response).
        """
        self.memory.add("user", user_input)
        context_messages = self._prepare_context(system_prompt)
        
        full_response = []
        
        try:
            for chunk in self.llm.stream(context_messages):
                full_response.append(chunk)
                yield chunk
        finally:
            # Save full response even if interrupted
            content = "".join(full_response)
            if content:
                self.memory.add("assistant", content)

    def _prepare_context(self, system_prompt: str = None) -> List[Dict[str, str]]:
        """
        Prepare and optimize context for the LLM.
        """
        # Get recent history
        # We fetch enough messages to form a context, usually last 10-20 exchanges
        raw_history = self.memory.get_history(limit=20)
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({"role": "system", "content": "You are Pulse, a helpful, intelligent, and efficient AI assistant."})
        
        # If optimization is disabled or we don't have enough history, return as is
        if not self.config.enable_context_optimization or len(raw_history) < 4 or not self.compressor:
            for msg in raw_history:
                m_dict = {"role": msg.role, "content": msg.content}
                if msg.metadata and "reasoning_details" in msg.metadata:
                    m_dict["reasoning_details"] = msg.metadata["reasoning_details"]
                messages.append(m_dict)
            return messages
        
        # --- Context Optimization Logic ---
        # Strategy: Keep last 2 turns (4 messages) raw, compress the older history
        
        recent_turns = raw_history[-4:] 
        older_turns = raw_history[:-4]
        
        # Convert older turns to a single text block for compression
        older_context_str = "\n".join([f"{m.role.upper()}: {m.content}" for m in older_turns])
        
        # Create a "pseudo-prompt" for the compressor to know what's relevant to the recent conversation
        # Using the last user message as the anchor
        current_query = raw_history[-1].content
        
        try:
            # Compress older context
            compressed = self.compressor.compress(
                context=older_context_str,
                prompt=current_query
            )
            
            # Add compressed summary as a system note or distinct message
            messages.append({
                "role": "system", 
                "content": f"Prior Conversation Summary (Optimized): {compressed.content}"
            })
            
        except ScaleDownAPIError as e:
            # Fallback to raw if compression fails
            print(f"Warning: Context optimization failed ({e}), using raw history.")
            for msg in older_turns:
                messages.append({"role": msg.role, "content": msg.content})
        
        # Append recent raw messages
        for msg in recent_turns:
            messages.append({"role": msg.role, "content": msg.content})
            
        return messages

    def clear_memory(self):
        """Clear conversation history."""
        self.memory.clear()
