"""
Message templates for each webhooks.

1. Discord
2. Slack
3. Google Chat

"""


import random
from typing import TYPE_CHECKING


if TYPE_CHECKING:
    from core.production import Production


def randomColor() -> int:
    """Returns a random discord integer color"""

    num = random.randint(0, 9)
    match num:
        case 0:
            return 5763719  # Green
        case 1:
            return 16705372  # Yellow
        case 2:
            return 15548997  # Red
        case 3:
            return 15418782  # Rose
        case 4:
            return 5793266  # Purple
        case 5:
            return 1146986  # Dark Green
        case 6:
            return 15277667  # Pink
        case 7:
            return 15105570  # Orange
        case _:
            return 3447003  # Blue


def getClockImage(hour: int) -> str:
    """Returns a clock image url for the given hour."""

    match hour:
        case  1 | 13:
            return "https://i.imgur.com/QXIxBcr.png"
        case  2 | 14:
            return "https://i.imgur.com/sO7GiQh.png"
        case  3 | 15:
            return "https://i.imgur.com/FmZrupJ.png"
        case  4 | 16:
            return "https://i.imgur.com/zNeOJSL.png"
        case  5 | 17:
            return "https://i.imgur.com/S4UPkPd.png"
        case  6 | 18:
            return "https://i.imgur.com/lC2E845.png"
        case  7 | 19:
            return "https://i.imgur.com/wcj8ESf.png"
        case  8 | 20:
            return "https://i.imgur.com/GVsFAgG.png"
        case  9 | 21:
            return "https://i.imgur.com/SPHh9BK.png"
        case  10 | 22:
            return "https://i.imgur.com/rQDK31v.png"
        case  11 | 23:
            return "https://i.imgur.com/e8WYgmU.png"
        case  12 | 0:
            return "https://i.imgur.com/oqb1oQz.png"
        case  _:
            return "https://i.imgur.com/lkwPtdD.jpg"


def discord_template(prod: "Production", average: int, summary: dict=None) -> dict:
    """Discord embed type meesage."""

    if not summary:
        # Hourly embed
        embed = {
            "embeds": [
                {
                    "color": f"{randomColor()}",
                    "thumbnail": {
                        "url": f"{getClockImage(prod.time.hour)}",
                    },
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
                        {"name": "Report", "value": "```{}```".format(summary["detail"])},
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


def slack_template(prod: "Production", average: int,summary: dict=None) -> dict:
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
            }
        ]

        card["cards"][0]["sections"][0]["widgets"].extend(keys)
        card["cards"].insert(0, header)

    return card