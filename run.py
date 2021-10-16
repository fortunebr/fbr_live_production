import pyodbc
import datetime
import time
from prod_card import webhook_send

con_str = (
    r"Driver={ODBC Driver 17 for SQL Server};"
    r"Server=SERVER_NAME;"
    r"Database=DATABASE_NAME;"
    r"uid=USERNAME;"
    r"pwd=PASSWORD;"
    r"Integrated Security=false;"
)

query = "select count(*) from [barcode].[dbo].[tbl_ProductionScan] where [prod_date] between ? and ?"

try:
    conn = pyodbc.connect(con_str)
    cursor = conn.cursor()
except Exception as e:
    print(e)



def getDailyDate(date):
    s_day = date
    e_day = datetime.timedelta(days=1) + date

    time_period = datetime.time(8, 0)

    start_date = datetime.datetime.combine(s_day, time_period)
    end_date = datetime.datetime.combine(e_day, time_period)

    return (start_date, end_date)



d = datetime.date.today()
start_date, end_date = getDailyDate(d)

try:
    result = cursor.execute(query, start_date, end_date)
    production = result.fetchone()[0]
    print(production)
    # cur_time = datetime.datetime.now().strftime("%b %d, %Y - %I:%M %p")
    # webhook_send(prod=production, prod_date=cur_time)
except Exception as e:
        print("Connection closed:\n")
        print(e)


print("Success")
