from flask import Flask, request, render_template_string
from pymongo import MongoClient
from urllib.parse import unquote
import os
import datetime

# This app instance is what Vercel looks for.
app = Flask(__name__)

# These MUST be set in your Vercel Project's Environment Variables settings.
MONGO_URI = os.environ.get("MONGO_URI")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME")

HTML_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Unsubscribe</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f5f6fa; display: flex; justify-content: center; align-items: center; height: 100vh; margin: 0; }
        .card { background-color: #fff; padding: 40px 60px; border-radius: 16px; box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1); text-align: center; max-width: 400px; }
        h1 { color: #2f3640; font-size: 24px; }
        p { color: #555; margin-top: 10px; font-size: 16px; }
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
    # Check if environment variables are loaded. This is a critical check.
    if not MONGO_URI or not MONGO_DB_NAME:
        return render_template_string(
            HTML_TEMPLATE,
            status_class="error",
            status_icon="❌",
            status_title="Configuration Error",
            message="The server is missing database configuration."
        ), 500

    email = unquote(request.args.get("email", "")).strip().lower()

    if not email:
        return render_template_string(
            HTML_TEMPLATE,
            status_class="error",
            status_icon="❌",
            status_title="Missing Email Parameter",
            message="No email address was provided."
        ), 400

    client = None
    try:
        client = MongoClient(MONGO_URI)
        db = client[MONGO_DB_NAME]
        unsubscribed_col = db.unsubscribed_emails

        existing = unsubscribed_col.find_one({"email": email})
        if existing:
            return render_template_string(
                HTML_TEMPLATE,
                status_class="warning",
                status_icon="⚠️",
                status_title="Already Unsubscribed",
                message=f"{email} is already in our unsubscribed list."
            ), 200

        unsubscribed_col.insert_one({
            "email": email,
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
        # In a real app, you would log the error `e` for debugging
        # but show a generic message to the user.
        return render_template_string(
            HTML_TEMPLATE,
            status_class="error",
            status_icon="❌",
            status_title="Server Error",
            message="An unexpected error occurred. Please try again later."
        ), 500
    finally:
        if client:
            client.close()

# This part is ignored by Vercel but useful for local testing
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=3000)
