import datetime
import requests
import random

prod = 10522
fg_prod = 522
data = {
    9: (1173, 1173),
    10: (2230, 1057),
    11: (3337, 1107),
    12: (4577, 1240),
    13: (5896, 1319),
    14: (6343, 447),
    15: (7490, 1147),
    16: (8934, 1444),
    17: (10522, 1588),
    18: (11874, 1352),
    19: (13163, 1289),
    20: (14650, 1487),
    21: (15665, 1015),
}


class Production:
    def __init__(self, production, fg, phour):
        self.production = production
        self.fg = fg
        self.last_hour = phour


def getClockImage(hour: int):
    match hour:
        case  1 | 13:
            return "https://i.imgur.com/QXIxBcr.png"
        case   2 | 14:
            return "https://i.imgur.com/sO7GiQh.png"
        case   3 | 15:
            return "https://i.imgur.com/FmZrupJ.png"
        case   4 | 16:
            return "https://i.imgur.com/zNeOJSL.png"
        case   5 | 17:
            return "https://i.imgur.com/S4UPkPd.png"
        case   6 | 18:
            return "https://i.imgur.com/lC2E845.png"
        case   7 | 19:
            return "https://i.imgur.com/wcj8ESf.png"
        case   8 | 20:
            return "https://i.imgur.com/GVsFAgG.png"
        case   9 | 21:
            return "https://i.imgur.com/SPHh9BK.png"
        case   10 | 22:
            return "https://i.imgur.com/rQDK31v.png"
        case   11 | 23:
            return "https://i.imgur.com/e8WYgmU.png"
        case   12 | 0:
            return "https://i.imgur.com/oqb1oQz.png"
        case _:
            return "https://listimg.pinclipart.com/picdir/s/195-1954098_24-hour-clock-spiral-free-printable-template-download.png"


def hourlyLogDisplay(data: dict) -> str:
    """For displaying hourly log"""

    data_string = "```\n"
    for key, item in data.items():
        data_string += f"08-{key:02d}  :  {item[0]}"
        data_string += " " * (8 - len(str(item[0])))
        data_string += f"+{item[1]}\n"
    return data_string + "```"


def randomColor() -> int:
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


def webhook_discord(embed) -> None:
    url = "https://discordapp.com/api/webhooks/897150490536718398/_ay4C-asZPGNa6TFnTVBT-IrqlJUlafC4Y4pld2y6O8NL2x5sr69CWb1ezIPEVc6Sy1d"

    try:
        res = requests.post(url, json=embed)
        if res.status_code == 400:
            print(f"Discord request failed: #{res.status_code}")
            print(res.__dict__)
    except Exception as e:
        print(f"Failed to send to discord webhook\n{e}")


def discord_embed_h(date: datetime.datetime, prod: Production, data: dict):
    date_string = date.strftime("%b %d, %Y  %I:%M %p")
    average_hprod = int(sum([v[1] for v in data.values()]) / len(data))

    embed = {
        "embeds": [
            {
                "color": f"{randomColor()}",
                "thumbnail": {
                    "url": "https://i.imgur.com/e22h9tf.png",
                },
                "fields": [
                    {
                        "name": "Achieved",
                        "value": f"{prod.production} pairs | {prod.fg} cs",
                    },
                    {
                        "name": "Last Hour",
                        "value": f"{prod.last_hour} pairs",
                        "inline": True
                    },
                    {
                        "name": "Average",
                        "value": f"{average_hprod} pairs/hour",
                        "inline": True
                    },
                ],
                "footer": {
                    "text": f"{date_string}",
                    "icon_url": "https://i.imgur.com/7SwrwqC.jpg",
                },
            }
        ]
    }
    return embed


def discord_embed_summary(date: datetime.datetime, prod: Production, data: dict):
    date_string = date.strftime("%b %d, %Y  %I:%M %p")
    average_hprod = int(sum([v[1] for v in data.values()]) / len(data))

    embed = {
        "embeds": [
            {
                "color": f"{randomColor()}",
                "thumbnail": {
                    "url": "https://i.imgur.com/e22h9tf.png",
                },
                "author": {
                    "name": f"{now.strftime('%A - %b %d, %Y')}"
                },
                "fields": [
                    {
                        "name": "Total Achieved",
                        "value": f"**{prod.production}** pairs | **{prod.fg}** cs",
                    },
                    {
                        "name": "Highest",
                        "value": f"**{prod.last_hour}** pairs \n11am-12pm",
                        "inline": True
                    },
                    {
                        "name": "Average",
                        "value": f"{average_hprod} pairs/hour",
                        "inline": True
                    },
                    {
                        "name": "Report",
                        "value": hourlyLogDisplay(data),
                    }
                ],
                "timestamp": f"{date.utcnow()}",
                "footer": {
                    "text": f"Fortune Br",
                    "icon_url": "https://i.imgur.com/7SwrwqC.jpg",
                },
            }
        ]
    }
    return embed


if __name__ == "__main__":
    now = datetime.datetime.now()
    production = Production(production=prod, fg=fg_prod, phour=1122)
    embed = discord_embed_summary(now, production, data)
    webhook_discord(embed=embed)
