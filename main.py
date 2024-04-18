from whatsapp import WhatsApp, Message
from json import load, loads, dump, dumps
import logging

try:
    with open("creds.json", "r") as f:
        creds = load(f)
except FileNotFoundError:
    creds = {}

whatsapp = WhatsApp(creds['token'],  phone_number_id=creds['numberid'], logger=True, update_check=True)
verify_token = creds['verify-token']

@whatsapp.on_event
async def on_event(event):
    print(event)


if __name__ == "__main__":
    context = ('/etc/letsencrypt/live/surajbhari.info/fullchain.pem', '/etc/letsencrypt/live/surajbhari.info/privkey.pem')
    
    try:
        whatsapp.run(port=creds['port'], host=creds['host'], ssl_certfile=context[0], ssl_keyfile=context[1])
    except FileNotFoundError:
        print("SSL Certificate not found")
        whatsapp.run(port=creds['port'], host=creds['host'])