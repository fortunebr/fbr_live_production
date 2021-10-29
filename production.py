from typing import Tuple

import configparser
import datetime
import pickle
import random

import requests
import pyodbc


root = "C:/fbr_production/"


class Production:
    def __init__(self, time=datetime.datetime.now(), achieved=0, fg=0, phour=0):
        self.time: datetime.datetime = time
        self.achieved = achieved
        self.fg = fg
        self.phour = phour

    @property
    def hour_string(self) -> str:
        from_hour = (self.time - datetime.timedelta(hours=1)).hour
        to_hour = self.time.hour
        return f"{from_hour:02d}-{to_hour:02d}"

    @property
    def date_string(self):
        return self.time.strftime("%b %d, %Y  %I:%M %p")

    @property
    def time_string(self):
        return self.time.strftime('%I:%M %p')


def getClockImage(hour: int) -> str:
    """Returns a clock image url"""

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
            return "https://i.imgur.com/lkwPtdD.jpg"


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


def logMessage(msg) -> None:
    """Program execution failure/exception logging"""

    global root

    with open(root + "log.txt", "a+") as f:
        f.write(f"{datetime.datetime.now()}  {msg}\n")


def load_configuration():
    """Load application's configurations"""

    global root

    config = configparser.ConfigParser(interpolation=None)
    exists = config.read(root + "config.ini")
    wh = {}
    if exists:
        try:
            connection_str = (
                r"Driver={ODBC Driver 17 for SQL Server};"
                rf'Server={config["SQL Server"]["SERVER"]};'
                rf'Database={config["SQL Server"]["DATABASE"]};'
                rf'uid={config["SQL Server"]["UID"]};'
                rf'pwd={config["SQL Server"]["PWD"]};'
                r"Integrated Security=false;"
            )
            if config.has_option("WEBHOOK", "DISCORD"):
                wh["DISCORD"] = config.get("WEBHOOK", "DISCORD")
            if config.has_option("WEBHOOK", "DISCORD_DAILY"):
                wh["DISCORD_DAILY"] = config.get("WEBHOOK", "DISCORD_DAILY")
            if config.has_option("WEBHOOK", "GOOGLE"):
                wh["GOOGLE"] = config.get("WEBHOOK", "GOOGLE")
            else:
                logMessage("Google webhook url not found.")
            return connection_str, wh
        except KeyError as e:
            logMessage(
                f'Required key "{e.args[0]}" not found in configurations.')

        except Exception as e:
            logMessage(f"Unknown exception occured.\n{e}")
    else:
        logMessage("Configuration file missing.")
        return None, wh


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


def webhook_google(prod: Production, data: dict[datetime.datetime, Production], url=None) -> None:
    """Google webhook execution"""

    if not url or not url.startswith("https://chat.googleapis.com"):
        return

    data_string = ""
    for p in data.values():
        data_string += f"{p.hour_string}: {p.phour}\n"

    text_message = {
        "text": f"*{prod.achieved} prs*  |  *{prod.fg} cs*  _- {prod.time_string} (+{prod.phour} prs)_"
    }
    try:
        res = requests.post(url, json=text_message)
        if res.status_code >= 400:
            logMessage(f"Google request failed: #{res.status_code}")
    except Exception as e:
        logMessage(f"Failed to send to google webhook\n{e}")


def getDailyProductionDate(cur_datetime) -> Tuple[datetime.datetime]:
    """Get production hours.

    8am to 8am (next day)
    """

    # New day production logging start at 9am (8am-9am)
    logtime = datetime.time(9)

    if cur_datetime.time() < logtime:
        sday = cur_datetime.date() - datetime.timedelta(days=1)
    else:
        sday = cur_datetime.date()

    eday = sday + datetime.timedelta(days=1)
    time_period = datetime.time(8, 0)
    start_date = datetime.datetime.combine(sday, time_period)
    end_date = datetime.datetime.combine(eday, time_period)
    return (start_date, end_date)


def getHourlyProductionLog() -> dict[datetime.datetime, Production]:
    """Get hourly logging from previously saved local file"""

    global root
    hourly_log = {}

    try:
        with open(root + "production.pickle", "rb") as f:
            hourly_log = pickle.load(f)
    except FileNotFoundError or EOFError:
        pass
    except Exception as e:
        logMessage(f"Failed to load previous production log.\n{e}")

    return hourly_log


def saveHourlyProductionLog(data: dict) -> None:
    """Saves the current latest log in the file"""

    global root
    try:
        with open(root + "production.pickle", "w+b") as f:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        logMessage(f"Failed to save current production log. \n{e}")


def discord_embed_h(prod: Production, data: dict[datetime.datetime, Production]) -> dict:
    """Discord embed for displaying hourly"""

    average_hprod = int(sum([p.phour for p in data.values()]) / len(data))

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
                        "inline": True
                    },
                    {
                        "name": "Average",
                        "value": f"**{average_hprod}** pairs/hour",
                        "inline": True
                    },
                ],
                "timestamp": f"{prod.time.utcnow()}",
                "footer": {
                    "text": "Fortune Br",
                    "icon_url": "https://i.imgur.com/7SwrwqC.jpg",
                },
            }
        ]
    }
    return embed


