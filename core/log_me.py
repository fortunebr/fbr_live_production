import datetime

from . import ROOT


def logMessage(msg) -> None:
    """Program execution failure/exception logging"""

    with open(ROOT + "log.txt", "a+") as f:
        f.write(f"{datetime.datetime.now()}  {msg}\n")
