from flask import Flask, request, jsonify
from pymongo import MongoClient
import os

app = Flask(__name__)

# Environment variables
MONGO_URI = os.environ.get("MONGO_URI")
DB_NAME = os.environ.get("MONGO_DB_NAME")

# Connect safely
try:
    client = MongoClient(MONGO_URI)
    db = client[DB_NAME]
    unsubscribed = db.get_collection("unsubscribed_emails")
except Exception as e:
    print(f"MongoDB connection failed: {e}")
    unsubscribed = None

@app.route("/unsubscribe")
def unsubscribe():
    if unsubscribed is None:
        return "Error: Cannot connect to database.", 500

    email = request.args.get("email")
    if not email:
        return "Error: No email provided.", 400

    try:
        unsubscribed.update_one(
            {"email": email},
            {"$set": {"unsubscribed": True}},
            upsert=True
        )
        return f"{email} has been unsubscribed successfully!"
    except Exception as e:
        return f"Database error: {e}", 500
