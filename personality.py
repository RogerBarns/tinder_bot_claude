"""
AI-powered message generation with personality
"""
import re
import json
import time
import random
from typing import List, Dict, Optional
from datetime import datetime
from zoneinfo import ZoneInfo

import requests

from config import CLAUDE_API_KEY, PERSONALITIES, CLAUDE_USAGE_FILE
from utils.logger import get_logger

logger = get_logger(__name__)


class MessageGenerator:
    """Generates human-like messages using Claude AI"""
    
    def __init__(self):
        self.api_key = CLAUDE_API_KEY
        self.api_url = "https://api.anthropic.com/v1/messages"
        self.refusal_patterns = [
            r"i do not feel comfortable",
            r"i'm sorry",
            r"unable to",
            r"cannot continue",
            r"i do not actually have the ability",
            r"i should have been more direct",
            r"i do not engage in roleplay",
            r"i'm not actually a real person",
            r"i cannot send real messages",
            r"i cannot make real phone calls",
            r"i am an ai program",
            r"as an ai",
            r"language model"
        ]
    
    def generate_reply(
        self,
        name: str,
        bio: str = "",
        chat_history: List[Dict] = None,
        personality: str = "default"
    ) -> str:
        """Generate a contextual reply"""
        chat_history = chat_history or []
        
        # Get personality prompt
        prompt_template = PERSONALITIES.get(personality, PERSONALITIES["default"])
        
        # Inject current time into prompt
        system_prompt = self._render_time_aware_prompt(
            prompt_template.get("system_prompt", prompt_template)
        )
        
        # Build messages for Claude
        messages = self._build_messages(name, bio, chat_history)
        
        # Make API call with retries
        max_retries = 3
        for attempt in range(max_retries):
            try:
                reply = self._call_claude(system_prompt, messages)
                
                # Check for refusal
                if self._is_refusal(reply):
                    logger.warning(f"Claude refused, retrying with flirty personality")
                    # Retry with more direct personality
                    system_prompt = self._render_time_aware_prompt(
                        PERSONALITIES["flirty"].get("system_prompt", PERSONALITIES["flirty"])
                    )
                    reply = self._call_claude(system_prompt, messages)
                    
                    if self._is_refusal(reply):
                        # Generate fallback
                        reply = self._generate_fallback(name)
                
                # Clean and validate reply
                reply = self._sanitize_reply(reply)
                
                return reply
                
            except Exception as e:
                logger.error(f"Generation attempt {attempt + 1} failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
        
        # Final fallback
        return self._generate_fallback(name)
    
    def _render_time_aware_prompt(self, template: str) -> str:
        """Inject current date/time into prompt"""
        if isinstance(template, dict):
            template = template.get("system_prompt", "")
        
        now = datetime.now(ZoneInfo("Europe/London"))
        
        return template.format(
            current_date=now.strftime("%B %d, %Y"),
            current_time=now.strftime("%H:%M")
        )
    
    def _build_messages(
        self, 
        name: str, 
        bio: str, 
        chat_history: List[Dict]
    ) -> List[Dict]:
        """Build message history for Claude"""
        messages = []
        
        # Add chat history
        if chat_history:
            # Limit to recent messages
            recent_history = chat_history[-10:]
            messages.extend(recent_history)
        
        # If it's a first message
        if not messages or len(messages) <= 2:
            opener_prompt = {
                "role": "user",
                "content": (
                    f"You matched with {name}. "
                    f"{'Their bio says: ' + bio if bio else 'No bio provided.'}. "
                    "Write a flirty, engaging opening message that will get a response."
                )
            }
            messages.append(opener_prompt)
        
        # Handle media mentions
        if messages and any(word in messages[-1].get("content", "").lower() 
                          for word in ["gif", "image", "photo", "picture", "selfie"]):
            messages.append({
                "role": "user",
                "content": f"{name} just sent a photo/GIF. Respond flirtatiously about it."
            })
        
        return messages
    
    def _call_claude(self, system_prompt: str, messages: List[Dict]) -> str:
        """Make API call to Claude"""
        headers = {
            "x-api-key": self.api_key,
            "content-type": "application/json",
            "anthropic-version": "2023-06-01"
        }
        
        payload = {
            "model": "claude-3-5-sonnet-20241022",
            "max_tokens": 300,
            "temperature": 0.7,
            "system": system_prompt,
            "messages": messages
        }
        
        response = requests.post(
            self.api_url,
            json=payload,
            headers=headers,
            timeout=15
        )
        
        response.raise_for_status()
        
        result = response.json()
        reply = result["content"][0]["text"].strip()
        
        # Track token usage
        self._track_usage(
            model=payload["model"],
            tokens=result.get("usage", {}).get("output_tokens", len(reply.split()))
        )
        
        return reply
    
    def _is_refusal(self, text: str) -> bool:
        """Check if response is a refusal"""
        text_lower = text.lower()
        return any(re.search(pattern, text_lower) for pattern in self.refusal_patterns)
    
    def _sanitize_reply(self, text: str) -> str:
        """Remove asterisk actions and clean up text"""
        # Remove *actions*
        text = re.sub(r'\*[^*]+\*', '', text)
        
        # Remove multiple spaces
        text = ' '.join(text.split())
        
        # Ensure it ends properly
        if text and not text[-1] in '.!?':
            text += '.'
        
        return text.strip()
    
    def _generate_fallback(self, name: str) -> str:
        """Generate fallback message when AI fails"""
        fallbacks = [
            f"Hey {name}! How's your evening going? 😊",
            f"Well hello there {name} 😉 What brings you to Tinder?",
            f"{name}! Love the vibe of your profile. What's been the highlight of your week?",
            f"Hi {name}! You seem interesting. Tell me something random about yourself?",
            f"Hey {name}, fancy a chat? What's your idea of a perfect Friday night?"
        ]
        
        return random.choice(fallbacks)
    
    def _track_usage(self, model: str, tokens: int):
        """Track token usage for billing"""
        try:
            usage = {}
            if CLAUDE_USAGE_FILE.exists():
                with open(CLAUDE_USAGE_FILE, 'r') as f:
                    usage = json.load(f)
            
            usage["total_tokens"] = usage.get("total_tokens", 0) + tokens
            usage["by_model"] = usage.get("by_model", {})
            usage["by_model"][model] = usage["by_model"].get(model, 0) + tokens
            
            with open(CLAUDE_USAGE_FILE, 'w') as f:
                json.dump(usage, f, indent=2)
                
        except Exception as e:
            logger.error(f"Failed to track token usage: {e}")
