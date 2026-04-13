import requests
from app.core.config import settings

def trigger_bot_join(join_url):

    print("Triggering Node Teams Bot")

    payload = {
        "meetingUrl": join_url
    }

    response = requests.post(
        f"{settings.BOT_SERVICE_URL}/bot-test/join-meeting-test", 
        json = payload
    )

    print("Bot service response:", response.text)

    if "application/json" in response.headers.get("content-type", ""):
        return response.json()
    else:
        return {"message": response.text}
