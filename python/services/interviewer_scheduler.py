import requests
from datetime import datetime
from app.core.config import settings
from app.services.auth_service import get_graph_token
from app.services.scheduler_service import schedule_bot_join

def schedule_interview(
        candidate_email: str, 
        start_time: datetime, 
        end_time: datetime
):
    token = get_graph_token()
    organizer = settings.TEAMS_ORGANIZER_EMAIL

    headers = {
        "Authorization": f"Bearer {token}", 
        "Content-Type": "application/json"
    }

#  Step 1: Get or Create "AI Interviews" secondary calendar 
# - The Teams app ONLY monitors the primary Exchange calendar
# - By creating the event in a secondary calendar, the organizer
# - (dev.test) gets NO popups or reminders in Teams 
# - However, the candidate still receives the real calendar invite and gets the proper native Teams popup!

    calendars_url = f"https://graph.microsoft.com/v1.0/users/{organizer}/calendars"
    calendars_response = requests.get(calendars_url, headers=headers)

    calendar_id = None
    if calendars_response.status_code == 200:
        for cal in calendars_response.json().get("value", []):
            if cal.get("name") == "AI Interviews":
                calendar_id = cal.get("id")
                break

    if not calendar_id:
        print("Creating 'AI Interviews' secondary calendar...")
        new_cal_response = requests.post(calendars_url, headers = headers, json = {"name": "AI Interviews"})

        if new_cal_response.status_code == 201:
            calendar_id = new_cal_response.json().get("id")
            print("Successfully created calendar:", calendar_id)
        else:
            print("Warning: Failed to create secondary calendar:", new_cal_response.text)

    # Use the secondary calendar endpoint if successful, else fallback to default
    if calendar_id:
        event_url = f"https://graph.microsoft.com/v1.0/users/{organizer}/calendars/{calendar_id}/events"
    else:
        event_url = f"https://graph.microsoft.com/v1.0/users/{organizer}/events"

    # Step 2: Create the Event & Teams Meeting (for the candidate)
    # - isOnlineMeeting = True generates native Teams meeting
    # - Candidate gets added as attendee and gets the POPUP

    event_payload = {
        "subject": "AI Interview Session", 

        "start": {
            "dateTime": start_time.isoformat(), 
            "timeZone": "UTC"
        }, 

        "end": {
            "dateTime": end_time.isoformat(), 
            "timeZone": "UTC"
        }, 

        # This makes it a PROPER native Teams meeting so the candidate gets a popup!
        "isOnlineMeeting": True, 
        "onlineMeetingProvider": "teamsForBusiness",

        # No attendees - just creating the meeting link
        "attendees": [
            {
                "emailAddress": {
                    "address": candidate_email, 
                    "name": candidate_email
                }, 
                "type": "required"
            }
        ], 
        
        "isReminderOn": False, 
        "showAs": "free", 
        "responseRequested": False
    }

    event_response = requests.post(event_url, headers = headers, json = event_payload)

    print("Secondary Calendar Event Status:", event_response.status_code)
    # print("Calendar Event Response:", response.text[:500])

    if event_response.status_code != 201:
        raise Exception(f"Failed to create event: {event_response.text}")
    
    event = event_response.json()
    join_url = event["onlineMeeting"]["joinUrl"]

    print("Meeting Join URL:", join_url)

    # Step 3: Create Placeholder Event in Primary Calendar for HR
    # - No attendees (so candidate doesn't get duplicate invite)
    # - isOnlineMeeting=False(so dev.test gets No Popup)
    # - But it is visually on dev.test's main calendar!

    if calendar_id:
        primary_event_url = f"https://graph.microsoft.com/v1.0/users/{organizer}/events"

        primary_payload = {
            "subject": f"AI Interview - {candidate_email}", 
            "start": {
                "dateTime": start_time.isoformat(), 
                "timeZone": "UTC"
            }, 

            "end": {
                "dateTime": end_time.isoformat(), 
                "timeZone": "UTC"
            }, 

            "location": {
                "displayName": join_url
            }, 
            "attendees": [], 
            "isOnlineMeeting": False, # False means no popup for HR!
            "isReminderOn": True, 
            "showAs": "busy", 
        }

        primary_response = requests.post(primary_event_url, headers = headers, json = primary_payload)
        print("Primary Calendar Status (for HR):", primary_response.status_code)

    # Step 4: Schedule bot to auto-join at the meeting start time
    
    schedule_bot_join(
        join_url = join_url, 
        start_time = start_time
    )

    print("Scheduling bot join")
    print("Join URL:", join_url)
    print("Start Time:", start_time)

    return {
        "meeting_link": join_url, 
        "event_id": event["id"], 
        "candidate_email": candidate_email, 
        "start_time": start_time.isoformat(), 
        "end_time": end_time.isoformat()
    }