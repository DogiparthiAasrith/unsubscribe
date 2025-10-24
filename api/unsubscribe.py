from flask import Flask, request, render_template_string
from pymongo import MongoClient
from urllib.parse import unquote
import os
import datetime

# Correctly initialize the Flask app
# The variable __name__ is a special Python variable that holds the name of the current module.
# Flask uses this to know where to look for resources like templates and static files.
app = Flask(__name__)

# MongoDB connection details from environment variables
MONGO_URI = os.environ.get("MONGO_URI")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME")

# Simple HTML template for the confirmation page
HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unsubscribe</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background-color: #f5f6fa;
            display: flex;
            justify-content: center;
            align-items: center;
            height: 100vh;
            margin: 0;
        }
        .card {
            background-color: #fff;
            padding: 40px 60px;
            border-radius: 16px;
            box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
            text-align: center;
            max-width: 400px;
        }
        h1 {
            color: #2f3640;
            font-size: 24px;
        }
        p {
            color: #555;
            margin-top: 10px;
            font-size: 16px;
        }
        .success { color: #27ae60; }
        .warning { color: #e67e22; }
        .error { color: #e74c3c; }
    </style>
</head>
<body>
    <div class="card">
        <h1 class="{{ status_class }}">{{ status_icon }} {{ status_title }}</h1>
        <p>{{ message }}</p>
    </div>
</body>
</html>
"""

@app.route("/unsubscribe", methods=["GET"])
def unsubscribe():
    email = unquote(request.args.get("email", "")).strip().lower()

    if not email:
        return render_template_string(
            HTML_TEMPLATE,
            status_class="error",
            status_icon="❌",
            status_title="Missing Email Parameter",
            message="No email address was provided."
        ), 400

    client = None  # Initialize client to None
    try:
        # Connect to MongoDB
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        unsubscribed_col = db.unsubscribed_emails

        # Check if email is already in the unsubscribed list
        existing = unsubscribed_col.find_one({"email": email})
        if existing:
            return render_template_string(
                HTML_TEMPLATE,
                status_class="warning",
                status_icon="⚠️",
                status_title="Already Unsubscribed",
                message=f"{email} is already in our unsubscribed list."
            ), 200

        # Insert the new email to be unsubscribed
        unsubscribed_col.insert_one({
            "email": email,
            # Use a reliable UTC timestamp
            "unsubscribed_at": datetime.datetime.now(datetime.timezone.utc)
        })

        return render_template_string(
            HTML_TEMPLATE,
            status_class="success",
            status_icon="✅",
            status_title="Unsubscribed Successfully!",
            message=f"{email} has been removed from our mailing list."
        ), 200

    except Exception as e:
        # Log the exception for debugging if you have a logging service
        return render_template_string(
            HTML_TEMPLATE,
            status_class="error",
            status_icon="❌",
            status_title="Server Error",
            message=f"An error occurred: {str(e)}"
        ), 500
    finally:
        # Ensure the client connection is closed
        if client:
            client.close()

# This block is for local development and will not be executed on Vercel
if __name__ == "__main__":
    # For local testing, you would need to set the environment variables.
    # For example, create a .env file and use a library like python-dotenv.
    # from dotenv import load_dotenv
    # load_dotenv()
    app.run(host="0.0.0.0", port=3000)
