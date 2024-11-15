import os
import requests
import json
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from slack_bolt.adapter.flask import SlackRequestHandler
from slack_bolt import App
from dotenv import find_dotenv, load_dotenv
from flask import Flask, request
from functions import answer_tech_question, answer_with_history

# Load environment variables from .env file
load_dotenv(find_dotenv())

# Set Slack API credentials
SLACK_BOT_TOKEN = os.environ["SLACK_BOT_TOKEN"]
SLACK_SIGNING_SECRET = os.environ["SLACK_SIGNING_SECRET"]
SLACK_BOT_USER_ID = os.environ["SLACK_BOT_USER_ID"]

config = {
    "LLM_MODEL": os.environ['LLM_MODEL'],
}    

# Initialize the Slack app
app = App(token=SLACK_BOT_TOKEN)

# Initialize the Flask app
# Flask is a web application framework written in Python
flask_app = Flask(__name__)
handler = SlackRequestHandler(app)


@flask_app.route("/")
def hello_world():
    response = answer_tech_question("How to become a great developer?", "HTML")
    print(response)
    return response

def get_bot_user_id():
    """
    Get the bot user ID using the Slack API.
    Returns:
        str: The bot user ID.
    """
    try:
        # Initialize the Slack client with your bot token
        slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
        response = slack_client.auth_test()
        return response["user_id"]
    except SlackApiError as e:
        print(f"Error: {e}")

def fetch_thread_replies(channel_id, ts):
    headers = {
        "Authorization": f"Bearer {SLACK_BOT_TOKEN}"
    }
    params = {
        "channel": channel_id,
        "ts": ts,
        "inclusive": "true",
        "limit": 100  # Adjust the limit as needed
    }
    response = requests.post("https://slack.com/api/conversations.replies", headers=headers, params=params)
    return response.json()

# def fetch_thread_replies(channel, thread_ts):
#     """
#     Fetch all thread replies in a channel using the Slack API.
#     Returns:
#         messages: all threads replies.
#     """
#     try:
#         slack_client = WebClient(token=os.environ["SLACK_BOT_TOKEN"])
#         result = slack_client.conversations_history(
#             channel=channel,
#             ts=thread_ts,
#             inclusive=False,
#             limit=1000  # Adjust the limit as per your needs
#         )
#         print(result["messages"])
#         return result["messages"]
#     except SlackApiError as e:
#         print(f"Error: {e}")


@app.event("app_mention")
def handle_mentions(body, say):
    """
    Event listener for mentions in Slack.
    When the bot is mentioned, this function processes the text and sends a response.

    Args:
        body (dict): The event data received from Slack.
        say (callable): A function for sending a response to the channel.
    """
    text = body["event"]["text"]

    event = body["event"]
    thread_ts = event.get("thread_ts", None) or event["ts"]

    mention = f"<@{SLACK_BOT_USER_ID}>"
    text = text.replace(mention, "").strip()

    if text.lower().find("--allow-history--") != -1:
        history_data = fetch_thread_replies(event["channel"], thread_ts)
        filtered_history_data = map(lambda x: x["text"], history_data["messages"])
        response = answer_with_history("Please summary the conversation", list(filtered_history_data), config['LLM_MODEL'])
        say(
            text=response, 
            thread_ts=thread_ts
        )
    else:
        response = answer_tech_question(text, config['LLM_MODEL'])
        say(
            text=response, 
            thread_ts=thread_ts
        )


@app.command("/dev-bot")
def handle_hello_command(body, ack, say):
    # Acknowledge the command request
    ack()

    print(body)
    new_config = {
        "LLM_MODEL": body['text'],
    }
    config.update(new_config)

    # Respond to the user
    say(f"Hi <@{body['user_id']}>! I updated llm model to {body['text']}")


@flask_app.route("/slack/events", methods=["POST"])
def slack_events():
    """
    Route for handling Slack events.
    This function passes the incoming HTTP request to the SlackRequestHandler for processing.

    Returns:
        Response: The result of handling the request.
    """
    return handler.handle(request)


# Run the Flask app
if __name__ == "__main__":
    flask_app.run(host='0.0.0.0', port=5002)