"""
**POST** request to webhook api.

1. Discord webhook
2. Slack webhook
3. Google Chat webhook

"""


from typing import TYPE_CHECKING

import requests
from .utils import logMessage

if TYPE_CHECKING:
    from .production import Production


def webhook_discord(embed: dict, url=None) -> None:
    """Discrod webhook execution"""

    if not url or not url.startswith("https://discord"):
        return
    try:
        res = requests.post(url, json=embed)
        if res.status_code >= 400:
            logMessage(f"Discord request failed: #{res.status_code}")
    except Exception as e:
        logMessage(f"Failed to send to discord webhook\n{e}")


def webhook_slack(block: dict, url=None) -> None:
    """Slack webhook execution"""

    if not url or not url.startswith("https://hooks.slack.com/services/"):
        return
    try:
        res = requests.post(url, json=block)
        if res.status_code >= 400:
            logMessage(f"Slack request failed: #{res.status_code}")
    except Exception as e:
        logMessage(f"Failed to send to slack webhook\n{e}")


def webhook_google(card: dict, url=None) -> None:
    """Google webhook execution"""

    if not url or not url.startswith("https://chat.googleapis.com"):
        return

    try:
        res = requests.post(url, json=card)
        if res.status_code >= 400:
            logMessage(f"Google request failed: #{res.status_code}")
    except Exception as e:
        logMessage(f"Failed to send to google webhook\n{e}")
