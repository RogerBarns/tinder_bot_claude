"""
core/tinder_api.py - Fixed TinderAPIClient with all required methods
"""
import time
import random
import logging
from typing import Dict, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class TinderAPIClient:
    """
    Tinder API Client - Stub implementation for testing
    This provides all required methods with stub data
    """

    def __init__(self, config=None):
        """Initialize the API client"""
        self.config = config or {}
        self.logged_in = False
        self.driver = None
        self.test_mode = self.config.get('test_mode', True)

        # Stub data for testing
        self.stub_matches = [
            {
                "match_id": "match_001",
                "user_id": "user_001",
                "name": "Emma",
                "bio": "Love hiking and coffee ☕",
                "age": 25,
                "messages": [
                    {"role": "user", "content": "Hey! How's your weekend going?", "timestamp": "2025-01-07T10:00:00Z"}
                ],
                "last_activity": datetime.now(timezone.utc).isoformat(),
                "created_at": "2025-01-06T12:00:00Z"
            },
            {
                "match_id": "match_002",
                "user_id": "user_002",
                "name": "Sophie",
                "bio": "Yoga instructor 🧘‍♀️",
                "age": 28,
                "messages": [
                    {"role": "user", "content": "Hi there! Nice to match with you 😊", "timestamp": "2025-01-07T11:00:00Z"}
                ],
                "last_activity": datetime.now(timezone.utc).isoformat(),
                "created_at": "2025-01-06T14:00:00Z"
            },
            {
                "match_id": "match_003",
                "user_id": "user_003",
                "name": "Olivia",
                "bio": "Dog mom 🐕 | Wine enthusiast 🍷",
                "age": 26,
                "messages": [],
                "last_activity": datetime.now(timezone.utc).isoformat(),
                "created_at": "2025-01-07T08:00:00Z"
            }
        ]

        logger.info("✅ TinderAPIClient initialized (stub mode)")

    def initialize_driver(self):
        """Initialize browser driver (stub)"""
        logger.info("🌐 Initializing browser driver (stub)...")
        time.sleep(1)  # Simulate startup time
        self.driver = {"type": "stub", "initialized": True}
        logger.info("✅ Browser driver initialized (stub)")
        return True

    def login(self, phone_number=None):
        """Login to Tinder (stub)"""
        logger.info("🔑 Attempting login (stub)...")
        time.sleep(2)  # Simulate login time
        self.logged_in = True
        self.is_logged_in = True
        logger.info("✅ Login successful (stub)")
        return True

    def get_matches(self, limit=100):
        """Get list of matches"""
        logger.info(f"📋 Fetching matches (limit: {limit})...")

        if not self.logged_in and not self.test_mode:
            logger.error("❌ Not logged in")
            return []

        # Return stub matches
        matches = self.stub_matches[:limit]
        logger.info(f"✅ Found {len(matches)} matches")
        return matches

    def get_messages(self, match_id: str) -> List[Dict]:
        """Get messages for a specific match"""
        logger.info(f"💬 Getting messages for match {match_id}")

        # Find the match in stub data
        for match in self.stub_matches:
            if match["match_id"] == match_id:
                return match.get("messages", [])

        return []

    def send_message(self, match_id: str, message: str) -> bool:
        """Send a message to a match"""
        logger.info(f"📤 Sending message to {match_id}: {message[:50]}...")

        if not self.logged_in and not self.test_mode:
            logger.error("❌ Not logged in")
            return False

        # Simulate typing delay
        typing_delay = self.config.get('typing_delay', 3)
        time.sleep(typing_delay + random.uniform(-1, 1))

        # Update stub data (simulate sending)
        for match in self.stub_matches:
            if match["match_id"] == match_id:
                match["messages"].append({
                    "role": "assistant",
                    "content": message,
                    "timestamp": datetime.now(timezone.utc).isoformat()
                })
                logger.info(f"✅ Message sent to {match_id}")
                return True

        logger.error(f"❌ Match {match_id} not found")
        return False

    def get_recommendations(self, limit=10):
        """Get swipe recommendations"""
        logger.info(f"🎯 Getting {limit} recommendations...")

        if not self.logged_in and not self.test_mode:
            logger.error("❌ Not logged in")
            return []

        # Generate stub recommendations
        recommendations = []
        for i in range(limit):
            recommendations.append({
                "user_id": f"rec_{i:03d}",
                "name": f"User {i+1}",
                "age": random.randint(21, 35),
                "bio": "Looking for something fun!",
                "distance": random.randint(1, 50),
                "photos": [f"photo_{j}.jpg" for j in range(3)]
            })

        logger.info(f"✅ Got {len(recommendations)} recommendations")
        return recommendations

    def swipe(self, user_id: str, direction: str = "right") -> bool:
        """Swipe on a user"""
        action = "Like" if direction == "right" else "Pass"
        logger.info(f"👆 {action} on user {user_id}")

        if not self.logged_in and not self.test_mode:
            logger.error("❌ Not logged in")
            return False

        # Simulate swipe delay
        time.sleep(random.uniform(0.5, 2))

        # Random match chance for right swipes
        if direction == "right" and random.random() < 0.3:
            logger.info(f"🎉 It's a match with {user_id}!")
            # Add to matches
            self.stub_matches.append({
                "match_id": f"match_{len(self.stub_matches):03d}",
                "user_id": user_id,
                "name": f"New Match",
                "bio": "Just matched!",
                "age": random.randint(21, 35),
                "messages": [],
                "last_activity": datetime.now(timezone.utc).isoformat(),
                "created_at": datetime.now(timezone.utc).isoformat()
            })

        logger.info(f"✅ Swiped {direction} on {user_id}")
        return True

    def get_profile(self, user_id: str) -> Optional[Dict]:
        """Get detailed profile information"""
        logger.info(f"👤 Getting profile for {user_id}")

        # Find in matches
        for match in self.stub_matches:
            if match["user_id"] == user_id:
                return match

        # Return stub profile
        return {
            "user_id": user_id,
            "name": "Unknown User",
            "bio": "No bio available",
            "age": 25,
            "photos": []
        }

    def unmatch(self, match_id: str) -> bool:
        """Unmatch with someone"""
        logger.info(f"💔 Unmatching {match_id}")

        # Remove from stub matches
        self.stub_matches = [m for m in self.stub_matches if m["match_id"] != match_id]
        logger.info(f"✅ Unmatched {match_id}")
        return True

    def close(self):
        """Close the browser/connection"""
        logger.info("🔌 Closing connection...")
        if self.driver:
            self.driver = None
        self.logged_in = False
        logger.info("✅ Connection closed")

    def is_rate_limited(self) -> bool:
        """Check if we're rate limited"""
        # Stub: never rate limited in test mode
        return False

    def get_user_info(self) -> Optional[Dict]:
        """Get current user's profile info"""
        if not self.logged_in and not self.test_mode:
            return None

        return {
            "user_id": "self",
            "name": "Test User",
            "age": 25,
            "bio": "Testing the bot!"
        }

    def __repr__(self):
        """String representation"""
        status = "logged in" if self.logged_in else "not logged in"
        return "<TinderAPIClient: {status}, test_mode={self.test_mode}>"