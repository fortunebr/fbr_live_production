"""
Utilities

"""

import datetime
from typing import TYPE_CHECKING, Tuple

import pickle

from .settings import PRODUCTION_START_HOUR
from .log_me import logMessage
from . import ROOT


if TYPE_CHECKING:
    from .production import Production


def loadHourlyProductionLog() -> dict[datetime.datetime, "Production"]:
    """Get hourly logging from previously saved local file"""

    hourly_log = {}

    try:
        with open(ROOT + "production.pickle", "rb") as f:
            hourly_log = pickle.load(f)
    except FileNotFoundError or EOFError:
        pass
    except Exception as e:
        logMessage(f"Failed to load previous production log.\n{e}")

    return hourly_log


def saveHourlyProductionLog(data: dict) -> None:
    """Saves the current latest log in the file"""

    try:
        with open(ROOT + "production.pickle", "w+b") as f:
            pickle.dump(data, f, pickle.HIGHEST_PROTOCOL)
    except Exception as e:
        logMessage(f"Failed to save current production log. \n{e}")


def getDailyProductionDate(cur_datetime) -> Tuple[datetime.datetime]:
    """Get production hours.

    8am to 8am (next day)
    """

    # New day production logging start at 9am (8am-9am) by default
    logtime = datetime.time(PRODUCTION_START_HOUR + 1)

    if cur_datetime.time() < logtime:
        sday = cur_datetime.date() - datetime.timedelta(days=1)
    else:
        sday = cur_datetime.date()

    eday = sday + datetime.timedelta(days=1)
    time_period = datetime.time(PRODUCTION_START_HOUR, 0)
    start_date = datetime.datetime.combine(sday, time_period)
    end_date = datetime.datetime.combine(eday, time_period)
    return (start_date, end_date)
