# Event Logger 

This is a basic whatsapp application that uses [whatsapp library](https://github.com/filipporomani/whatsapp) to store user's location from time to time and log events in a database.


## Installation
```bash
pip install -r requirements.txt
```

## Running
```bash
python hook.py
```


It only runs if you have a ssl certificate as whatsapp only serves webhook events on https.

## Usage
Modify the creds.json file to your liking. follow [this video](https://www.youtube.com/watch?v=d6lNxP2gadA) to get the credentials.