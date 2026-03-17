import os
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

NTFY_TOPIC = "nils-infra-maintenance-2026"  # Unique topic
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}"

class Notifier:
    def send_notification(self, title: str, message: str, priority: str = "default"):
        """
        Sends a notification via ntfy.sh
        """
        try:
            headers = {
                "Title": title,
                "Priority": priority,
            }
            response = requests.post(
                NTFY_URL,
                data=message.encode("utf-8"),
                headers=headers
            )
            response.raise_for_status()
            logger.info(f"✅ Notification sent to ntfy.sh/{NTFY_TOPIC}")
        except Exception as e:
            logger.error(f"❌ Failed to send notification: {e}")

def main():
    # This can be used as a standalone test
    notifier = Notifier()
    notifier.send_notification(
        "Maintenance Test", 
        "This is a test notification from the Infra Maintenance bot."
    )

if __name__ == "__main__":
    main()
