"""
Claude AI integration for generating Tinder responses
"""
import os
from anthropic import Anthropic

class ClaudeHandler:
    def __init__(self):
        self.api_key = os.getenv("CLAUDE_API_KEY")
        if self.api_key:
            self.client = Anthropic(api_key=self.api_key)
            self.available = True
        else:
            self.available = False
            print("⚠️ CLAUDE_API_KEY not found in environment variables")

    def generate_reply(self, match_name, messages):
        """Generate a contextual reply using Claude"""
        if not self.available:
            # Fallback responses
            return f"Hey {match_name}! How's it going? 😊"

        try:
            # Build conversation context
            conversation = "\n".join([
                f"{'Them' if msg['from_match'] else 'Me'}: {msg['text']}" 
                for msg in messages[-5:]  # Last 5 messages for context
            ])

            prompt = f"""You are Josh, a 34-year-old confident, British man on Tinder. 
You're flirty, funny, and charming. Keep responses short (1-2 sentences), casual, and engaging.
Never mention being AI or a bot. Use British slang occasionally.

Match name: {match_name}
Recent conversation:
{conversation}

Generate a short, flirty response that continues the conversation naturally:"""

            response = self.client.messages.create(
                model="claude-3-haiku-20240307",
                max_tokens=100,
                temperature=0.8,
                messages=[{"role": "user", "content": prompt}]
            )

            return response.content[0].text.strip()

        except Exception as e:
            print(f"Claude API error: {e}")
            # Fallback response
            return f"Hey {match_name}! That's interesting, tell me more 😊"
