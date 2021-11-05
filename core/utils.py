"""
Utilities

"""

import configparser
import datetime
from typing import TYPE_CHECKING, Tuple

import pickle

from . import root

if TYPE_CHECKING:
    from .production import Production


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


def logMessage(msg) -> None:
    """Program execution failure/exception logging"""

    with open(root + "log.txt", "a+") as f:
        f.write(f"{datetime.datetime.now()}  {msg}\n")


def load_configuration():
    """Load application's configurations"""

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
            if config.has_option("WEBHOOK", "SLACK"):
                wh["SLACK"] = config.get("WEBHOOK", "SLACK")
            if config.has_option("WEBHOOK", "GOOGLE"):
                wh["GOOGLE"] = config.get("WEBHOOK", "GOOGLE")

            if not wh.keys():
                logMessage("Cannot find a webhook to send report to!")

            return connection_str, wh
        except KeyError as e:
            logMessage(f'Required key "{e.args[0]}" not found in configurations.')

        except Exception as e:
            logMessage(f"Unknown exception occured.\n{e}")
    else:
        logMessage("Configuration file missing.")
        return None, wh


def loadHourlyProductionLog() -> dict[datetime.datetime, "Production"]:
    """Get hourly logging from previously saved local file"""

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

    try:
        with open(root + "production.pickle", "w+b") as f:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        logMessage(f"Failed to save current production log. \n{e}")
