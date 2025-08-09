"""
Add messaging functionality to the Tinder bot
This file adds to your existing dashboard_browser.py
"""

import os
from pathlib import Path


def create_message_handler():
    """Create a message handler module"""

    message_handler_code = '''"""
Message handling for Tinder bot
Handles reading and replying to messages
"""
import time
import random
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime

class MessageHandler:
    def __init__(self, driver, claude_handler=None):
        self.driver = driver
        self.claude_handler = claude_handler
        self.processed_messages = set()

    def get_matches_with_messages(self):
        """Get all matches that have sent messages"""
        matches = []

        try:
            # Navigate to matches page
            if "/app/matches" not in self.driver.current_url:
                self.driver.get("https://tinder.com/app/matches")
                time.sleep(2)

            # Find all match elements
            match_elements = self.driver.find_elements(By.CSS_SELECTOR, "[role='link']")

            for element in match_elements:
                try:
                    # Check if has unread message indicator
                    name = element.find_element(By.CSS_SELECTOR, "div").text
                    if name:
                        matches.append({
                            "name": name,
                            "element": element,
                            "has_new_message": self.check_for_new_message(element)
                        })
                except:
                    continue

            return matches

        except Exception as e:
            print(f"Error getting matches: {e}")
            return []

    def check_for_new_message(self, match_element):
        """Check if a match has a new message"""
        try:
            # Look for unread message indicators
            indicators = match_element.find_elements(By.CSS_SELECTOR, ".badge, .unread, [data-testid='message-preview']")
            return len(indicators) > 0
        except:
            return False

    def open_chat(self, match_element):
        """Open a specific chat"""
        try:
            match_element.click()
            time.sleep(1)
            return True
        except:
            return False

    def read_messages(self):
        """Read messages from current chat"""
        messages = []

        try:
            # Find message elements
            message_elements = self.driver.find_elements(By.CSS_SELECTOR, "[class*='message'], [data-testid*='message']")

            for element in message_elements:
                try:
                    text = element.text
                    if text:
                        # Determine if it's from match or us
                        is_from_match = "received" in element.get_attribute("class") or element.location['x'] < 400
                        messages.append({
                            "text": text,
                            "from_match": is_from_match
                        })
                except:
                    continue

            return messages

        except Exception as e:
            print(f"Error reading messages: {e}")
            return []

    def send_message(self, message):
        """Send a message in current chat"""
        try:
            # Find message input
            input_selectors = [
                "[data-testid='messageInput']",
                "textarea",
                "[placeholder*='Type a message']",
                "[contenteditable='true']"
            ]

            message_input = None
            for selector in input_selectors:
                elements = self.driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    message_input = elements[0]
                    break

            if not message_input:
                print("Could not find message input")
                return False

            # Type message with human-like delays
            message_input.click()
            time.sleep(0.5)

            for char in message:
                message_input.send_keys(char)
                time.sleep(random.uniform(0.05, 0.15))  # Human typing speed

            time.sleep(0.5)

            # Send message
            message_input.send_keys(Keys.RETURN)

            print(f"Sent message: {message}")
            return True

        except Exception as e:
            print(f"Error sending message: {e}")
            return False

    def generate_reply(self, match_name, messages):
        """Generate a reply using Claude or fallback"""
        if self.claude_handler:
            # Use Claude AI
            return self.claude_handler.generate_reply(match_name, messages)
        else:
            # Use simple fallback responses
            responses = [
                f"Hey {match_name}! How's your day going?",
                f"Hi {match_name}! What are you up to?",
                "Hey there! 😊 How's it going?",
                "Hi! How was your weekend?",
                "Hey! What brings you to Tinder?",
                f"Hi {match_name}! Tell me something interesting about yourself",
                "Hey! Love your energy 😊 What do you do for fun?"
            ]
            return random.choice(responses)

    def process_new_messages(self):
        """Process all new messages and reply"""
        replied_count = 0

        try:
            matches = self.get_matches_with_messages()
            print(f"Found {len(matches)} matches")

            for match in matches:
                if match['has_new_message']:
                    print(f"Processing messages from {match['name']}")

                    # Open chat
                    if self.open_chat(match['element']):
                        time.sleep(1)

                        # Read messages
                        messages = self.read_messages()

                        if messages:
                            # Generate reply
                            reply = self.generate_reply(match['name'], messages)

                            # Send reply
                            if self.send_message(reply):
                                replied_count += 1
                                time.sleep(random.uniform(2, 5))  # Wait between conversations

                        # Go back to matches
                        self.driver.get("https://tinder.com/app/matches")
                        time.sleep(1)

            return replied_count

        except Exception as e:
            print(f"Error processing messages: {e}")
            return replied_count
'''

    # Save message handler
    with open("message_handler.py", "w", encoding="utf-8") as f:
        f.write(message_handler_code)

    print("✅ Created message_handler.py")


