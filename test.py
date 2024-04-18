from whatsapp import WhatsApp, Message
from json import load, loads, dump, dumps
import logging
from whatsapp import WhatsApp, Message
from flask import Flask, request, Response
try:
    with open("creds.json", "r") as f:
        creds = load(f)
except FileNotFoundError:
    creds = {}

print(creds)
messenger = WhatsApp(creds['token'],  phone_number_id=creds['numberid'], logger=True, update_check=True)
# Initialize Flask App


with open("test.json", "r") as f:
    data = load(f)

m = Message(instance=messenger, data=data)
print(m.sender)
