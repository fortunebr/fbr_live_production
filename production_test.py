from typing import Tuple

import configparser
import datetime
import os
import pickle
import random

import requests
import pyodbc


class Production:
    def __init__(self, time=datetime.datetime.now(), achieved=0, fg=0, phour=0):
        self.time: datetime.datetime = time
        self.achieved = achieved
        self.fg = fg
        self.phour = phour

    @property
    def hour(self) -> int:
        return self.time.hour

    @property
    def day(self) -> int:
        return self.time.day

    @property
    def hour_string(self) -> str:
        return f"{self.time.hour - 1:02d}-{self.time.hour:02d}"

    @property
    def date_string(self):
        return self.time.strftime("%b %d, %Y  %I:%M %p")


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
            return "https://listimg.pinclipart.com/picdir/s/195-1954098_24-hour-clock-spiral-free-printable-template-download.png"


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

    with open(os.getcwd() + "/fbr_plog.txt", "a+") as f:
        f.write(f"{datetime.datetime.now()}  {msg}\n")


def load_configuration():
    """Load application's configurations"""

    config = configparser.ConfigParser(interpolation=None)
    exists = config.read("fbr_config.ini")
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
            if config.has_option("WEBHOOK", "GOOGLE"):
                wh["GOOGLE"] = config.get("WEBHOOK", "GOOGLE")
            else:
                logMessage("Webhook url not found.")
            return connection_str, wh
        except KeyError as e:
            print(f'Required key "{e.args[0]}" not found in configurations.')
            logMessage(
                f'Required key "{e.args[0]}" not found in configurations.')

        except Exception as e:
            print(f"Unknown exception occured\n{e}")
            logMessage(f"Unknown exception occured.\n{e}")
    else:
        print("Configuration file missing.")
        logMessage("Configuration file missing.")
        return None, wh


def webhook_discord(embed: dict, url=None) -> None:
    """Discrod webhook execution"""

    if not url or not url.startswith("https"):
        url = "https://discordapp.com/api/webhooks/897150490536718398/_ay4C-asZPGNa6TFnTVBT-IrqlJUlafC4Y4pld2y6O8NL2x5sr69CWb1ezIPEVc6Sy1d"

    try:
        res = requests.post(url, json=embed)
        if res.status_code == 400:
            logMessage(f"Discord request failed: #{res.status_code}")
    except Exception as e:
        logMessage(f"Failed to send to discord webhook\n{e}")


def webhook_google(production, date, history, fg_prod, url=""):
    """Google webhook execution"""

    if not url or not url.startswith("https"):
        return
    time = date.strftime('%I:%M %p')

    # formatted_datettime = prod_date.strftime("%b %d, %Y - %I:%M:%S %p")
    text_message = {
        "text": f"*{production} prs*  |  *{fg_prod} cs*  _- {time}_\n```\nHourly\n{history}```"
    }
    try:
        res = requests.post(url, json=text_message)
        if res.status_code != 200:
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

    hourly_log = {}

    try:
        with open(os.getcwd() + "/production.pickle", "rb") as f:
            hourly_log = pickle.load(f)
    except FileNotFoundError or EOFError:
        pass
    except Exception as e:
        logMessage(f"Failed to load previous production log.\n{e}")

    return hourly_log


def saveHourlyProductionLog(data) -> None:
    """Saves the current latest log in the file"""

    try:
        with open(os.getcwd() + "/production.pickle", "w+b") as f:
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
                    "url": f"{getClockImage(prod.hour)}",
                },
                "fields": [
                    {
                        "name": "Achieved",
                        "value": f"{prod.production} pairs | {prod.fg} cs",
                    },
                    {
                        "name": "Last Hour",
                        "value": f"{prod.phour} pairs",
                        "inline": True
                    },
                    {
                        "name": "Average",
                        "value": f"{average_hprod} pairs/hour",
                        "inline": True
                    },
                ],
                "footer": {
                    "text": f"{prod.date_string}",
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
    data_string + "```"
    productions = list(data.values())
    productions.sort(key=lambda x: x.phour)

    embed = {
        "embeds": [
            {
                "color": f"{randomColor()}",
                "author": {
                    "name": f"{productions[0].time.strftime('%A - %b %d, %Y')}"
                },
                "thumbnail": {
                    "url": "https://i.imgur.com/e22h9tf.png",
                },
                "fields": [
                    {
                        "name": "Total Achieved",
                        "value": f"**{prod.production}** pairs | **{prod.fg}** cs",
                    },
                    {
                        "name": "Highest (per hour)",
                        "value": f"**{productions[-1].phour}** pairs\n{productions[-1].hour_string}",
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
                "timestamp": f"{prod.time.utcnow()}",
                "footer": {
                    "text": "Fortune Br",
                    "icon_url": "https://i.imgur.com/7SwrwqC.jpg",
                },
            }
        ]
    }
    return embed


def google_text_h(data) -> str:
    """For displaying hourly log"""

    data_string = ""
    for key, item in data.items():
        data_string += f"{key-1:02d}-{key:02d}: {item[1]}\n"
    return data_string


def main() -> None:
    """Main program"""
    now = datetime.datetime.now()
    query = "select count(*) from [barcode].[dbo].[tbl_ProductionScan] where [prod_date] between ? and ?"
    query_fg = "select count(*) from [barcode].[dbo].[tbl_StorageScan] where [store_date] between ? and ?"
    con_str, wh = load_configuration()

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
    now_hour = now.time().hour
    hourly_sdate = now.replace(
        hour=now_hour - 1, minute=0, second=0, microsecond=0)
    hourly_edate = now.replace(minute=0, second=0, microsecond=0)

    if now_hour == 9:
        prod_log = {}
    else:
        prod_log = getHourlyProductionLog()
        max_time = max(list(prod_log.keys()))
        min_time = min(list(prod_log.keys()))
        if ((max_time.hour <= 23 and min_time.date != now.date)
                or (min_time.date <= (now.date - datetime.timedelta(days=2)))):
            prod_log = {}

    prod_now = Production(time=now)

    try:
        qresult_hour = cursor.execute(
            query, hourly_sdate, hourly_edate)  # hour based
        prod_now.phour = qresult_hour.fetchone()[0]

        qresult_cur = cursor.execute(
            query, start_date, hourly_edate)  # 8 - cur_hour
        prod_now.achieved = qresult_cur.fetchone()[0]

        qresult_fg = cursor.execute(
            query_fg, start_date, hourly_edate)  # 8 - 8
        prod_now.fg = qresult_fg.fetchone()[0]

        prod_log[now] = prod_now
        saveHourlyProductionLog(prod_log)

    except Exception as e:
        logMessage(f"Query execution failed.\n{e}")

    if prod_now.phour > 0 and prod_now.achieved > 0 and prod_log:
        # Send to webhooks

        embed = discord_embed_h(prod=prod_now, data=prod_log)
        webhook_discord(embed=embed, url=wh.get("DISCORD", ""))

        # webhook_google(url=wh.get("GOOGLE", ""), production=cur_production, date=now, history=hourlyLogDisplay2(prod_log), fg_prod=cur_fgproduction)


if __name__ == "__main__":
    now = datetime.datetime.now()

    if now.weekday() == 6 and now.time() > datetime.time(8, 15):
        # Sunday is holiday
        pass
    else:
        main()