def create_claude_handler():
    """Create Claude AI handler for generating responses"""

    claude_code = '''"""
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
            conversation = "\\n".join([
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
'''

    with open("claude_handler.py", "w", encoding="utf-8") as f:
        f.write(claude_code)

    print("✅ Created claude_handler.py")


def update_dashboard_with_messaging():
    """Update dashboard to include messaging features"""

    update_code = '''
# Add this to your dashboard_browser.py after the TinderBrowser class

# Import message handler
try:
    from message_handler import MessageHandler
    from claude_handler import ClaudeHandler
    MESSAGE_HANDLER_AVAILABLE = True
    print("✅ Message handler loaded")
except ImportError:
    MESSAGE_HANDLER_AVAILABLE = False
    print("⚠️ Message handler not available")

# Initialize message handler (add after tinder_browser initialization)
if MESSAGE_HANDLER_AVAILABLE and tinder_browser.driver:
    claude = ClaudeHandler()
    message_handler = MessageHandler(tinder_browser.driver, claude)
else:
    message_handler = None

# Add this route to your dashboard_browser.py

@app.route('/process-messages', methods=['POST'])
def process_messages():
    """Process and reply to messages"""
    if not tinder_browser.driver:
        return jsonify({
            "status": "error",
            "message": "Browser not started"
        })

    if not tinder_browser.is_logged_in:
        return jsonify({
            "status": "error",
            "message": "Not logged in to Tinder"
        })

    if not message_handler:
        return jsonify({
            "status": "error",
            "message": "Message handler not initialized"
        })

    # Process messages
    replied_count = message_handler.process_new_messages()

    return jsonify({
        "status": "ok",
        "replied_to": replied_count,
        "message": f"Replied to {replied_count} matches"
    })

# Add auto-reply functionality (add to toggle_bot route)
# When bot is enabled, start auto-reply thread
def auto_reply_loop():
    """Auto-reply to messages"""
    while bot_state['bot_enabled']:
        if tinder_browser.driver and tinder_browser.is_logged_in and message_handler:
            replied = message_handler.process_new_messages()
            if replied > 0:
                print(f"📬 Auto-replied to {replied} matches")
        time.sleep(60)  # Check every minute

# Start auto-reply thread when bot is enabled
if bot_state['bot_enabled']:
    reply_thread = threading.Thread(target=auto_reply_loop, daemon=True)
    reply_thread.start()
'''

    with open("dashboard_updates.txt", "w", encoding="utf-8") as f:
        f.write(update_code)

    print("✅ Created dashboard_updates.txt with messaging integration")
    print("\n📋 Add the code from dashboard_updates.txt to your dashboard_browser.py")


def main():
    print("=" * 60)
    print("🔧 ADDING MESSAGING FEATURES TO TINDER BOT")
    print("=" * 60)

    # Create the modules
    create_message_handler()
    create_claude_handler()
    update_dashboard_with_messaging()

    print("\n" + "=" * 60)
    print("✅ MESSAGING FEATURES CREATED!")
    print("=" * 60)
    print("\nTo enable messaging:")
    print("1. Set your Claude API key:")
    print("   Create a .env file with: CLAUDE_API_KEY=your_key_here")
    print("\n2. Add the code from dashboard_updates.txt to dashboard_browser.py")
    print("\n3. Install required package:")
    print("   pip install anthropic python-dotenv")
    print("\n4. Restart your dashboard")
    print("\n5. The bot will now auto-reply to messages when enabled!")
    print("=" * 60)


if __name__ == "__main__":
    main()