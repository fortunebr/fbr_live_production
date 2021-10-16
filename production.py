import pyodbc
import datetime
from json import dumps
from httplib2 import Http
import configparser
import requests


con_str = (
    r"Driver={ODBC Driver 17 for SQL Server};"
    r"Server=stallion;"
    r"Database=barcode;"
    r"uid=sa;"
    r"pwd=barcode@123;"
    r"Integrated Security=false;"
)

query = "select count(*) from [barcode].[dbo].[tbl_ProductionScan] where [prod_date] between ? and ?"


def webhook_google(prod, prod_date, prod_log):
    """Google webhook execution"""
    url = "https://chat.googleapis.com/v1/spaces/AAAAo58JrEA/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=4sp7avsoTMsgLH9FEMNiORLheMi1hLZj72O0HNFQMCI%3D"
    message_headers = {"Content-Type": "application/json; charset=UTF-8"}
    http_obj = Http()
    # formatted_datettime = prod_date.strftime("%b %d, %Y - %I:%M:%S %p")
    # text_message = {"text": f"{prod}"}
    card_message = {
        "cards": [
            {
                # "header": {
                #     "title": f'<font color="#0d4cde"><b>{prod}</b></font>',
                #     # "subtitle": f"{formatted_datettime}",
                # },
                "sections": [
                    {
                        "header": f"{prod_date.strftime('%H:%M+%S')}",
                        "widgets": [
                            {
                                "textParagraph": {
                                    "text": f'<font color="#0d4cde"><b>{prod}</b></font>',
                                }
                            },
                        ],
                    },
                    {
                        "widgets": [
                            # {
                            #     "keyValue": {
                            #         "topLabel": f"{formatted_datettime}",
                            #         "content": f'<font color="#0d4cde"><b>{prod}</b></font>',
                            #     }
                            # },
                            {
                                "textParagraph": {
                                    "text": f"<i><u>Hourly</u></i>\n{prod_log}",
                                }
                            },
                        ]
                    },
                ]
            }
        ]
    }

    try:
        response = http_obj.request(
            uri=url,
            method="POST",
            headers=message_headers,
            body=dumps(card_message),
        )
    except:
        with open("E:/log.txt", "a") as f:
            f.write(f"{prod_date}  Failed to send to google webhook\n")
            f.write(f"{prod_date}  {e}\n\n")


def webhook_discord(prod, prod_date, prod_log):
    """Discrod webhook execution"""
    url = "https://discord.com/api/webhooks/897150490536718398/_ay4C-asZPGNa6TFnTVBT-IrqlJUlafC4Y4pld2y6O8NL2x5sr69CWb1ezIPEVc6Sy1d"

    embed = {
        "embeds": [
            {
                "title": f"Live Production: {prod}",
                "description": f"```\n{prod_log}```",
                "timestamp": f"{prod_date.utcnow()}",
                "color": "3447003",
            }
        ]
    }
    try:
        res = requests.post(url, json=embed)

        if res.status_code >= 400:
            with open("E:/log.txt", "a") as f:
                f.write(f"{prod_date}  Discord request failed: #{res.status_code}\n")
                f.write(f"{prod_date}\n")
    except Exception as e:
        with open("E:/log.txt", "a") as f:
            f.write(f"{prod_date}  Failed to send to discord webhook\n")
            f.write(f"{prod_date}  {e}\n")


def getDailyProductionDate(cur_datetime):
    logtime = datetime.time(8, 30)  # New day production logging start at 9am (8am-9am)

    if cur_datetime.time() < logtime:
        sday = cur_datetime.date() - datetime.timedelta(days=1)
    else:
        sday = cur_datetime.date()

    eday = sday + datetime.timedelta(days=1)

    time_period = datetime.time(8, 0)

    start_date = datetime.datetime.combine(sday, time_period)
    end_date = datetime.datetime.combine(eday, time_period)

    return (start_date, end_date)


def logProduction(production, proddate, shour, ehour):
    """Log hourly productionuction"""
    conf = configparser.ConfigParser(interpolation=None)
    day_section = f"{proddate.date()}"
    hour_key = f"{shour:02d}-{ehour:02d}"
    exists = conf.read("E:/production.ini")  # Load existing ini

    is_logged = conf.has_section(day_section)
    if not is_logged:
        conf.add_section(day_section)
    conf.set(day_section, hour_key, f"{production}")

    f = open("E:/production.ini", "w")
    conf.write(f)
    f.close()

    hourly_log = ""
    for hr, prd in dict(conf.items(day_section)).items():
        hourly_log += f"{hr}: {prd}\n"

    return hourly_log


if __name__ == "__main__":
    prod_time = datetime.datetime.now()
    # Connecting server...
    try:
        conn = pyodbc.connect(con_str)
        cursor = conn.cursor()
    except Exception as e:
        with open("E:/log.txt", "a") as f:
            f.write(f"{prod_time}  Connection to server failed\n")
            f.write(f"{prod_time}  {e}\n\n")

    start_date, end_date = getDailyProductionDate(prod_time)
    ehour = prod_time.time().hour
    hourly_sdate = prod_time.replace(hour=ehour - 1, minute=0, second=0, microsecond=0)
    hourly_edate = prod_time.replace(hour=ehour, minute=0, second=0, microsecond=0)

    # Executing query and fetching data and prepare to send to wh
    try:
        result = cursor.execute(query, start_date, end_date)
        production = result.fetchone()[0]
        result2 = cursor.execute(query, hourly_sdate, hourly_edate)
        hourly_production = result2.fetchone()[0]

        prod_log = logProduction(hourly_production, start_date, ehour - 1, ehour)
        webhook_google(production, prod_time, prod_log)
        webhook_discord(prod=production, prod_date=prod_time, prod_log=prod_log)
    except Exception as e:
        print(e)
        with open("E:/log.txt", "a") as f:
            f.write(f"{prod_time}  Query execution failed\n")
            f.write(f"{prod_time}  {e}\n\n")

    with open("E:/log.txt", "a") as f:
        f.write(f"{prod_time}  Execution completed\n\n")
