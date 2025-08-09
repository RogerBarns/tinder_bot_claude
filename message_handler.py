"""
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
