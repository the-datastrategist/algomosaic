from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import configs

SLACK_BOT_TOKEN = configs.SLACK_BOT_TOKEN


class messageObject:
    """Post a message to Slack

    Args:
        token (str): API token assigned to SlackBot. By default, this is
            pulled from configs.py, but can also be overwritten.

    Returns:
        None

    """
    def __init__(self, token=SLACK_BOT_TOKEN):
        self.client = WebClient(token=token)

    def send(self, msg, channel="#general"):
        try:
            self.response = self.client.chat_postMessage(
                channel=channel if channel.startswith('#') else '#' + channel,
                text=msg
            )
            assert self.response["message"]["text"] == msg
        except SlackApiError as e:
            # You will get a SlackApiError if "ok" is False
            assert e.response["ok"] is False
            assert e.response["error"]  # str like 'invalid_auth', 'channel_not_found'
            print(f"Got an error: {e.response['error']}")
