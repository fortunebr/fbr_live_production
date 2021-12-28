"""
Webhook/Api implementation

"""

from typing import Optional

import requests
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from core.log_me import logMessage


def webhook_request(url: str, data: dict, wh_type: Optional[str] = ""):
    """Send the data to webhook."""

    try:
        res = requests.post(url, json=data)
        if res.status_code >= 400:
            logMessage(f"{wh_type} request failed: #{res.status_code}")
    except Exception as e:
        logMessage(f"Failed to send to {wh_type} webhook\n{e}")


def slack_api(
    token: str, channel_id: str, text: str, blocks: list, summary: Optional[str] = None
) -> None:
    """Slack client execution"""

    CLIENT = WebClient(token=token)

    try:
        res = CLIENT.chat_postMessage(channel=channel_id, text=text, blocks=blocks)
        thread_id = res.data.get("ts", None)
        if summary:
            if thread_id:
                res = CLIENT.chat_postMessage(
                    channel=channel_id, text=summary, thread_ts=thread_id
                )
                # Get captured old message id's and delete them
                with open("slack_ts.txt", "r") as f:
                    slack_ts = f.read()
                for ts in slack_ts.strip().split("\n"):
                    _ = CLIENT.chat_delete(channel=channel_id, ts=ts)
                with open("slack_ts.txt", "w+") as f:
                    f.write("")
        else:
            with open("slack_ts.txt", "a+") as f:
                f.write("\n")
                f.write(thread_id)

    except SlackApiError as e:
        logMessage(f"Failed to send to Slack client\n{e}")
    except OSError:
        # slack_ts.txt file not found
        pass
    except Exception as e:
        logMessage(f"Slack App execution failure, please report..\n{e}")
