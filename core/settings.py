"""
Main configurations of the application, this file needed to be loaded initially.

"""

import configparser
import os

from .utils import logMessage
from . import ROOT, CONNECTION_STRING


if not os.path.exists(ROOT):
    os.makedirs(ROOT)

SLACK_WH = None
DISCORD_WH = None
GOOGLE_WH = None
SLACK_APP_TOKEN = None
SLACK_CHANNEL_ID = None

is_api_available = False

config = configparser.ConfigParser(interpolation=None)
exists = config.read(ROOT + "config.ini")

if exists:

    if config.has_section("SQL SERVER"):
        try:
            CONNECTION_STRING = (
                r"Driver={ODBC Driver 17 for SQL Server};"
                rf'Server={config["SQL SERVER"]["SERVER"]};'
                rf'Database={config["SQL SERVER"]["DATABASE"]};'
                rf'uid={config["SQL SERVER"]["UID"]};'
                rf'pwd={config["SQL SERVER"]["PWD"]};'
                r"Integrated Security=false;"
            )
        except KeyError as e:
            CONNECTION_STRING = None
            logMessage(f'Required key "{e.args[0]}" not found in configurations.')

    if config.has_section("SLACK APP"):
        try:
            SLACK_APP_TOKEN = config["SLACK APP"]["TOKEN"]
            SLACK_CHANNEL_ID = config["SLACK APP"]["CHANNEL_ID"]
            if not SLACK_APP_TOKEN.startswith("xoxb"):
                SLACK_APP_TOKEN = None
            else:
                is_api_available = True
        except KeyError as e:
            SLACK_APP_TOKEN = None
            logMessage(f'Required key "{e.args[0]}" not found in configurations.')

    if config.has_option("WEBHOOK", "SLACK"):
        value = config.get("WEBHOOK", "SLACK")
        if value.startswith("https://hooks.slack.com/services/"):
            SLACK_WH = value
            is_api_available = True

    if config.has_option("WEBHOOK", "DISCORD"):
        value = config.get("WEBHOOK", "DISCORD")
        if value.startswith("https://discord"):
            DISCORD_WH = value
            is_api_available = True

    if config.has_option("WEBHOOK", "GOOGLE"):
        value = config.get("WEBHOOK", "GOOGLE")
        if value.startswith("https://chat.googleapis.com"):
            GOOGLE_WH = value
            is_api_available = True

    if not is_api_available:
        logMessage("No valid webhook configurations found. Failed to sent report.")
else:
    CONNECTION_STRING = None
    logMessage("Configuration file missing, Exiting..!")  # Then do not run
