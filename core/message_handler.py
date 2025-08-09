"""
core/message_handler.py - Fixed message handler
"""
import json
import logging
import time
import random
from datetime import datetime, timezone
from typing import Dict, List, Optional
from pathlib import Path

from config import config, DATA_DIR
from core.api_selector import get_api_client
from personality.generator import MessageGenerator

logger = logging.getLogger(__name__)


class MessageHandler:
    """Handles message processing and responses"""

    def __init__(self):
        """Initialize message handler"""
        self.api_client = get_api_client("message_handler")
        self.generator = MessageGenerator()
        self.processed_messages = set()
        self.chat_log_file = DATA_DIR / "chat_log.json"
        self.auto_approved_file = DATA_DIR / "auto_approved_log.json"

        # Load previously processed messages
        self._load_processed_messages()

        logger.info("✅ MessageHandler initialized")

    def _load_processed_messages(self):
        """Load previously processed message IDs"""
        if self.chat_log_file.exists():
            try:
                with open(self.chat_log_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            log = json.loads(line)
                            msg_id = f"{log.get('match_id')}_{log.get('timestamp')}"
                            self.processed_messages.add(msg_id)
                        except:
                            continue
                logger.info(f"📋 Loaded {len(self.processed_messages)} processed messages")
            except Exception as e:
                logger.error(f"Error loading processed messages: {e}")

    def process_new_messages(self, socketio=None) -> List[Dict]:
        """
        Process new messages from matches

        Args:
            socketio: Optional SocketIO instance for real-time updates

        Returns:
            List of processed message logs
        """
        processed = []

        try:
            # Get matches
            matches = self.api_client.get_matches(limit=config.get("match_limit", 100))

            if not matches:
                logger.info("📭 No matches found")
                return processed

            logger.info(f"📬 Found {len(matches)} matches to check")

            for match in matches:
                try:
                    match_id = match.get("match_id")
                    user_name = match.get("name", "Unknown")
                    user_bio = match.get("bio", "")

                    # Get messages for this match
                    messages = match.get("messages", [])

                    if not messages:
                        logger.debug(f"No messages from {user_name}")
                        continue

                    # Get last user message
                    user_messages = [m for m in messages if m.get("role") == "user"]
                    if not user_messages:
                        continue

                    last_user_msg = user_messages[-1]
                    msg_content = last_user_msg.get("content", "")
                    msg_timestamp = last_user_msg.get("timestamp", "")

                    # Create unique message ID
                    msg_id = f"{match_id}_{msg_timestamp}"

                    # Skip if already processed
                    if msg_id in self.processed_messages:
                        continue

                    logger.info(f"💬 New message from {user_name}: {msg_content[:50]}...")

                    # Generate reply
                    personality = config.get("personality", "default")
                    bot_reply = self.generator.generate_reply(
                        name=user_name,
                        bio=user_bio,
                        chat_history=messages,
                        personality=personality
                    )

                    # Create log entry
                    log_entry = {
                        "match_id": match_id,
                        "user_name": user_name,
                        "user_msg": msg_content,
                        "bot_reply": bot_reply,
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "personality": personality,
                        "auto": config.get("auto_approve", False)
                    }

                    # Auto-approve if enabled
                    if config.get("auto_approve", False):
                        success = self._send_reply(match_id, bot_reply)
                        if success:
                            log_entry["sent"] = True
                            logger.info(f"✅ Auto-replied to {user_name}")
                            self._save_to_auto_approved(log_entry)
                        else:
                            logger.error(f"❌ Failed to send reply to {user_name}")
                    else:
                        logger.info(f"⏸️ Reply pending approval for {user_name}")

                    # Mark as processed
                    self.processed_messages.add(msg_id)

                    # Save to chat log
                    self._save_to_chat_log(log_entry)

                    # Emit to WebSocket if available
                    if socketio:
                        socketio.emit("new_message", log_entry)

                    processed.append(log_entry)

                    # Rate limiting
                    time.sleep(random.uniform(2, 5))

                except Exception as e:
                    logger.error(f"Error processing match {match.get('match_id')}: {e}")
                    continue

            logger.info(f"✅ Processed {len(processed)} new messages")

        except Exception as e:
            logger.error(f"Error processing messages: {e}")

        return processed

    def _send_reply(self, match_id: str, message: str) -> bool:
        """Send a reply message"""
        try:
            # Add typing delay
            typing_delay = config.get("typing_delay", 3)
            time.sleep(typing_delay + random.uniform(-1, 1))

            # Send message
            return self.api_client.send_message(match_id, message)
        except Exception as e:
            logger.error(f"Error sending reply: {e}")
            return False

    def _save_to_chat_log(self, log_entry: Dict):
        """Save entry to chat log"""
        try:
            with open(self.chat_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Error saving to chat log: {e}")

    def _save_to_auto_approved(self, log_entry: Dict):
        """Save entry to auto-approved log"""
        try:
            with open(self.auto_approved_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            logger.error(f"Error saving to auto-approved log: {e}")

    def send_to_unmatched(self, count: int = 5) -> Dict:
        """
        Send opening messages to matches without any messages

        Args:
            count: Number of matches to message

        Returns:
            Result summary
        """
        sent = 0
        failed = 0

        try:
            matches = self.api_client.get_matches(limit=100)

            # Find matches with no messages
            unmatched = [m for m in matches if not m.get("messages", [])][:count]

            for match in unmatched:
                try:
                    match_id = match.get("match_id")
                    user_name = match.get("name", "Unknown")
                    user_bio = match.get("bio", "")

                    # Generate opening message
                    opener = self.generator.generate_opener(
                        name=user_name,
                        bio=user_bio,
                        personality=config.get("personality", "default")
                    )

                    # Send message
                    if self._send_reply(match_id, opener):
                        sent += 1
                        logger.info(f"✅ Sent opener to {user_name}")
                    else:
                        failed += 1
                        logger.error(f"❌ Failed to message {user_name}")

                    # Rate limiting
                    time.sleep(random.uniform(5, 10))

                except Exception as e:
                    logger.error(f"Error messaging unmatched: {e}")
                    failed += 1

        except Exception as e:
            logger.error(f"Error in send_to_unmatched: {e}")

        return {
            "sent": sent,
            "failed": failed,
            "total": sent + failed
        }