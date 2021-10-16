from json import dumps

from httplib2 import Http

durl = "https://discord.com/api/webhooks/897150490536718398/"


def webhook_send(prod, prod_date):
    """Webhook execution"""
    url = "https://chat.googleapis.com/v1/spaces/AAAAo58JrEA/messages?key=AIzaSyDdI0hCZtE6vySjMm-WEfRq3CPzqKqqsHI&token=4sp7avsoTMsgLH9FEMNiORLheMi1hLZj72O0HNFQMCI%3D"
    text_message = {"text": f"{prod}"}
    card_message = {
        "cards": [
            {
                "header": {"title": f"{prod}", "subtitle": f"{prod_date}"},
            }
        ]
    }

    message_headers = {"Content-Type": "application/json; charset=UTF-8"}

    http_obj = Http()

    response = http_obj.request(
        uri=url,
        method="POST",
        headers=message_headers,
        body=dumps(text_message),
    )
