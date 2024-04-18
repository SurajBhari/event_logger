from whatsapp import WhatsApp, Message
from json import load, loads, dump, dumps
import logging
import os
from time import time
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
app = Flask(__name__)

VERIFY_TOKEN = creds['verify-token']

# make and verify data.json
if "data.json" not in os.listdir("."):
    with open("data.json", "w") as f:
        dump({}, f)
    sdata = {}
else:
    with open("data.json", "r") as f:
        sdata = load(f)

if "locations" not in sdata:
    sdata['locations'] = [] # store location . {'time': '1713403389', 'sender':'7742055965', 'location': {'latitude': '12.9715987', 'longitude': '77.5945627'}}

if "visits" not in sdata:
    sdata['visits'] = [] # store visits . {'time': '1713403389', 'sender':'7742055965', 'message_content': 'I am here'}



def update_data():
    with open("data.json", "w") as f:
        dump(sdata, f, indent=4)
# Logging
"""
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)"""

@app.get("/webhook")
def verify_token():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        logging.info("Verified webhook")
        challenge = request.args.get("hub.challenge")
        return str(challenge)
    logging.error("Webhook Verification failed")
    return "Invalid verification token"


@app.post("/webhook")
def hook():
    # Handle Webhook Subscriptions
    data = request.get_json()
    # store the data to file for vertification 
    if data is None:
        return Response(status=200)
    logging.info("Received webhook data: %s", data)
    changed_field = messenger.changed_field(data)
    if changed_field == "messages":
        new_message = messenger.is_message(data)
        if new_message:
            msg = Message(instance=messenger, data=data)
            mobile = msg.sender
            name = msg.name
            message_type = msg.type
            logging.info(
                f"New Message; sender:{mobile} name:{name} type:{message_type}"
            )
            if message_type == "text":
                message = msg.content
                name = msg.name
                logging.info("Message: %s", message)
                m = Message(instance=messenger, to=mobile,
                            content=message)
                m.send()

            elif message_type == "interactive":
                message_response = msg.interactive
                if message_response is None:
                    return Response(status=400)
                interactive_type = message_response.get("type")
                message_id = message_response[interactive_type]["id"]
                message_text = message_response[interactive_type]["title"]
                logging.info(
                    f"Interactive Message; {message_id}: {message_text}")

            elif message_type == "location":
                message_location = msg.location
                if message_location is None:
                    return Response(status=400)
                if "name" in message_location:
                    m = Message(instance=messenger, to=mobile, content=f"❌ Only give your current location.")
                    m.send()
                    return "OK", 200
                message_latitude = message_location["latitude"]
                message_longitude = message_location["longitude"]
                logging.info("Location: %s, %s",
                             message_latitude, message_longitude)
                sdata['locations'].append({
                    'time': int(time()),
                    'sender': mobile,
                    'location': {
                        'latitude': message_latitude,
                        'longitude': message_longitude
                    }
                })
                update_data()
                m = Message(instance=messenger, to=mobile, content=f"✔ Location: Updated at {time()}.")
                m.send()
        else:
            delivery = messenger.get_delivery(data)
            if delivery:
                logging.info(f"Message : {delivery}")
            else:
                logging.info("No new message")
    return "OK", 200


if __name__ == "__main__":
    context = ('/etc/letsencrypt/live/surajbhari.info/fullchain.pem', '/etc/letsencrypt/live/surajbhari.info/privkey.pem')
    
    try:
        app.run(port=creds['port'], host=creds['host'], ssl_context=context, debug=True)
    except FileNotFoundError:
        print("SSL Certificate not found")
        app.run(port=creds['port'], host=creds['host'], debug=True)