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
app = Flask(__name__)

VERIFY_TOKEN = creds['verify-token']

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
    with open("test.json", "w+") as f:
        dump(data, f, indent=4)
    if data is None:
        return Response(status=200)
    logging.info("Received webhook data: %s", data)
    changed_field = messenger.changed_field(data)
    if changed_field == "messages":
        new_message = messenger.is_message(data)
        if new_message:
            msg = Message(instance=messenger, data=data)
            for att in dir(msg):
                print(att, getattr(msg,att))
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
                            content="Hello World")
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
                message_latitude = message_location["latitude"]
                message_longitude = message_location["longitude"]
                logging.info("Location: %s, %s",
                             message_latitude, message_longitude)

            elif message_type == "image":
                image = msg.image
                if image is None:
                    return Response(status=400)
                image_id, mime_type = image["id"], image["mime_type"]
                image_url = messenger.query_media_url(image_id)
                if image_url is None:
                    return Response(status=400)
                image_filename = messenger.download_media(image_url, mime_type)
                logging.info(f"{mobile} sent image {image_filename}")
            else:
                logging.info(f"{mobile} sent {message_type} ")
                logging.info(data)
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