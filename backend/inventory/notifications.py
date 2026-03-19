import requests
import logging

EXPO_PUSH_URL = 'https://exp.host/--/api/v2/push/send'

logger = logging.getLogger(__name__)

def send_push_notification(tokens: list, title: str, body: str, data: dict = None):
    """
    Send a push notification to one or more Expo push tokens.

    Args:
        tokens:  List of ExponentPushToken[...] strings
        title:   Notification title shown on the device
        body:    Notification body text
        data:    Optional dict passed to the app (used for navigation)
    """
    if not tokens:
        return None

    messages = [
        {
            'to': token,
            'title': title,
            'body': body,
            'data': data or {},
            'sound': 'default',
            'priority': 'high',
        }
        for token in tokens
    ]

    response = requests.post(
        EXPO_PUSH_URL,
        json=messages,
        headers={
            'Accept': 'application/json',
            'Accept-Encoding': 'gzip, deflate',
            'Content-Type': 'application/json',
        },
        timeout=10,
    )

    result = response.json()

    # Log any per-token delivery errors
    for i, receipt in enumerate(result.get('data', [])):
        if receipt.get('status') == 'error':
            logger.error(f'Push error for token {tokens[i]}: {receipt.get("message")}')

    return result