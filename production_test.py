from typing import Tuple

import configparser
import datetime
import os
import pickle

import requests
import pyodbc


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
            if config.has_option("WEBOHOOK", "DISCORD"):
                wh["DISCORD"] = config.get("WEBOHOOK", "DISCORD")
            if config.has_option("WEBOHOOK", "GOOGLE"):
                wh["GOOGLE"] = config.get("WEBOHOOK", "GOOGLE")
            return connection_str, wh
        except KeyError as e:
            print(f'Required key "{e.args[0]}" not found in configurations.')
            logMessage(f'Required key "{e.args[0]}" not found in configurations.')

        except Exception as e:
            print(f"Unknown exception occured\n{e}")
            logMessage(f"Unknown exception occured.\n{e}")
    else:
        print("Configuration file missing.")
        logMessage("Configuration file missing.")
        return None, wh


def webhook_discord(production, date, history, fg_prod=None,url="") -> None:
    """Discrod webhook execution"""
    fg_production = ""
    if fg_prod:
        fg_production += f"  |  {fg_prod} cs"

    if not url or not url.startswith("https"):
        url = "https://discordapp.com/api/webhooks/897150490536718398/_ay4C-asZPGNa6TFnTVBT-IrqlJUlafC4Y4pld2y6O8NL2x5sr69CWb1ezIPEVc6Sy1d"

    embed = {
        "embeds": [
            {
                "title": f"{production} prs" + fg_production,
                "description": f"```\n{history}```",
                "timestamp": f"{date.utcnow()}",
                "color": "3447003",
            }
        ]
    }
    try:
        res = requests.post(url, json=embed)
        if res.status_code != 400:
            logMessage(f"Discord request failed: #{res.status_code}")
    except Exception as e:
        logMessage(f"Failed to send to discord webhook\n{e}")


def webhook_google(production, date, history, fg_prod,url=""):
    """Google webhook execution"""

    if not url or not url.startswith("https"):
        url = "https://chat.googleapis.com/v1/spaces/AAAAkkgKKdY/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=VFQoL9u_SjlMQDBwmWdFYOp1LTP914sn-7uwMGQVTNY%3D"
    
    time = date.strftime('%I:%M %p')

    # formatted_datettime = prod_date.strftime("%b %d, %Y - %I:%M:%S %p")
    text_message = {
        "text": f"*{production} prs*  |  *{fg_prod} cs*  _- {time}_\n```\nHourly\n{history}```"
    }
    try:
        res = requests.post(url,json=text_message)
        if res.status_code != 200:
            logMessage(f"Google request failed: #{res.status_code}")
    except Exception as e:
        logMessage(f"Failed to send to google webhook\n{e}")


def getDailyProductionDate(cur_datetime) -> Tuple[datetime.datetime]:
    """Get production hours.

    8am to 8am (next day)
    """

    logtime = datetime.time(9)  # New day production logging start at 9am (8am-9am)

    if cur_datetime.time() < logtime:
        sday = cur_datetime.date() - datetime.timedelta(days=1)
    else:
        sday = cur_datetime.date()

    eday = sday + datetime.timedelta(days=1)
    time_period = datetime.time(8, 0)
    start_date = datetime.datetime.combine(sday, time_period)
    end_date = datetime.datetime.combine(eday, time_period)
    return (start_date, end_date)


def getHourlyProductionLog() -> dict:
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


def hourlyLogDisplay(data) -> str:
    """For displaying hourly log"""

    data_string = ""
    for key, item in data.items():
        data_string += f"08-{key:02d}: {item[0]}"
        data_string += " " * (6 - len(str(item[0])))
        data_string += f"+{item[1]}\n"

    return data_string

def hourlyLogDisplay2(data) -> str:
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
    hourly_sdate = now.replace(hour=now_hour - 1, minute=0, second=0, microsecond=0)
    hourly_edate = now.replace(minute=0, second=0, microsecond=0)

    if now_hour == 9:
        prod_log = {}
    else:
        prod_log = getHourlyProductionLog()

    cur_production = 0
    cur_production_h = 0

    try:
        qresult_hour = cursor.execute(query, hourly_sdate, hourly_edate) # hour based
        cur_production_h = qresult_hour.fetchone()[0]

        qresult_cur = cursor.execute(query, start_date, hourly_edate) # 8 - cur_hour
        cur_production = qresult_cur.fetchone()[0]
        
        qresult_fg = cursor.execute(query_fg, start_date, hourly_edate)  # 8 - 8
        cur_fgproduction = qresult_fg.fetchone()[0]

        prod_log[now_hour] = (cur_production, cur_production_h)
        saveHourlyProductionLog(prod_log)

    except Exception as e:
        logMessage(f"Query execution failed.\n{e}")

    if cur_production_h > 0 and cur_production > 0 and prod_log:
        # Send to webhooks

        discord_url = wh.get("DISCORD", "")
        webhook_discord(
            url="", production=cur_production, date=now, history=hourlyLogDisplay(prod_log), fg_prod=cur_fgproduction
        )
        google_url = wh.get("GOOGLE", "")
        webhook_google(
            url="", production=cur_production, date=now, history=hourlyLogDisplay2(prod_log), fg_prod=cur_fgproduction
        )


if __name__ == "__main__":
    now = datetime.datetime.now()

    if now.weekday() == 6 and now.time() > datetime.time(8, 15):
        # Sunday is holiday
        pass
    else:
        # import timeit
        # print(timeit.timeit (main, number=1)) # 0.55 - 0.75 sec
        main()

