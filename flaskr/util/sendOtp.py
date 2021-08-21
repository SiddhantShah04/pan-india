import os
from twilio.rest import Client
from os import environ


# Find your Account SID and Auth Token at twilio.com/console
# and set the environment variables. See http://twil.io/secure
# account_sid = environ.get("TWILIO_ACCOUNT_SID")
# auth_token = environ.get("TWILIO_AUTH_TOKEN")
# client = Client(account_sid, auth_token)


def sendMessgae(number, message):
    # message = client.messages.create(
    #     body=message,
    #     from_=environ.get("TWILIO_NUMBER"),
    #     to=number
    # )
    message = ""
    return(message)
