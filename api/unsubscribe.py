from flask import Flask, request
from pymongo import MongoClient
import os

app = Flask(__name__)

MONGO_URI = os.environ.get("MONGO_URI")
DB_NAME = os.environ.get("MONGO_DB_NAME")

client = MongoClient(MONGO_URI)
db = client[DB_NAME]
unsubscribed = db.get_collection("unsubscribed_emails")

@app.route("/unsubscribe")
def unsubscribe():
    email = request.args.get("email")
    if not email:
        return "No email provided.", 400
    unsubscribed.update_one({"email": email}, {"$set": {"unsubscribed": True}}, upsert=True)
    return f"{email} has been unsubscribed successfully!"
