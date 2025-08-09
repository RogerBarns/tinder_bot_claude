"""
personality/generator.py - Message generator with different personalities
"""
import random
import logging
from typing import List, Dict, Optional

logger = logging.getLogger(__name__)


class MessageGenerator:
    """Generate messages with different personalities"""

    def __init__(self):
        """Initialize message generator"""
        self.personalities = {
            "default": self._default_personality,
            "flirty": self._flirty_personality,
            "funny": self._funny_personality,
            "gentle": self._gentle_personality,
            "intellectual": self._intellectual_personality
        }
        logger.info("✅ MessageGenerator initialized")

    def generate_reply(
        self,
        name: str,
        bio: str,
        chat_history: List[Dict],
        personality: str = "default"
    ) -> str:
        """
        Generate a reply message

        Args:
            name: Match's name
            bio: Match's bio
            chat_history: Previous messages
            personality: Personality style to use

        Returns:
            Generated reply message
        """
        # Get the personality function
        personality_func = self.personalities.get(personality, self._default_personality)

        # Get last user message
        last_msg = ""
        for msg in reversed(chat_history):
            if msg.get("role") == "user":
                last_msg = msg.get("content", "")
                break

        # Generate reply based on personality
        reply = personality_func(name, bio, last_msg, chat_history)

        logger.info(f"🤖 Generated {personality} reply: {reply[:50]}...")
        return reply

    def generate_opener(
        self,
        name: str,
        bio: str,
        personality: str = "default"
    ) -> str:
        """
        Generate an opening message

        Args:
            name: Match's name
            bio: Match's bio
            personality: Personality style to use

        Returns:
            Generated opening message
        """
        openers = {
            "default": [
                f"Hey {name}! How's your day going?",
                f"Hi {name}! Nice to match with you 😊",
                f"Hey there {name}! What are you up to today?"
            ],
            "flirty": [
                f"Hey {name}, you caught my eye! 😍",
                f"Well hello there {name} 😉",
                f"Hi {name}! Your smile is absolutely captivating ✨"
            ],
            "funny": [
                f"Hey {name}! On a scale of 1-10, how's your day? I'm at a solid 7.5 😄",
                f"Hi {name}! Quick question: pineapple on pizza - yes or no? 🍕",
                f"Hey {name}! I was going to use a pickup line, but I figured just saying hi might work better 😅"
            ],
            "gentle": [
                f"Hi {name}, hope you're having a lovely day 🌸",
                f"Hello {name}! Your profile really resonated with me",
                f"Hey {name}, would love to get to know you better 😊"
            ]
        }

        # Add bio-specific openers if bio exists
        if bio:
            if "coffee" in bio.lower():
                openers["default"].append(f"Hey {name}! I see you're into coffee - what's your go-to order? ☕")
            if "travel" in bio.lower():
                openers["default"].append(f"Hi {name}! Where's your favorite place you've traveled to?")
            if "dog" in bio.lower() or "cat" in bio.lower():
                openers["default"].append(f"Hey {name}! Your pet is adorable! What's their name? 🐾")

        # Get openers for personality
        personality_openers = openers.get(personality, openers["default"])
        opener = random.choice(personality_openers)

        logger.info(f"🎯 Generated {personality} opener: {opener}")
        return opener

    # Personality implementations

    def _default_personality(self, name: str, bio: str, last_msg: str, history: List[Dict]) -> str:
        """Default balanced personality"""
        responses = []

        # Context-aware responses
        if "?" in last_msg:
            # They asked a question
            if "how are you" in last_msg.lower() or "how's" in last_msg.lower():
                responses.extend([
                    "I'm doing great, thanks for asking! How about you?",
                    "Pretty good! Just enjoying the day. What about yourself?",
                    "Can't complain! How's your day been?"
                ])
            elif "what" in last_msg.lower():
                responses.extend([
                    "That's a great question! I'd love to know more about your thoughts on it too",
                    "Interesting question! What made you think of that?",
                    "Good question! I think it depends on the perspective"
                ])
            else:
                responses.extend([
                    "That's interesting! Tell me more",
                    "I'd love to hear your thoughts on that",
                    "Great question! What do you think?"
                ])
        else:
            # They made a statement
            responses.extend([
                f"That's really interesting, {name}! Tell me more",
                f"I love that! What else are you into?",
                f"That sounds amazing! How did you get into that?",
                f"Wow, that's cool! I'd love to hear more about it"
            ])

        return random.choice(responses)

    def _flirty_personality(self, name: str, bio: str, last_msg: str, history: List[Dict]) -> str:
        """Flirty and playful personality"""
        responses = []

        if "?" in last_msg:
            responses.extend([
                f"Hmm, great question {name}! But first, I have to say you have amazing energy 😊",
                "I could answer that, but I'm more interested in getting to know you better 😉",
                f"Good question! You're pretty intriguing yourself, {name} ✨"
            ])
        else:
            responses.extend([
                f"You're really something special, {name} 😍",
                "I have to admit, you've got my full attention now 😊",
                f"There's something about you that's just... captivating ✨",
                "You're making me smile over here! 😄"
            ])

        return random.choice(responses)

    def _funny_personality(self, name: str, bio: str, last_msg: str, history: List[Dict]) -> str:
        """Funny and witty personality"""
        responses = []

        if "?" in last_msg:
            responses.extend([
                "Is this a pop quiz? Because I didn't study! 😅",
                f"Great question, {name}! I'll trade you an answer for your best dad joke",
                "Hmm, let me consult my magic 8-ball... it says 'ask again later' 🎱"
            ])
        else:
            responses.extend([
                "Well, this conversation just got 100% more interesting! 🎉",
                f"Plot twist: {name} just became my favorite person to chat with today",
                "I'm giving this message a solid 10/10. Would read again! 📖",
                "This is better than my morning coffee, and that's saying something! ☕"
            ])

        return random.choice(responses)

    def _gentle_personality(self, name: str, bio: str, last_msg: str, history: List[Dict]) -> str:
        """Gentle and thoughtful personality"""
        responses = []

        if "?" in last_msg:
            responses.extend([
                f"That's such a thoughtful question, {name}. I really appreciate your curiosity",
                "What a wonderful thing to ask about. I'd love to explore that with you",
                f"You ask such interesting questions, {name}. It really makes me think"
            ])
        else:
            responses.extend([
                f"Thank you for sharing that, {name}. It means a lot",
                "I really appreciate you opening up like that 🌸",
                f"That's beautiful, {name}. You have such a wonderful perspective",
                "Your message really brightened my day. Thank you for that 😊"
            ])

        return random.choice(responses)

    def _intellectual_personality(self, name: str, bio: str, last_msg: str, history: List[Dict]) -> str:
        """Intellectual and sophisticated personality"""
        responses = []

        if "?" in last_msg:
            responses.extend([
                f"Fascinating question, {name}. From a philosophical standpoint...",
                "That's quite thought-provoking. Have you considered the implications?",
                f"An excellent inquiry, {name}. Let's explore this together"
            ])
        else:
            responses.extend([
                f"Your perspective is quite intriguing, {name}. I'd love to delve deeper",
                "That's a remarkably insightful observation. What led you to that conclusion?",
                f"You raise an excellent point, {name}. The nuances here are fascinating"
            ])

        return random.choice(responses)