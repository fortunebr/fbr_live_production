"""
Production information.

"""

import datetime
from typing import Iterable


class Production:
    """Model for storing hourly production details."""

    def __init__(
        self,
        date=datetime.datetime.now(),
        time=datetime.datetime.now(),
        achieved: int = 0,
        fg: int = 0,
        phour: int = 0,
    ):

        self.time: datetime.datetime = time
        """Current hour datetime object."""
        self.date: datetime.datetime = date
        """Production day datetime object"""
        self.achieved: int = achieved
        """Production achieved upto this hour."""
        self.fg: int = fg
        """FG Production upto this hour."""
        self.phour: int = phour
        """Production on this hour."""

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
        return self.time.strftime("%I:%M %p")


def averageHourlyProduction(productions: Iterable[Production]) -> int:
    """Returns average production per hour."""

    return int(sum([p.phour for p in productions]) / len(productions))


def generateProductionSummary(data: dict[datetime.datetime, Production]) -> dict:
    """Returns production summary report"""

    summary = {}
    summary["top"] = max(data.values(), key=lambda p: p.phour)
    summary["detail"] = ""
    for p in data.values():
        summary["detail"] += f"{p.hour_string}  :  {p.achieved}"
        summary["detail"] += " " * (8 - len(str(p.achieved)))
        summary["detail"] += f"+{p.phour}\n"

    # productions = list(data.values()) # Sort for getting top5, last5
    # productions.sort(key=lambda x: x.phour)

    return summary
