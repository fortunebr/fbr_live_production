"""
Message templates for each webhooks/apis.

1. Discord
2. Slack
3. Google Chat
4. Slack Client Api

"""

import random
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from core.production import Production


def randomColor() -> int:
    """Returns a random discord integer color"""

    discord_colors = {
        "green": 5763719,
        "yellow": 16705372,
        "red": 15548997,
        "rose": 15418782,
        "purple": 5793266,
        "dark_green": 1146986,
        "pink": 15277667,
        "orange": 15105570,
        "blue": 3447003,
    }
    return random.random.choice(discord_colors.values())


def discord_template(prod: "Production", average: int, summary: dict = None) -> dict:
    """Discord embed type meesage."""

    if not summary:
        # Hourly embed
        embed = {
            "embeds": [
                {
                    "color": f"{randomColor()}",
                    "fields": [
                        {
                            "name": "Achieved",
                            "value": f"**{prod.achieved}** pairs | **{prod.fg}** cs",
                        },
                        {
                            "name": "Last Hour",
                            "value": f"**{prod.phour}** pairs",
                            "inline": True,
                        },
                        {
                            "name": "Average",
                            "value": f"**{average}** pairs/hour",
                            "inline": True,
                        },
                    ],
                    "timestamp": f"{prod.time.utcnow()}",
                    "footer": {
                        "text": "Fortune Br",
                        # "icon_url": "https://i.imgur.com/7SwrwqC.jpg",
                    },
                }
            ]
        }

    else:
        # Summary embed
        top_prod: "Production" = summary["top"]
        embed = {
            "embeds": [
                {
                    "color": f"{randomColor()}",
                    "author": {"name": f"{prod.date.strftime('%A - %b %d, %Y')}"},
                    "thumbnail": {
                        "url": "https://i.imgur.com/e22h9tf.png",
                    },
                    "fields": [
                        {
                            "name": "Achieved",
                            "value": f"**{prod.achieved}** pairs | **{prod.fg}** cs",
                        },
                        {
                            "name": "Highest",
                            "value": f"**{top_prod.phour}** pairs/hour  `[{top_prod.hour_string}]`",
                            "inline": True,
                        },
                        {
                            "name": "Average",
                            "value": f"**{average}** pairs/hour",
                            "inline": True,
                        },
                        {
                            "name": "Report",
                            "value": "```{}```".format(summary["detail"]),
                        },
                    ],
                    "footer": {
                        "text": "Fortune Br",
                        # "icon_url": "https://i.imgur.com/7SwrwqC.jpg",
                    },
                    "timestamp": f"{prod.time.utcnow()}",
                }
            ]
        }

    return embed


def slack_template(prod: "Production", average: int, summary: dict = None) -> dict:
    """Slack block type message."""

    if not summary:
        # Hourly block
        block = {
            "text": f"{prod.achieved} pairs | {prod.fg} cs",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Achieved\n*{prod.achieved}* _pairs_ | *{prod.fg}* _cs_",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Last Hour\n*{prod.phour}* _pairs_",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Average\n*{average}* _pairs/hour_",
                    },
                },
                {"type": "divider"},
            ],
        }
    else:
        # Summary block
        top_prod: Production = summary["top"]
        block = {
            "text": f"{prod.achieved} pairs | {prod.fg} cs",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{prod.date.strftime('%A - %b %d, %Y')}",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Achieved\n*{prod.achieved}* _pairs_ | *{prod.fg}* _cs_",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Last Hour\n*{prod.phour}* _pairs_",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Highest\n*{top_prod.phour}* _pairs/hour_ `[{top_prod.hour_string}]`",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Average\n*{average}* _pairs/hour_",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Summary\n```{summary['detail']}```",
                    },
                },
                {"type": "divider"},
            ],
        }

    return block


# ToDo: Not checked
def google_template(prod: "Production", average: int, summary: dict = None) -> dict:
    """Google card type message."""

    card = {
        "text": f"{prod.achieved} pairs | {prod.fg} cs",
        "cards": [
            {
                "sections": [
                    {
                        "widgets": [
                            {
                                "keyValue": {
                                    "topLabel": f"Last hour",
                                    "content": f"{prod.phour} pairs",
                                }
                            },
                        ]
                    }
                ]
            }
        ],
    }

    if summary:
        # top_prod: Production = summary["top"]
        header = {"header": {"title": f"{prod.date.strftime('%A - %b %d, %Y')}"}}
        keys = [
            {
                "keyValue": {
                    "topLabel": f"Achieved",
                    "content": f"{prod.achieved} pairs | {prod.fg} cs",
                },
            },
            {
                "keyValue": {
                    "topLabel": f"Average",
                    "content": f"{average} pairs/hour",
                },
            },
        ]

        card["cards"][0]["sections"][0]["widgets"].extend(keys)
        card["cards"].insert(0, header)

    return card


def slack_api_template(prod: "Production", average: int, summary: dict = None) -> dict:
    """Slack block type message."""

    if not summary:
        # Hourly block
        msg = {
            "text": f"{prod.achieved} pairs | {prod.fg} cs",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Achieved\n*{prod.achieved}* _pairs_ | *{prod.fg}* _cs_",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Last Hour\n*{prod.phour}* _pairs_",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Average\n*{average}* _pairs/hour_",
                    },
                },
                {"type": "divider"},
            ],
            "summary": None,
        }
    else:
        # Summary block
        # top_prod: Production = summary["top"]
        msg = {
            "text": f"{prod.achieved} pairs | {prod.fg} cs",
            "blocks": [
                {
                    "type": "context",
                    "elements": [
                        {
                            "type": "mrkdwn",
                            "text": f"{prod.date.strftime('%A - %b %d, %Y')}",
                        },
                        {"type": "mrkdwn", "text": "  <!here>"},
                    ],
                },
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": f"{prod.achieved} pairs | {prod.fg} cs",
                    },
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Last Hour\n*{prod.phour}* _pairs_",
                    },
                },
                # { # Highest production is not that important.
                #     "type": "section",
                #     "text": {
                #         "type": "mrkdwn",
                #         "text": f"Highest\n*{top_prod.phour}* _pairs/hour_ `[{top_prod.hour_string}]`",
                #     },
                # },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"Average\n*{average}* _pairs/hour_",
                    },
                },
                {"type": "divider"},
            ],
            "summary": f"Summary\n```{summary['detail']}```",
        }

    return msg
