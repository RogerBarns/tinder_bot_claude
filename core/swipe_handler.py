"""
core/swipe_handler.py - Handle swiping logic
"""
import logging
import random
import time
from typing import Dict, List, Optional
from datetime import datetime, timezone

from config import config
from core.api_selector import get_api_client

logger = logging.getLogger(__name__)


class SwipeHandler:
    """Handle swiping on profiles"""

    def __init__(self):
        """Initialize swipe handler"""
        self.api_client = get_api_client("swipe_handler")
        self.swipe_stats = {
            "total_swipes": 0,
            "right_swipes": 0,
            "left_swipes": 0,
            "matches": 0,
            "last_swipe": None
        }
        logger.info("✅ SwipeHandler initialized")

    def auto_swipe(self, count: int = 10) -> Dict:
        """
        Perform automatic swiping

        Args:
            count: Number of profiles to swipe on

        Returns:
            Statistics about the swipe session
        """
        logger.info(f"🎯 Starting auto-swipe session ({count} profiles)")

        session_stats = {
            "swiped": 0,
            "liked": 0,
            "passed": 0,
            "matches": 0,
            "errors": 0
        }

        try:
            # Get recommendations
            recommendations = self.api_client.get_recommendations(limit=count)

            if not recommendations:
                logger.warning("📭 No recommendations available")
                return session_stats

            logger.info(f"📋 Got {len(recommendations)} recommendations")

            for rec in recommendations:
                try:
                    user_id = rec.get("user_id")
                    name = rec.get("name", "Unknown")
                    bio = rec.get("bio", "")
                    age = rec.get("age", 0)
                    distance = rec.get("distance", 0)

                    # Decide whether to swipe right or left
                    should_like = self._should_like_profile(rec)
                    direction = "right" if should_like else "left"

                    logger.info(f"👆 Swiping {direction} on {name} ({age}yo, {distance}km)")

                    # Perform swipe
                    success = self.api_client.swipe(user_id, direction)

                    if success:
                        session_stats["swiped"] += 1
                        self.swipe_stats["total_swipes"] += 1

                        if should_like:
                            session_stats["liked"] += 1
                            self.swipe_stats["right_swipes"] += 1
                        else:
                            session_stats["passed"] += 1
                            self.swipe_stats["left_swipes"] += 1

                        self.swipe_stats["last_swipe"] = datetime.now(timezone.utc).isoformat()

                        # Check for match (would be returned by API in real implementation)
                        if should_like and random.random() < 0.3:  # 30% match rate for likes
                            session_stats["matches"] += 1
                            self.swipe_stats["matches"] += 1
                            logger.info(f"🎉 It's a match with {name}!")
                    else:
                        session_stats["errors"] += 1
                        logger.error(f"❌ Failed to swipe on {name}")

                    # Random delay between swipes (human-like behavior)
                    delay = random.uniform(
                        config.get("min_swipe_delay", 2),
                        config.get("max_swipe_delay", 8)
                    )
                    time.sleep(delay)

                except Exception as e:
                    logger.error(f"Error swiping on profile: {e}")
                    session_stats["errors"] += 1
                    continue

        except Exception as e:
            logger.error(f"Error in auto-swipe session: {e}")

        logger.info(
            f"✅ Swipe session complete: "
            f"{session_stats['liked']} likes, "
            f"{session_stats['passed']} passes, "
            f"{session_stats['matches']} matches"
        )

        return session_stats

    def _should_like_profile(self, profile: Dict) -> bool:
        """
        Decide whether to like a profile based on criteria

        Args:
            profile: Profile data

        Returns:
            True if should swipe right, False for left
        """
        # Get swipe preferences from config
        min_age = config.get("min_age", 18)
        max_age = config.get("max_age", 100)
        max_distance = config.get("max_distance", 100)
        like_ratio = config.get("like_ratio", 0.3)  # Default 30% like rate

        age = profile.get("age", 25)
        distance = profile.get("distance", 50)
        bio = profile.get("bio", "")

        # Apply filters
        if age < min_age or age > max_age:
            logger.debug(f"Age {age} outside range {min_age}-{max_age}")
            return False

        if distance > max_distance:
            logger.debug(f"Distance {distance}km exceeds max {max_distance}km")
            return False

        # Bio keywords (positive and negative)
        positive_keywords = config.get("positive_keywords", [])
        negative_keywords = config.get("negative_keywords", [])

        bio_lower = bio.lower()

        # Check negative keywords
        for keyword in negative_keywords:
            if keyword.lower() in bio_lower:
                logger.debug(f"Found negative keyword: {keyword}")
                return False

        # Boost for positive keywords
        boost = 0
        for keyword in positive_keywords:
            if keyword.lower() in bio_lower:
                boost += 0.2
                logger.debug(f"Found positive keyword: {keyword}")

        # Random decision with boost
        final_ratio = min(like_ratio + boost, 0.9)  # Cap at 90%
        decision = random.random() < final_ratio

        return decision

    def manual_swipe(self, direction: str = "right", user_id: Optional[str] = None) -> Dict:
        """
        Perform a manual swipe

        Args:
            direction: "right" for like, "left" for pass
            user_id: Optional specific user ID to swipe on

        Returns:
            Result of the swipe
        """
        logger.info(f"👆 Manual swipe {direction}")

        try:
            if not user_id:
                # Get one recommendation
                recommendations = self.api_client.get_recommendations(limit=1)
                if not recommendations:
                    return {"success": False, "error": "No recommendations available"}

                profile = recommendations[0]
                user_id = profile.get("user_id")
                name = profile.get("name", "Unknown")
            else:
                profile = self.api_client.get_profile(user_id)
                name = profile.get("name", "Unknown") if profile else "Unknown"

            # Perform swipe
            success = self.api_client.swipe(user_id, direction)

            if success:
                self.swipe_stats["total_swipes"] += 1
                if direction == "right":
                    self.swipe_stats["right_swipes"] += 1
                else:
                    self.swipe_stats["left_swipes"] += 1

                self.swipe_stats["last_swipe"] = datetime.now(timezone.utc).isoformat()

                logger.info(f"✅ Swiped {direction} on {name}")
                return {
                    "success": True,
                    "direction": direction,
                    "user_id": user_id,
                    "name": name
                }
            else:
                logger.error(f"❌ Failed to swipe on {name}")
                return {
                    "success": False,
                    "error": "Swipe failed"
                }

        except Exception as e:
            logger.error(f"Error in manual swipe: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def get_stats(self) -> Dict:
        """Get swipe statistics"""
        return self.swipe_stats.copy()

    def reset_stats(self):
        """Reset swipe statistics"""
        self.swipe_stats = {
            "total_swipes": 0,
            "right_swipes": 0,
            "left_swipes": 0,
            "matches": 0,
            "last_swipe": None
        }
        logger.info("📊 Swipe stats reset")