def discord_embed_summary(prod: Production, data: dict[datetime.datetime, Production]) -> dict:
    """Discord embed for displaying hourly"""

    average_hprod = int(sum([p.phour for p in data.values()]) / len(data))
    data_string = "```\n"
    for p in data.values():
        data_string += f"{p.hour_string}  :  {p.achieved}"
        data_string += " " * (8 - len(str(p.achieved)))
        data_string += f"+{p.phour}\n"
    data_string += "```"
    highest_prod = max(data.values(), key=lambda p: p.phour)
    first_prod = min(data.values(), key=lambda p: p.time)
    # productions = list(data.values()) # Sort for getting top5, last5
    # productions.sort(key=lambda x: x.phour)

    embed = {
        "embeds": [
            {
                "color": f"{randomColor()}",
                "author": {
                    "name": f"{first_prod.time.strftime('%A - %b %d, %Y')}"
                },
                "thumbnail": {
                    "url": "https://i.imgur.com/e22h9tf.png",
                },
                "fields": [
                    {
                        "name": "Total Achieved",
                        "value": f"**{prod.achieved}** pairs | **{prod.fg}** cs",
                    },
                    {
                        "name": "Highest (per hour)",
                        "value": f"**{highest_prod.phour}** pairs\n{highest_prod.hour_string}",
                        "inline": True
                    },
                    {
                        "name": "Average",
                        "value": f"**{average_hprod}** pairs/hour",
                        "inline": True
                    },
                    {
                        "name": "Report",
                        "value": data_string
                    },
                ],
                "footer": {
                    "text": "Fortune Br",
                    "icon_url": "https://i.imgur.com/7SwrwqC.jpg",
                },
                "timestamp": f"{prod.time.utcnow()}",
            }
        ]
    }
    return embed


def main(now: datetime.datetime = datetime.datetime.now()) -> None:
    """Connect to SQL Server and execute the query to count rows.

    * Total number of queries to run: 3
    * Send results to Discord/Google webhook
    """

    con_str, wh = load_configuration()
    query = "select count(*) from [barcode].[dbo].[tbl_ProductionScan] where [prod_date] between ? and ?"
    query_fg = "select count(*) from [barcode].[dbo].[tbl_StorageScan] where [store_date] between ? and ?"

    if not con_str:
        return

    # Connecting SQL Server
    try:
        conn = pyodbc.connect(con_str)
        if not conn:
            raise ConnectionError("Failed to connect SQL Server.")
        cursor = conn.cursor()
    except ConnectionError:
        logMessage("Failed to connect SQL Server")
    except Exception as e:
        logMessage(f"Connection to server failed.\n{e}")

    start_date, end_date = getDailyProductionDate(now)

    hourly_edate = now.replace(minute=0, second=0, microsecond=0)
    hourly_sdate = hourly_edate - datetime.timedelta(hours=1)

    if now.hour == 9:
        prod_log = {}
    else:
        prod_log = getHourlyProductionLog()
        if len(prod_log) > 0:
            min_time = min(prod_log.keys())
            if (now.date() != min_time.date()):
                if now.hour > 8 or (min_time.date() < now.date() - datetime.timedelta(days=1)):
                    prod_log = {}
            else:
                if min_time.hour <= 8 and now.hour > 8:
                    prod_log = {}

    prod_now = Production(time=now)
    # Query execution
    try:
        # Current hour production
        qresult_hour = cursor.execute(
            query, hourly_sdate, hourly_edate)
        prod_now.phour = qresult_hour.fetchone()[0]
        # Production upto this hour
        qresult_cur = cursor.execute(
            query, start_date, hourly_edate)
        prod_now.achieved = qresult_cur.fetchone()[0]
        # FG production upto this hour
        qresult_fg = cursor.execute(
            query_fg, start_date, hourly_edate)
        prod_now.fg = qresult_fg.fetchone()[0]

        prod_log[now] = prod_now
        saveHourlyProductionLog(prod_log)

    except Exception as e:
        logMessage(f"Query execution failed.\n{e}")

    if prod_now.achieved > 100 and prod_log:
        # Send to webhooks
        if prod_now.phour > 100:
            # Hourly report
            embed = discord_embed_h(prod=prod_now, data=prod_log)
            discord_url = wh.get("DISCORD", None)
            webhook_discord(embed=embed, url=discord_url)

            if not (now.weekday() == 6 and now.time() > datetime.time(8, 15)):
                if not (now.weekday() == 0 and now.time() <= datetime.time(7, 59)):
                    # If not sunday, send to google webhook
                    webhook_google(prod=prod_now, data=prod_log,
                                   url=wh.get("GOOGLE", None))
        if now.hour == 8:
            # Day summary
            embed = discord_embed_summary(prod=prod_now, data=prod_log)
            webhook_discord(embed=embed, url=wh.get("DISCORD_DAILY", None))


if __name__ == "__main__":
    now = datetime.datetime.now()
    try:
        main(now)
    except Exception as e:
        logMessage(f"Main program execution failed.\n{e}")
# Sunday is not always holiday for plant,
    # if now.weekday() == 6 and now.time() > datetime.time(8, 15):
    #     # Sunday is holiday
    #     pass
    # else:
    #     main(now)
