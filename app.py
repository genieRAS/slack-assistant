import os
from dotenv import find_dotenv, load_dotenv
from flask import Flask, request

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Initialize the Flask app
# Flask is a web application framework written in Python
flask_app = Flask(__name__)

@flask_app.route("/")
def hello_world():
    response = "Hello World!"
    return response

# Run the Flask app
if __name__ == "__main__":
    flask_app.run(host='0.0.0.0', port=5002)