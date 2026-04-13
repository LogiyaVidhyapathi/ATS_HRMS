import uuid
import requests
from datetime import datetime

from app.core.config import settings
from app.services.auth_service import get_graph_token
from app.services.scheduler_service import schedule_bot_join
from app.db.mongo import interviews

def schedule_interview(
        candidate_email: str, 
        start_time: datetime, 
        end_time: datetime
):
    token = get_graph_token()

    organizer = settings.TEAMS_ORGANIZER_EMAIL

    url = f"https://graph.microsoft.com/v1.0/users/{organizer}/events?sendUpdates=all"

    headers = {
        "Authorization": f"Bearer {token}", 
        "Content-Type": "application/json"
    }

    payload = {
        "subject": "AI Interview Session", 

        "transactionId": str(uuid.uuid4()),

        "start": {
            "dateTime": start_time.isoformat(), 
            "timeZone": "UTC"
        }, 

        "end": {
            "dateTime": end_time.isoformat(), 
            "timeZone": "UTC"
        }, 

        "isOnlineMeeting": True, 
        "onlineMeetingProvider": "teamsForBusiness", 

        "responseRequested": True, 
        "allowNewTimeProposals": True,

        "attendees": [
            {
                "emailAddress": {
                    "address": candidate_email, 
                    "name": candidate_email
                }, 
                "type": "required"
            }
        ],
    }

    response = requests.post(url, headers = headers, json = payload)

    print("Status:", response.status_code)
    print("Graph Response:", response.text)

    if response.status_code != 201:
        raise Exception(response.text)
    
    event = response.json()

    join_url = event["onlineMeeting"]["joinUrl"]

    # interviews.insert_one({
    #     "candidate_email": candidate_email, 
    #     "join_url": join_url, 
    #     "event_id": event["id"], 
    #     "start_time": start_time, 
    #     "status": "scheduled"
    # })

    schedule_bot_join(
        join_url = join_url, 
        start_time = start_time
    )

    return {
        "meeting_link": event["onlineMeeting"]["joinUrl"], 
        "event_id": event["id"]
    }