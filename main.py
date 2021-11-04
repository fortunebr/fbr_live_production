"""
Get production information from SQL Server and send
the report to webhooks (Discord, Slack, Google)

Made with ❤️ from kalaLokia
"""


import datetime

import pyodbc

from core.production import (
    Production,
    averageHourlyProduction,
    generateProductionSummary,
)
from core.utils import (
    getDailyProductionDate,
    load_configuration,
    logMessage,
    loadHourlyProductionLog,
    saveHourlyProductionLog,
)
from core.webhook import webhook_slack, webhook_discord, webhook_google, webhook_google2
from templates import slack_template, discord_template, google_template


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
        prod_log = loadHourlyProductionLog()
        if len(prod_log) > 0:
            min_time = min(prod_log.keys())
            if now.date() != min_time.date():
                if now.hour > 8 or (
                    min_time.date() < now.date() - datetime.timedelta(days=1)
                ):
                    prod_log = {}
            else:
                if min_time.hour <= 8 and now.hour > 8:
                    prod_log = {}

    prod_now = Production(time=hourly_edate)
    # Query execution
    try:
        # Current hour production
        qresult_hour = cursor.execute(query, hourly_sdate, hourly_edate)
        prod_now.phour = qresult_hour.fetchone()[0]
        # Production upto this hour
        qresult_cur = cursor.execute(query, start_date, hourly_edate)
        prod_now.achieved = qresult_cur.fetchone()[0]
        # FG production upto this hour
        qresult_fg = cursor.execute(query_fg, start_date, hourly_edate)
        prod_now.fg = qresult_fg.fetchone()[0]

        prod_log[hourly_edate] = prod_now
        saveHourlyProductionLog(prod_log)

    except Exception as e:
        logMessage(f"Query execution failed.\n{e}")

    if prod_now.achieved > 100 and prod_log:
        # Send to webhooks
        average_production = averageHourlyProduction(prod_log.values())
        summary = None

        if now.hour == 8 and len(prod_log) > 5:
            summary = generateProductionSummary(prod_log)

        if prod_now.phour > 100 or (now.hour == 8 and len(prod_log) > 5):
            # Hourly report

            embed = discord_template(prod_now, average_production, summary)
            block = slack_template(prod_now, average_production, summary)
            card = google_template(prod_now, average_production, summary)

            webhook_discord(embed=embed, url=wh.get("DISCORD", None))
            webhook_slack(block=block, url=wh.get("SLACK", None))
            # ToDo: Test google card looks
            # webhook_google(card=card, url=wh.get("GOOGLE", None))

            if not (now.weekday() == 6 and now.time() > datetime.time(8, 15)):
                if not (now.weekday() == 0 and now.time() <= datetime.time(7, 59)):
                    # If not sunday, send to google webhook
                    webhook_google2(prod_now, wh.ger("GOOGLE", None))


if __name__ == "__main__":
    now = datetime.datetime.now()

    # ToDo: Remove try-catch expression here
    try:
        main(now)
    except Exception as e:
        logMessage(f"Main program execution failed.\n{e}")
