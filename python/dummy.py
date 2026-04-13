import requests
from datetime import datetime, timedelta
from app.core.config import settings
from app.services.auth_service import get_graph_token

GRAPH_URL = "https://graph.microsoft.com/v1.0"

def create_teams_meeting():
    token = get_graph_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    meeting_payload = {
        "subject": "AI Interview Session",
        "startDateTime": datetime.utcnow().isoformat(),
        "endDateTime": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
    }

    response = requests.post(
        f"{GRAPH_URL}/me/onlineMeetings",
        headers=headers,
        json=meeting_payload
    )

    response.raise_for_status()
    return response.json()



from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    # Azure AD
    CLIENT_ID: str
    CLIENT_SECRET: str
    TENANT_ID: str

    # App
    ENV: str = "development"
    API_PREFIX: str = "/api"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings():
    return Settings()


settings = get_settings()



import requests
from app.core.config import settings

def get_graph_token():
    url = f"https://login.microsoftonline.com/{settings.TENANT_ID}/oauth2/v2.0/token"

    payload = {
        "client_id": settings.CLIENT_ID,
        "client_secret": settings.CLIENT_SECRET,
        "scope": "https://graph.microsoft.com/.default",
        "grant_type": "client_credentials"
    }

    response = requests.post(url, data=payload)
    response.raise_for_status()

    return response.json()["access_token"]


https://login.microsoftonline.com/organizations/oauth2/token



from fastapi import APIRouter
from app.services.teams_service import create_teams_meeting

router = APIRouter()

@router.post("/start-interview")
def start_interview():
    meeting = create_teams_meeting()
    return {
        "join_url": meeting["joinWebUrl"],
        "meeting_id": meeting["id"]
    }



from fastapi import FastAPI
from app.api.interview_routes import router as interview_router

app = FastAPI(title="AI Interview Platform")

app.include_router(interview_router, prefix="/api")






import requests
from app.services.auth_service import get_graph_token
from app.core.config import settings
from datetime import datetime, timedelta

def create_teams_meeting():
    token = get_graph_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    start = datetime.utcnow() + timedelta(minutes=5)
    end = start + timedelta(minutes=30)

    payload = {
        "subject": "AI Interview Session",
        "startDateTime": start.isoformat() + "Z",
        "endDateTime": end.isoformat() + "Z"
    }

    url = (
        f"https://graph.microsoft.com/v1.0/users/"
        f"{settings.TEAMS_ORGANIZER_EMAIL}/onlineMeetings"
    )

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code != 201:
        raise Exception(response.text)

    return response.json()



import requests
from app.services.auth_service import get_graph_token
from app.core.config import settings

def create_teams_meeting():
    token = get_graph_token()

    url = f"https://graph.microsoft.com/v1.0/users/{settings.teams_organizer_email}/onlineMeetings"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "subject": "AI Interview Session",
        "startDateTime": "2026-02-02T14:00:00Z",
        "endDateTime": "2026-02-02T14:30:00Z"
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code >= 400:
        raise Exception(response.text)

    return response.json()





import requests
from datetime import datetime, timedelta
from app.core.config import settings
from app.services.auth_service import get_graph_token


def create_teams_meeting():

    token = get_graph_token()

    url = f"https://graph.microsoft.com/v1.0/users/{settings.teams_organizer_email}/onlineMeetings"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    start = datetime.utcnow().replace(microsecond=0) + timedelta(minutes=5)
    end = start + timedelta(minutes=30)

    meeting_payload = {
        "subject": "AI Interview Session",
        "startDateTime": start.isoformat() + "Z",
        "endDateTime": end.isoformat() + "Z",
        "isOnlineMeeting": True,
        "onlineMeetingProvider": "teamsForBusiness"
    }

    response = requests.post(
        url,
        headers=headers,
        json=meeting_payload
    )

    print("Status:", response.status_code)
    print("Graph Response:", response.text)

    if response.status_code != 201:
        raise Exception(response.text)

    return response.json()


    token = response.json()["access_token"]

    print("ACCESS TOKEN:", token)   # 👈 add this

url = "https://graph.microsoft.com/v1.0/me/onlineMeetings"





import msal
from app.core.config import settings

def get_graph_token():
    authority = f"https://login.microsoftonline.com/{settings.tenant_id}"

    app = msal.ConfidentialClientApplication(
        client_id=settings.client_id,
        client_credential=settings.client_secret,
        authority=authority
    )

    # Application permission scope
    result = app.acquire_token_for_client(
        scopes=["https://graph.microsoft.com/.default"]
    )

    if "access_token" not in result:
        raise Exception(f"Failed to get token: {result}")

    print("Access token acquired successfully")

    return result["access_token"]


import msal
from fastapi import APIRouter
from fastapi.responses import RedirectResponse
from app.core.config import settings

router = APIRouter()

AUTHORITY = f"https://login.microsoftonline.com/{settings.tenant_id}"

SCOPES = [
    "User.Read",
    "OnlineMeetings.ReadWrite"
]

msal_app = msal.ConfidentialClientApplication(
    client_id=settings.client_id,
    authority=AUTHORITY,
    client_credential=settings.client_secret
)




from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse, JSONResponse
from app.core.config import settings
from app.services.auth_service import msal_app, SCOPES

router = APIRouter()


# -----------------------------------------
# 🔐 LOGIN ROUTE
# Redirect user to Microsoft Login Page
# -----------------------------------------
@router.get("/login")
def login():

    auth_url = msal_app.get_authorization_request_url(
        scopes=SCOPES,
        redirect_uri=settings.redirect_uri
    )

    return RedirectResponse(auth_url)


# -----------------------------------------
# 🔐 CALLBACK ROUTE
# Microsoft redirects here after login
# -----------------------------------------
@router.get("/auth/callback")
def auth_callback(code: str):

    result = msal_app.acquire_token_by_authorization_code(
        code=code,
        scopes=SCOPES,
        redirect_uri=settings.redirect_uri
    )

    # ❌ Error Handling
    if "access_token" not in result:
        return JSONResponse(
            status_code=400,
            content={"error": result}
        )

    access_token = result["access_token"]

    return {
        "message": "Login successful",
        "access_token": access_token
    }

redirect_uri: str = "http://localhost:8000/auth/callback"


from fastapi import FastAPI
from app.api import auth_routes

app = FastAPI()

app.include_router(auth_routes.router)





import msal
from app.core.config import settings

# ✅ Global authority
AUTHORITY = f"https://login.microsoftonline.com/{settings.tenant_id}"

# ✅ Global scopes
SCOPES = [
    "User.Read",
    "OnlineMeetings.ReadWrite"
]

# ✅ Global MSAL app instance
msal_app = msal.ConfidentialClientApplication(
    client_id=settings.client_id,
    client_credential=settings.client_secret,
    authority=AUTHORITY
)


from fastapi import APIRouter
from fastapi.responses import RedirectResponse, JSONResponse
from app.core.config import settings
from app.services.auth_service import msal_app, SCOPES

router = APIRouter()


@router.get("/login")
def login():

    auth_url = msal_app.get_authorization_request_url(
        scopes=SCOPES,
        redirect_uri=settings.redirect_uri
    )

    return RedirectResponse(auth_url)


@router.get("/auth/callback")
def auth_callback(code: str):

    result = msal_app.acquire_token_by_authorization_code(
        code=code,
        scopes=SCOPES,
        redirect_uri=settings.redirect_uri
    )

    if "access_token" not in result:
        return JSONResponse(
            status_code=400,
            content={"error": result}
        )

    access_token = result["access_token"]

    return {
        "message": "Login successful",
        "access_token": access_token
    }

















from fastapi import APIRouter, Response
from fastapi.responses import RedirectResponse, JSONResponse
from app.core.config import settings
from app.services.auth_service import msal_app, SCOPES

router = APIRouter()


@router.get("/login")
def login():

    auth_url = msal_app.get_authorization_request_url(
        scopes=SCOPES,
        redirect_uri=settings.redirect_uri
    )

    return RedirectResponse(auth_url)


@router.get("/auth/callback")
def auth_callback(code: str):

    result = msal_app.acquire_token_by_authorization_code(
        code=code,
        scopes=SCOPES,
        redirect_uri=settings.redirect_uri
    )

    if "access_token" not in result:
        return JSONResponse(status_code=400, content={"error": result})

    access_token = result["access_token"]

    # ✅ Store token automatically
    response = RedirectResponse(url="/docs")

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True
    )

    return response


from fastapi import Request, HTTPException


def get_current_token(request: Request):

    token = request.cookies.get("access_token")

    if not token:
        raise HTTPException(status_code=401, detail="User not authenticated")

    return token



from fastapi import APIRouter, Depends
from app.services.teams_service import create_teams_meeting
from app.core.dependencies import get_current_token

router = APIRouter()


@router.post("/start-interview")
def start_interview(token: str = Depends(get_current_token)):

    meeting = create_teams_meeting(token)

    return {
        "join_url": meeting["joinWebUrl"],
        "meeting_id": meeting["id"]
    }



import requests
from datetime import datetime, timedelta


def create_teams_meeting(token: str):

    url = "https://graph.microsoft.com/v1.0/me/onlineMeetings"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    start = datetime.utcnow().replace(microsecond=0) + timedelta(minutes=5)
    end = start + timedelta(minutes=30)

    meeting_payload = {
        "subject": "AI Interview Session",
        "startDateTime": start.isoformat() + "Z",
        "endDateTime": end.isoformat() + "Z",
    }

    response = requests.post(url, headers=headers, json=meeting_payload)

    print("Status:", response.status_code)
    print("Graph Response:", response.text)

    if response.status_code != 201:
        raise Exception(response.text)

    return response.json()




from fastapi import FastAPI
from app.api import auth_routes, interview_routes

app = FastAPI(title="AI Interview Platform")

app.include_router(auth_routes.router)
app.include_router(interview_routes.router)













import requests
from app.core.config import settings
from app.services.auth_service import get_graph_token


def schedule_interview(candidate_email: str, start_time: str, end_time: str):

    token = get_graph_token()

    url = f"https://graph.microsoft.com/v1.0/users/{settings.teams_organizer_email}/events"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "subject": "AI Interview Session",
        "body": {
            "contentType": "HTML",
            "content": "Your AI interview is scheduled."
        },
        "start": {
            "dateTime": start_time,
            "timeZone": "UTC"
        },
        "end": {
            "dateTime": end_time,
            "timeZone": "UTC"
        },
        "attendees": [
            {
                "emailAddress": {
                    "address": candidate_email,
                    "name": "Candidate"
                },
                "type": "required"
            },
            {
                "emailAddress": {
                    "address": settings.bot_email,
                    "name": "AI Interview Bot"
                },
                "type": "required"
            }
        ],
        "isOnlineMeeting": True,
        "onlineMeetingProvider": "teamsForBusiness"
    }

    response = requests.post(url, headers=headers, json=payload)

    if response.status_code not in [200, 201]:
        raise Exception(response.text)

    data = response.json()

    return {
        "meeting_id": data["id"],
        "join_url": data["onlineMeeting"]["joinUrl"]
    }








import requests
from datetime import datetime
from app.core.config import settings
from app.services.auth_service import get_graph_token


def schedule_interview(
    candidate_email: str,
    start_time: datetime,
    end_time: datetime
):
    """
    Creates Calendar Event + Teams Meeting + Candidate Invite
    """

    token = get_graph_token()

    organizer = settings.teams_organizer_email

    url = f"https://graph.microsoft.com/v1.0/users/{organizer}/events"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "subject": "AI Interview Session",

        "start": {
            "dateTime": start_time.isoformat(),
            "timeZone": "UTC"
        },

        "end": {
            "dateTime": end_time.isoformat(),
            "timeZone": "UTC"
        },

        # ✅ Automatically creates Teams meeting
        "isOnlineMeeting": True,
        "onlineMeetingProvider": "teamsForBusiness",

        # ✅ Candidate invite
        "attendees": [
            {
                "emailAddress": {
                    "address": candidate_email,
                    "name": candidate_email
                },
                "type": "required"
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)

    print("Status:", response.status_code)
    print("Graph Response:", response.text)

    if response.status_code != 201:
        raise Exception(response.text)

    event = response.json()

    return {
        "meeting_link": event["onlineMeeting"]["joinUrl"],
        "event_id": event["id"]
    }



from fastapi import APIRouter
from datetime import datetime
from app.services.teams_service import schedule_interview

router = APIRouter()


@router.post("/start-interview")
def start_interview():

    meeting = schedule_interview(
        candidate_email="candidate@gmail.com",
        start_time=datetime.utcnow(),
        end_time=datetime.utcnow()
    )

    return meeting






import msal
from app.core.config import settings


AUTHORITY = f"https://login.microsoftonline.com/{settings.tenant_id}"

SCOPES = ["https://graph.microsoft.com/.default"]


msal_app = msal.ConfidentialClientApplication(
    client_id=settings.client_id,
    client_credential=settings.client_secret,
    authority=AUTHORITY
)


def get_graph_token():

    result = msal_app.acquire_token_for_client(scopes=SCOPES)

    if "access_token" not in result:
        raise Exception(result)

    return result["access_token"]




from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    # Azure AD
    client_id: str
    client_secret: str
    tenant_id: str

    # Microsoft Graph
    graph_base_url: str = "https://graph.microsoft.com/v1.0"
    graph_scope: str = "https://graph.microsoft.com/.default"

    # Teams / Calendar
    teams_organizer_email: str
    default_timezone: str = "UTC"

    # App
    ENV: str = "development"
    API_PREFIX: str = "/api"
    APP_NAME: str = "AI Interview Platform"

    class Config:
        env_file = ".env"
        case_sensitive = True


@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()









from fastapi import APIRouter
from datetime import datetime
from backend.app.services.interviewer_scheduler_old import schedule_interview

router = APIRouter()

@router.post("/start-interview")
def start_interview():

    meeting = schedule_interview(
        candidate_email="logiyavidhyapathi@gmail.com",

        # Feb 13 10 AM IST = 04:30 UTC
        start_time=datetime(2026, 2, 13, 4, 30),

        # Feb 13 11 AM IST = 05:30 UTC
        end_time=datetime(2026, 2, 13, 5, 30),
    )

    return meeting




import requests
from datetime import datetime
from app.core.config import settings
from app.services.auth_service import get_graph_token


def schedule_interview(
        candidate_email: str,
        start_time: datetime,
        end_time: datetime
):

    token = get_graph_token()
    organizer = settings.teams_organizer_email

    url = f"https://graph.microsoft.com/v1.0/users/{organizer}/events"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    payload = {
        "subject": "AI Interview Session",

        "start": {
            "dateTime": start_time.isoformat() + "Z",
            "timeZone": "UTC"
        },

        "end": {
            "dateTime": end_time.isoformat() + "Z",
            "timeZone": "UTC"
        },

        "isOnlineMeeting": True,
        "onlineMeetingProvider": "teamsForBusiness",

        "attendees": [
            {
                "emailAddress": {
                    "address": candidate_email,
                    "name": candidate_email
                },
                "type": "required"
            }
        ]
    }

    response = requests.post(url, headers=headers, json=payload)

    print("Status:", response.status_code)
    print("Graph Response:", response.text)

    if response.status_code != 201:
        raise Exception(response.text)

    event = response.json()

    return {
        "meeting_link": event["onlineMeeting"]["joinUrl"],
        "event_id": event["id"]
    }



from TTS.api import TTS
import os

class VoiceGenerator:
    def __init__(self):
        print("Loading XTTS voice model")

        self.tts = TTS(
            model_name="tts_models/multilingual/multi-dataset/xtts_v2",
            gpu=False
        )

        self.speaker_wav = os.path.join(
            os.path.dirname(__file__),
            "voice_samples",
            "interviewer.wav"
        )

    def speak(self, text: str) -> str:
        output_path = os.path.abspath("output.wav")

        self.tts.tts_to_file(
            text=text,
            speaker_wav=self.speaker_wav,
            language="en",
            file_path=output_path
        )

        print(f"Audio generated at: {output_path}")
        return output_path









from apscheduler.schedulers.background import BackgroundScheduler
from app.services.bot_trigger_service import trigger_bot_join

scheduler = BackgroundScheduler()


def start_scheduler():
    scheduler.start()


def schedule_bot_join(join_url, start_time):

    scheduler.add_job(
        trigger_bot_join,
        trigger="date",
        run_date=start_time,
        args=[join_url]
    )



import requests

NODE_BOT_URL = "http://localhost:4000/join-meeting"

def trigger_bot_join(join_url):

    print("Triggering Node Teams Bot")

    response = requests.post(
        NODE_BOT_URL,
        json={"joinUrl": join_url}
    )

    print("Bot response:", response.text)



schedule_bot_join(
    join_url=event["onlineMeeting"]["joinUrl"],
    start_time=start_time
)



from fastapi import FastAPI
from app.api import interview_route
from app.services.scheduler_service import start_scheduler

app = FastAPI()

app.include_router(interview_route.router)

@app.on_event("startup")
def startup_event():
    start_scheduler()




npm install express axios dotenv






const axios = require("axios");
require("dotenv").config();

async function getGraphToken() {

    const url = `https://login.microsoftonline.com/${process.env.TENANT_ID}/oauth2/v2.0/token`;

    const params = new URLSearchParams();

    params.append("client_id", process.env.CLIENT_ID);
    params.append("client_secret", process.env.CLIENT_SECRET);
    params.append("scope", "https://graph.microsoft.com/.default");
    params.append("grant_type", "client_credentials");

    const response = await axios.post(url, params);

    return response.data.access_token;
}

module.exports = { getGraphToken };







const axios = require("axios");
const { getGraphToken } = require("./graphAuth");

async function joinMeeting(joinUrl) {

    console.log("Joining Teams Meeting...");

    const token = await getGraphToken();

    const payload = {
        "@odata.type": "#microsoft.graph.call",
        "callbackUri": "https://yourbotcallback.com/calls",
        "requestedModalities": ["audio"],
        "mediaConfig": {
            "@odata.type": "#microsoft.graph.serviceHostedMediaConfig"
        },
        "meetingInfo": {
            "@odata.type": "#microsoft.graph.organizerMeetingInfo",
            "joinWebUrl": joinUrl
        }
    };

    await axios.post(
        "https://graph.microsoft.com/v1.0/communications/calls",
        payload,
        {
            headers: {
                Authorization: `Bearer ${token}`
            }
        }
    );
}

module.exports = { joinMeeting };








const express = require("express");
const { joinMeeting } = require("./teamsJoinService");

const app = express();

app.use(express.json());

app.post("/join-meeting", async (req, res) => {

    try {

        const { joinUrl } = req.body;

        await joinMeeting(joinUrl);

        res.send("Bot joined meeting");

    } catch (error) {

        console.error(error);
        res.status(500).send("Error joining meeting");
    }
});

app.listen(4000, () => {
    console.log("Teams Bot running on port 4000");
});









start_time = datetime.utcnow() + timedelta(minutes=5)
end_time = start_time + timedelta(minutes=60)













const express = require("express");
const { joinTeamsMeeting } = require("./teamsJoinService");

const app = express();
app.use(express.json());

app.post("/join-meeting", async (req, res) => {

    try {

        console.log("Join meeting request received");

        const { joinUrl } = req.body;

        await joinTeamsMeeting(joinUrl);

        res.send("Bot joining meeting");

    } catch (error) {

        console.error(error);
        res.status(500).send("Bot join failed");

    }
});

app.listen(4000, () => {
    console.log("Teams Bot running on port 4000");
});





const axios = require("axios");
const { getGraphToken } = require("./graphAuth");

async function joinTeamsMeeting(joinUrl) {

    const token = await getGraphToken();

    const payload = {

        "@odata.type": "#microsoft.graph.call",

        "callbackUri": "https://your-bot-ngrok-url/api/callback",

        "requestedModalities": ["audio"],

        "mediaConfig": {
            "@odata.type": "#microsoft.graph.serviceHostedMediaConfig"
        },

        "meetingInfo": {
            "@odata.type": "#microsoft.graph.organizerMeetingInfo",
            "joinWebUrl": joinUrl
        },

        "tenantId": process.env.TENANT_ID
    };

    const response = await axios.post(
        "https://graph.microsoft.com/v1.0/communications/calls",
        payload,
        {
            headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        }
    );

    console.log("Graph Join Response:", response.data);
}

module.exports = { joinTeamsMeeting };







mediaConfig: {
        "@odata.type": "#microsoft.graph.serviceHostedMediaConfig"
    },

    meetingInfo: {
        "@odata.type": "#microsoft.graph.joinMeetingIdMeetingInfo",
        joinWebUrl: joinUrl
    },





import requests
from app.core.config import settings

def trigger_bot_join(meeting_join_url):

    payload = {
        "meetingUrl": meeting_join_url
    }

    response = requests.post(
        f"{settings.bot_service_url}/join-meeting",
        json=payload
    )

    return response.json()




from app.services.teams_join_service import trigger_bot_join

meeting = create_meeting(...)

join_url = meeting["onlineMeeting"]["joinUrl"]

trigger_bot_join(join_url)









import requests
from app.core.config import settings


def trigger_bot_join(join_url: str):

    print("Triggering Node Teams Bot")

    payload = {
        "meetingUrl": join_url
    }

    response = requests.post(
        f"{settings.bot_service_url}/join-meeting",
        json=payload
    )

    print("Bot service response:", response.text)

    return response.json()





from apscheduler.schedulers.background import BackgroundScheduler
from app.services.bot_trigger_service import trigger_bot_join
import pytz

scheduler = BackgroundScheduler(timezone=pytz.UTC)


def start_scheduler():
    print("Scheduler Started")
    scheduler.start()


def schedule_bot_join(join_url, start_time):

    print("Scheduling bot join")
    print("join_url:", join_url)
    print("start_time:", start_time)

    scheduler.add_job(
        trigger_bot_join,
        trigger="date",
        run_date=start_time,
        args=[join_url]
    )





event = response.json()

join_url = event["onlineMeeting"]["joinUrl"]

interviews.insert_one({
    "candidate": candidate_email,
    "join_url": join_url,
    "event_id": event["id"],
    "start_time": start_time,
    "status": "scheduled"
})



from fastapi import FastAPI
from app.services.scheduler_service import start_scheduler

app = FastAPI()


@app.on_event("startup")
def startup():

    start_scheduler()







const axios = require("axios");
require("dotenv").config();

async function getAccessToken() {

    const url = `https://login.microsoftonline.com/${process.env.TENANT_ID}/oauth2/v2.0/token`;

    const params = new URLSearchParams();
    params.append("client_id", process.env.CLIENT_ID);
    params.append("client_secret", process.env.CLIENT_SECRET);
    params.append("scope", "https://graph.microsoft.com/.default");
    params.append("grant_type", "client_credentials");

    const res = await axios.post(url, params);

    return res.data.access_token;
}

module.exports = { getAccessToken };





const axios = require("axios");
const { getAccessToken } = require("./graphAuth");

async function joinMeeting(meetingUrl) {

    const token = await getAccessToken();

    const payload = {
        callbackUri: process.env.BOT_CALLBACK_URL,
        requestedModalities: ["audio"],
        mediaConfig: {
            "@odata.type": "#microsoft.graph.serviceHostedMediaConfig"
        },
        meetingInfo: {
            "@odata.type": "#microsoft.graph.joinMeetingIdMeetingInfo",
            joinWebUrl: meetingUrl
        }
    };

    const res = await axios.post(
        "https://graph.microsoft.com/v1.0/communications/calls",
        payload,
        {
            headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        }
    );

    return res.data;
}

module.exports = { joinMeeting };






module.exports = {

    async handleIncomingCall(req, res) {

        const event = req.body;

        console.log("Teams call event:", event);

        res.status(200).send();
    }

};





const express = require("express");
const bodyParser = require("body-parser");

const botRoutes = require("./routes/botMessages");

const app = express();

app.use(bodyParser.json());

app.use("/bot", botRoutes);

const PORT = process.env.PORT || 3978;

app.listen(PORT, () => {

    console.log(`Teams Bot running on port ${PORT}`);

});





const express = require("express");
require("dotenv").config();

const botRoutes = require("./routes/botMessages");

const app = express();

app.use(express.json());

/*
Register bot routes
*/
app.use("/", botRoutes);

const PORT = 4000;

app.listen(PORT, () => {
    console.log(`Teams Bot running on port ${PORT}`);
});





const express = require("express");
const router = express.Router();

const { joinMeeting } = require("../services/teamsJoinService");
const { handleCall } = require("../handlers/callHandler");

/*
FastAPI backend calls this endpoint
to make the bot join the meeting
*/
router.post("/join-meeting", async (req, res) => {

    try {

        console.log("Join meeting request received");

        const { meetingUrl } = req.body;

        console.log("Meeting URL:", meetingUrl);

        await joinMeeting(meetingUrl);

        res.send("Bot joined meeting");

    } catch (error) {

        console.error(error);

        res.status(500).send("Error joining meeting");
    }

});

/*
Microsoft Graph sends meeting events here
*/
router.post("/calls", handleCall);

module.exports = router;





function handleCall(req, res) {

    console.log(
        "Teams Call Event:",
        JSON.stringify(req.body, null, 2)
    );

    res.sendStatus(200);
}

module.exports = { handleCall };





const axios = require("axios");
const { getGraphToken } = require("./graphAuth");

async function joinMeeting(joinUrl) {

    console.log("Joining Teams meeting...");
    console.log("joinUrl:", joinUrl);

    const token = await getGraphToken();

    const payload = {

        "@odata.type": "#microsoft.graph.call",

        callbackUri: process.env.CALLBACK_URI,

        requestedModalities: ["audio"],

        mediaConfig: {
            "@odata.type": "#microsoft.graph.serviceHostedMediaConfig"
        },

        meetingInfo: {
            "@odata.type": "#microsoft.graph.joinMeetingIdMeetingInfo",
            joinWebUrl: joinUrl
        },

        tenantId: process.env.TENANT_ID
    };

    const response = await axios.post(
        "https://graph.microsoft.com/v1.0/communications/calls",
        payload,
        {
            headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        }
    );

    console.log("Graph Join Response:", response.data);

    return response.data;
}

module.exports = { joinMeeting };






const axios = require("axios");
require("dotenv").config();

async function getGraphToken() {

    const url =
        `https://login.microsoftonline.com/${process.env.TENANT_ID}/oauth2/v2.0/token`;

    const params = new URLSearchParams();

    params.append("client_id", process.env.CLIENT_ID);
    params.append("client_secret", process.env.CLIENT_SECRET);
    params.append("scope", "https://graph.microsoft.com/.default");
    params.append("grant_type", "client_credentials");

    const response = await axios.post(url, params);

    return response.data.access_token;
}

module.exports = { getGraphToken };





const { GoogleGenerativeAI } = require("@google/generative-ai");

const genAI = new GoogleGenerativeAI(process.env.GEMINI_API_KEY);

async function generateQuestion(role) {

    const model = genAI.getGenerativeModel({
        model: "gemini-2.0-flash"
    });

    const prompt = `Ask a technical interview question for ${role}`;

    const result = await model.generateContent(prompt);

    return result.response.text();
}

module.exports = { generateQuestion };





if "application/json" in response.headers.get("content-type", ""):
    return response.json()
else:
    return {"message": response.text}




catch (error) {
    console.error("FULL ERROR:", error.response?.data || error.message);

    res.status(500).json({
        message: "Error joining meeting",
        error: error.response?.data || error.message
    });
}







const payload = {
    "@odata.type": "#microsoft.graph.call",

    callbackUri: process.env.CALLBACK_URI,

    requestedModalities: ["audio"],

    mediaConfig: {
        "@odata.type": "#microsoft.graph.serviceHostedMediaConfig"
    },

    meetingInfo: {
        "@odata.type": "#microsoft.graph.joinMeetingIdMeetingInfo",
        joinWebUrl: joinUrl
    },

    tenantId: process.env.TENANT_ID
};





const payload = {
    "@odata.type": "#microsoft.graph.call",

    callbackUri: process.env.CALLBACK_URI,

    requestedModalities: ["audio"],

    mediaConfig: {
        "@odata.type": "#microsoft.graph.serviceHostedMediaConfig"
    },

    meetingInfo: {
        "@odata.type": "#microsoft.graph.organizerMeetingInfo",

        organizer: {
            "@odata.type": "#microsoft.graph.identitySet",
            user: {
                "@odata.type": "#microsoft.graph.identity",
                id: process.env.ORGANIZER_ID   // VERY IMPORTANT
            }
        },

        joinWebUrl: joinUrl
    },

    tenantId: process.env.TENANT_ID
};



const token = await getGraphToken();

console.log("TOKEN:", token);






async function getGraphToken() {
    try {
        const url = `https://login.microsoftonline.com/${process.env.TENANT_ID}/oauth2/v2.0/token`;

        const params = new URLSearchParams();

        params.append("client_id", process.env.CLIENT_ID);
        params.append("client_secret", process.env.CLIENT_SECRET);
        params.append("scope", "https://graph.microsoft.com/.default");
        params.append("grant_type", "client_credentials");

        const response = await axios.post(url, params, {
            headers: {
                "Content-Type": "application/x-www-form-urlencoded"
            }
        });

        console.log("TOKEN RESPONSE:", response.data);

        return response.data.access_token;

    } catch (error) {
        console.error("TOKEN ERROR:", error.response?.data || error.message);
        throw error;
    }
}





try {
    const response = await axios.post(
        "https://graph.microsoft.com/v1.0/communications/calls",
        payload,
        {
            headers: {
                Authorization: `Bearer ${token}`,
                "Content-Type": "application/json"
            }
        }
    );

    console.log("Graph Join Response:", response.data);
    return response.data;

} catch (error) {

    console.error("========== GRAPH ERROR ==========");
    console.error(JSON.stringify(error.response?.data, null, 2));
    console.error("================================");

    throw error;
}


http://127.0.0.1:4000



meetingInfo: {
    "@odata.type": "#microsoft.graph.organizerMeetingInfo",
    "joinWebUrl": joinUrl
}






meetingInfo: {
    "@odata.type": "#microsoft.graph.joinMeetingIdMeetingInfo",
    "joinWebUrl": joinUrl
}






async function joinMeeting(joinUrl) {

    console.log("Joining Teams Meeting...");
    console.log("joinUrl:", joinUrl)

    const token = await getGraphToken();

    const payload = {
        "@odata.type": "#microsoft.graph.call",

        callbackUri: process.env.CALLBACK_URI,

        requestedModalities: ["audio"],

        mediaConfig: {
            "@odata.type": "#microsoft.graph.serviceHostedMediaConfig"
        },

        meetingInfo: {
            "@odata.type": "#microsoft.graph.organizerMeetingInfo",
            "organizer": {
                "user": {
                    "id": "b82623c6-376c-4f6a-86db-bc4718e1328d" // <-- from your logs (Oid)
                }
            }
        },

        tenantId: process.env.TENANT_ID
    };

    try {
        const response = await axios.post(
            "https://graph.microsoft.com/v1.0/communications/calls",
            payload,
            {
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            }
        );

        console.log("Graph Join Response:", response.data)
        return response.data;

    } catch (error) {
        console.error("-------Graph Error-------");
        console.error(JSON.stringify(error.response?.data, null, 2));
        console.error("---------------");

        throw error;
    }
}




// 👇 ADD IT HERE (above or below joinMeeting — both OK)
function extractThreadId(joinUrl) {
    const decoded = decodeURIComponent(joinUrl);
    const match = decoded.match(/19:meeting_[^@]+@thread\.v2/);
    return match ? match[0] : null;
}



chatInfo: {
            "@odata.type": "#microsoft.graph.chatInfo",
            "threadId": threadId,
            "messageId": "0"
        },



        // 👇 USE FUNCTION HERE
    const threadId = extractThreadId(joinUrl);



meetingInfo: {
        "@odata.type": "#microsoft.graph.organizerMeetingInfo",
        
        "organizer": {
            "user": {
                "id": "b82623c6-376c-4f6a-86db-bc4718e1328d"
            }
        },

        "joinWebUrl": joinUrl   // ✅ REQUIRED
    },



    source: {   // ✅ THIS IS THE MISSING PIECE
        identity: {
            application: {
                id: process.env.CLIENT_ID,
                displayName: "AI Interview Bot"
            }
        }
    },



     "@odata.type": "#microsoft.graph.joinMeetingIdMeetingInfo",
    joinWebUrl: joinUrl








    const axios = require("axios");
const { getGraphToken } = require("./graphAuth");

function extractTenantId(joinUrl) {
    try {
        const decodedUrl = decodeURIComponent(joinUrl);

        const match = decodedUrl.match(/context=({.*})/);

        if (!match) return null;

        const context = JSON.parse(match[1]);

        return context.Tid;
    } catch (err) {
        console.error("Error extracting tenantId:", err);
        return null;
    }
}

async function joinMeeting(joinUrl) {

    console.log("Joining Teams Meeting...");
    console.log("joinUrl:", joinUrl);

    const token = await getGraphToken();

    const decoded = JSON.parse(
        Buffer.from(token.split('.')[1], 'base64').toString()
    );

    console.log("Token Tenant (tid):", decoded.tid);

    const tenantIdFromUrl = extractTenantId(joinUrl);

    console.log("Join URL Tenant:", tenantIdFromUrl);

    if (!tenantIdFromUrl) {
        throw new Error("TenantId not found in join URL");
    }

    const payload = {
        "@odata.type": "#microsoft.graph.call",

        callbackUri: process.env.CALLBACK_URI,

        requestedModalities: ["audio"],

        mediaConfig: {
            "@odata.type": "#microsoft.graph.serviceHostedMediaConfig"
        },

        source: {
            identity: {
                application: {
                    id: process.env.CLIENT_ID,
                    displayName: "AI Interview Bot"
                }
            }
        },

        meetingInfo: {
            "@odata.type": "#microsoft.graph.joinMeetingIdMeetingInfo",
            joinWebUrl: joinUrl,
            tenantId: tenantIdFromUrl   // ✅ FIXED HERE
        },

        tenantId: tenantIdFromUrl       // ✅ FIXED HERE
    };

    try {
        const response = await axios.post(
            "https://graph.microsoft.com/v1.0/communications/calls",
            payload,
            {
                headers: {
                    Authorization: `Bearer ${token}`,
                    "Content-Type": "application/json"
                }
            }
        );

        console.log("Graph Join Response:", response.data);
        return response.data;

    } catch (error) {
        console.error("-------Graph Error-------");
        console.error(JSON.stringify(error.response?.data, null, 2));
        console.error("---------------");

        throw error;
    }
}

module.exports = { joinMeeting };






const payload = {
    "@odata.type": "#microsoft.graph.call",

    callbackUri: process.env.CALLBACK_URI,

    requestedModalities: ["audio"],

    mediaConfig: {
        "@odata.type": "#microsoft.graph.serviceHostedMediaConfig"
    },

    source: {
        identity: {
            application: {
                id: process.env.CLIENT_ID,
                displayName: "AI Interview Bot"
            }
        }
    },

    meetingInfo: {
        "@odata.type": "#microsoft.graph.organizerMeetingInfo",
        organizer: {
            user: {
                id: process.env.ORGANIZER_ID
            }
        }
    },

    chatInfo: {
        "@odata.type": "#microsoft.graph.chatInfo",
        threadId: joinUrl.split("thread.v2/")[1]?.split("/")[0]
    },

    tenantId: tenantFromUrl
};














const payload = {
    "@odata.type": "#microsoft.graph.call",

    callbackUri: process.env.CALLBACK_URI,

    requestedModalities: ["audio"],

    mediaConfig: {
        "@odata.type": "#microsoft.graph.serviceHostedMediaConfig"
    },

    source: {
        identity: {
            application: {
                id: process.env.CLIENT_ID,
                displayName: "AI Interview Bot"
            }
        }
    },

    meetingInfo: {
        "@odata.type": "#microsoft.graph.organizerMeetingInfo",
        organizer: {
            user: {
                id: process.env.ORGANIZER_ID
            }
        }
    },

    chatInfo: {
        "@odata.type": "#microsoft.graph.chatInfo",
        threadId: threadId
    },

    tenantId: process.env.TENANT_ID
};














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
    organizer = settings.teams_organizer_email

    headers = {
        "Authorization": f"Bearer {token}", 
        "Content-Type": "application/json"
    }

    # ──────────────────────────────────────────────────────────────
    # Step 1: Create Online Meeting (organizer does NOT get notified)
    # ──────────────────────────────────────────────────────────────
    meeting_url = f"https://graph.microsoft.com/v1.0/users/{organizer}/onlineMeetings"

    meeting_payload = {
        "subject": "AI Interview Session",
        "startDateTime": start_time.strftime("%Y-%m-%dT%H:%M:%S.0000000Z"),
        "endDateTime": end_time.strftime("%Y-%m-%dT%H:%M:%S.0000000Z"),
        "lobbyBypassSettings": {
            "scope": "everyone",
            "isDialInBypassEnabled": True
        },
    }

    meeting_response = requests.post(meeting_url, headers=headers, json=meeting_payload)

    print("Online Meeting Status:", meeting_response.status_code)
    print("Online Meeting Response:", meeting_response.text)

    if meeting_response.status_code != 201:
        raise Exception(f"Failed to create online meeting: {meeting_response.text}")

    meeting = meeting_response.json()
    join_url = meeting["joinWebUrl"]

    print("Meeting Join URL:", join_url)

    # ──────────────────────────────────────────────────────────────
    # Step 2: Send calendar invite to the candidate
    #   - Creates an event on organizer's calendar with candidate as attendee
    #   - Candidate receives a calendar invite with the Teams join link
    #   - Organizer: reminders off, showAs free, no auto-join
    # ──────────────────────────────────────────────────────────────
    event_url = f"https://graph.microsoft.com/v1.0/users/{organizer}/events"

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

        "body": {
            "contentType": "HTML",
            "content": f"""
                <div style="font-family: Segoe UI, sans-serif; padding: 16px;">
                    <h2>AI Interview Session</h2>
                    <p>You have been scheduled for an AI-powered interview session.</p>
                    <p>Please join at the scheduled time using the link below:</p>
                    <br/>
                    <a href="{join_url}" 
                       style="background-color: #6264A7; color: white; padding: 10px 24px; 
                              text-decoration: none; border-radius: 4px; font-weight: bold;">
                       Join Teams Meeting
                    </a>
                    <br/><br/>
                    <p style="color: #666; font-size: 12px;">
                        If the button doesn't work, copy and paste this link:<br/>
                        <a href="{join_url}">{join_url}</a>
                    </p>
                </div>
            """
        },

        "attendees": [
            {
                "emailAddress": {
                    "address": candidate_email,
                    "name": candidate_email
                },
                "type": "required"
            }
        ],

        # Do NOT set isOnlineMeeting=True — that would link the organizer to the call
        "isOnlineMeeting": False,

        # Minimize organizer involvement
        "isReminderOn": False,
        "showAs": "free",
        "responseRequested": False,
    }

    event_response = requests.post(event_url, headers=headers, json=event_payload)

    print("Calendar Event Status:", event_response.status_code)
    print("Calendar Event Response:", event_response.text)

    if event_response.status_code != 201:
        print(f"Warning: Failed to create calendar invite: {event_response.text}")

    # ──────────────────────────────────────────────────────────────
    # Step 3: Schedule bot to auto-join at the meeting start time
    # ──────────────────────────────────────────────────────────────
    schedule_bot_join(
        join_url=join_url,
        start_time=start_time
    )

    print("Scheduling bot join")
    print("  join_url:", join_url)
    print("  start_time:", start_time)

    return {
        "meeting_link": join_url,
        "meeting_id": meeting["id"],
        "candidate_email": candidate_email,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }














import requests
import urllib.parse
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

    # ──────────────────────────────────────────────────────────────
    # Step 1: Get or Create "AI Interviews" secondary calendar
    #   - We place the real Teams Meeting here so the candidate gets
    #     the popup, but the HR (dev.test) does NOT get the popup!
    # ──────────────────────────────────────────────────────────────
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
        new_cal_response = requests.post(calendars_url, headers=headers, json={"name": "AI Interviews"})
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

    # ──────────────────────────────────────────────────────────────
    # Step 2: Create the Event & Teams Meeting (for the candidate)
    #   - isOnlineMeeting=True generates native Teams meeting
    #   - Candidate gets added as attendee and gets the POPUP!
    # ──────────────────────────────────────────────────────────────
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
        "responseRequested": False,
    }

    event_response = requests.post(event_url, headers=headers, json=event_payload)

    print("Secondary Calendar Event Status:", event_response.status_code)

    if event_response.status_code != 201:
        raise Exception(f"Failed to create event: {event_response.text}")

    event = event_response.json()
    join_url = event["onlineMeeting"]["joinUrl"]

    print("Meeting Join URL:", join_url)

    # ──────────────────────────────────────────────────────────────
    # Step 3: Create Placeholder Event in Primary Calendar for HR
    #   - No attendees (so candidate doesn't get duplicate invite)
    #   - isOnlineMeeting=False (so dev.test gets NO POPUP)
    #   - But it is visually on dev.test's main calendar!
    # ──────────────────────────────────────────────────────────────
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
            "body": {
                "contentType": "HTML", 
                "content": f"""
                    <div style="font-family: Segoe UI, sans-serif; padding: 16px;">
                        <h2>AI Interview Session</h2>
                        <p>This is the placeholder for the AI Interview with <b>{candidate_email}</b>.</p>
                        <br/>
                        <a href="{join_url}" 
                           style="background-color: #6264A7; color: white; padding: 10px 24px; 
                                  text-decoration: none; border-radius: 4px; font-weight: bold;">
                           Join Teams Meeting
                        </a>
                        <br/><br/>
                        <p>Link to join: <a href="{join_url}">{join_url}</a></p>
                    </div>
                """
            },
            "location": {
                "displayName": f"Interview w/ {candidate_email}"
            },
            "attendees": [], 
            "isOnlineMeeting": False, 
            
            # Explicitly turning on reminders so dev.test gets notified
            "isReminderOn": True,
            "reminderMinutesBeforeStart": 15,
            
            "showAs": "busy", 
        }
        
        primary_response = requests.post(primary_event_url, headers=headers, json=primary_payload)
        print("Primary Calendar Status (for HR):", primary_response.status_code)

    # ──────────────────────────────────────────────────────────────
    # Step 4: Schedule bot to auto-join at the meeting start time
    # ──────────────────────────────────────────────────────────────
    schedule_bot_join(
        join_url=join_url, 
        start_time=start_time
    )

    print("Scheduling bot join")
    print("Start Time:", start_time)

    return {
        "meeting_link": join_url, 
        "event_id": event.get("id", ""), 
        "candidate_email": candidate_email, 
        "start_time": start_time.isoformat(), 
        "end_time": end_time.isoformat()
    }














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

    # ──────────────────────────────────────────────────────────────
    # Step 1: Create a calendar event WITH online meeting
    #   - isOnlineMeeting=True auto-creates the Teams meeting & join URL
    #   - Candidate is added as attendee and gets the calendar invite
    #   - Organizer settings minimized: no reminders, showAs free
    #   - The organizer does NOT auto-join — they only appear if
    #     they manually click "Join" from their calendar
    # ──────────────────────────────────────────────────────────────
    event_url = f"https://graph.microsoft.com/v1.0/users/{organizer}/events"

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

        # This creates the Teams meeting and generates a joinUrl
        "isOnlineMeeting": True, 
        "onlineMeetingProvider": "teamsForBusiness",

        "attendees": [
            {
                "emailAddress": {
                    "address": candidate_email, 
                    "name": candidate_email
                }, 
                "type": "required"
            }
        ],

        # Minimize organizer involvement — they won't get reminders
        # and the event shows as "free" on their calendar
        "isReminderOn": False, 
        "showAs": "free", 
        "responseRequested": False,
    }

    response = requests.post(event_url, headers=headers, json=event_payload)

    print("Calendar Event Status:", response.status_code)
    print("Calendar Event Response:", response.text[:500])

    if response.status_code != 201:
        raise Exception(f"Failed to create event: {response.text}")

    event = response.json()
    join_url = event["onlineMeeting"]["joinUrl"]

    print("Meeting Join URL:", join_url)

    # ──────────────────────────────────────────────────────────────
    # Step 2: Schedule bot to auto-join at the meeting start time
    # ──────────────────────────────────────────────────────────────
    schedule_bot_join(
        join_url=join_url, 
        start_time=start_time
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

    # ──────────────────────────────────────────────────────────────
    # Step 1: Create a temporary event with isOnlineMeeting=True
    #   - NO attendees — just to generate the Teams meeting join URL
    #   - We will delete this event immediately after extracting the URL
    # ──────────────────────────────────────────────────────────────
    temp_event_url = f"https://graph.microsoft.com/v1.0/users/{organizer}/events"

    temp_payload = {
        "subject": "AI Interview Session (temp)", 

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

        # No attendees — just creating the meeting link
        "attendees": [],

        "isReminderOn": False, 
        "showAs": "free",
    }

    temp_response = requests.post(temp_event_url, hea ders=headers, json=temp_payload)

    print("Temp Event Status:", temp_response.status_code)

    if temp_response.status_code != 201:
        raise Exception(f"Failed to create temp event: {temp_response.text}")

    temp_event = temp_response.json()
    join_url = temp_event["onlineMeeting"]["joinUrl"]
    temp_event_id = temp_event["id"]

    print("Meeting Join URL:", join_url)

    # ──────────────────────────────────────────────────────────────
    # Step 2: Delete the temporary event from organizer's calendar
    #   - The online meeting link persists even after the event is deleted
    #   - This prevents the organizer from getting any popup/notification
    # ──────────────────────────────────────────────────────────────
    delete_url = f"https://graph.microsoft.com/v1.0/users/{organizer}/events/{temp_event_id}"
    delete_response = requests.delete(delete_url, headers=headers)

    print("Delete Temp Event Status:", delete_response.status_code)

    # ──────────────────────────────────────────────────────────────
    # Step 3: Send calendar invite to the candidate
    #   - isOnlineMeeting=False — no Teams popup for organizer
    #   - The Teams join link is embedded in the email body
    #   - Candidate receives a proper calendar invite with the link
    # ──────────────────────────────────────────────────────────────
    event_url = f"https://graph.microsoft.com/v1.0/users/{organizer}/events"

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

        "body": {
            "contentType": "HTML", 
            "content": f"""
                <div style="font-family: Segoe UI, sans-serif; padding: 16px;">
                    <h2 style="color: #333;">AI Interview Session</h2>
                    <p>You have been scheduled for an AI-powered interview session.</p>
                    <p>Please join at the scheduled time using the link below:</p>
                    <br/>
                    <a href="{join_url}" 
                       style="background-color: #6264A7; color: white; padding: 10px 24px; 
                              text-decoration: none; border-radius: 4px; font-weight: bold;
                              display: inline-block;">
                       Join Teams Meeting
                    </a>
                    <br/><br/>
                    <p style="color: #666; font-size: 12px;">
                        If the button doesn't work, copy and paste this link:<br/>
                        <a href="{join_url}">{join_url}</a>
                    </p>
                </div>
            """
        }, 

        "attendees": [
            {
                "emailAddress": {
                    "address": candidate_email, 
                    "name": candidate_email
                }, 
                "type": "required"
            }
        ],

        # NOT an online meeting — prevents organizer Teams popup
        "isOnlineMeeting": False,

        # Minimize organizer involvement
        "isReminderOn": False, 
        "showAs": "free", 
        "responseRequested": False,
    }

    event_response = requests.post(event_url, headers=headers, json=event_payload)

    print("Calendar Invite Status:", event_response.status_code)

    if event_response.status_code != 201:
        print(f"Warning: Failed to send calendar invite: {event_response.text}")

    event = event_response.json() if event_response.status_code == 201 else {}

    # ──────────────────────────────────────────────────────────────
    # Step 4: Schedule bot to auto-join at the meeting start time
    # ──────────────────────────────────────────────────────────────
    schedule_bot_join(
        join_url=join_url, 
        start_time=start_time
    )

    print("Scheduling bot join")
    print("Join URL:", join_url)
    print("Start Time:", start_time)

    return {
        "meeting_link": join_url, 
        "event_id": event.get("id", ""), 
        "candidate_email": candidate_email, 
        "start_time": start_time.isoformat(), 
        "end_time": end_time.isoformat()
    }


















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

    # ──────────────────────────────────────────────────────────────
    # Step 1: Get or Create "AI Interviews" secondary calendar
    #   - The Teams app ONLY monitors the primary Exchange calendar
    #   - By creating the event in a secondary calendar, the organizer
    #     (dev.test) gets NO popups or reminders in Teams!
    #   - However, the candidate still receives the real calendar invite
    #     and gets the proper native Teams popup!
    # ──────────────────────────────────────────────────────────────
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
        new_cal_response = requests.post(calendars_url, headers=headers, json={"name": "AI Interviews"})
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

    # ──────────────────────────────────────────────────────────────
    # Step 2: Create the Event & Teams Meeting
    #   - isOnlineMeeting=True generates native Teams meeting
    #   - Candidate gets added as attendee and receives the invite
    # ──────────────────────────────────────────────────────────────
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
        "responseRequested": False,
    }

    event_response = requests.post(event_url, headers=headers, json=event_payload)

    print("Calendar Event Status:", event_response.status_code)

    if event_response.status_code != 201:
        raise Exception(f"Failed to create event: {event_response.text}")

    event = event_response.json()
    join_url = event["onlineMeeting"]["joinUrl"]

    print("Meeting Join URL:", join_url)

    # ──────────────────────────────────────────────────────────────
    # Step 3: Schedule bot to auto-join at the meeting start time
    # ──────────────────────────────────────────────────────────────
    schedule_bot_join(
        join_url=join_url, 
        start_time=start_time
    )

    print("Scheduling bot join")
    print("Join URL:", join_url)
    print("Start Time:", start_time)

    return {
        "meeting_link": join_url, 
        "event_id": event.get("id", ""), 
        "candidate_email": candidate_email, 
        "start_time": start_time.isoformat(), 
        "end_time": end_time.isoformat()
    }



















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

    # ──────────────────────────────────────────────────────────────
    # Step 1: Get or Create "AI Interviews" secondary calendar
    #   - We place the real Teams Meeting here so the candidate gets
    #     the popup, but the HR (dev.test) does NOT get the popup!
    # ──────────────────────────────────────────────────────────────
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
        new_cal_response = requests.post(calendars_url, headers=headers, json={"name": "AI Interviews"})
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

    # ──────────────────────────────────────────────────────────────
    # Step 2: Create the Event & Teams Meeting (for the candidate)
    #   - isOnlineMeeting=True generates native Teams meeting
    #   - Candidate gets added as attendee and gets the POPUP!
    # ──────────────────────────────────────────────────────────────
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
        "responseRequested": False,
    }

    event_response = requests.post(event_url, headers=headers, json=event_payload)

    print("Secondary Calendar Event Status:", event_response.status_code)

    if event_response.status_code != 201:
        raise Exception(f"Failed to create event: {event_response.text}")

    event = event_response.json()
    join_url = event["onlineMeeting"]["joinUrl"]

    print("Meeting Join URL:", join_url)

    # ──────────────────────────────────────────────────────────────
    # Step 3: Create Placeholder Event in Primary Calendar for HR
    #   - No attendees (so candidate doesn't get duplicate invite)
    #   - isOnlineMeeting=False (so dev.test gets NO POPUP)
    #   - But it is visually on dev.test's main calendar!
    # ──────────────────────────────────────────────────────────────
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
            "body": {
                "contentType": "HTML", 
                "content": f"""
                    <div style="font-family: Segoe UI, sans-serif; padding: 16px;">
                        <h2>AI Interview Session</h2>
                        <p>This is the placeholder for the AI Interview with <b>{candidate_email}</b>.</p>
                        <br/>
                        <a href="{join_url}" 
                           style="background-color: #6264A7; color: white; padding: 10px 24px; 
                                  text-decoration: none; border-radius: 4px; font-weight: bold;">
                           Join Teams Meeting Manually
                        </a>
                    </div>
                """
            },
            "location": {
                "displayName": f"Microsoft Teams - {candidate_email}"
            },
            "attendees": [], 
            "isOnlineMeeting": False, # CRITICAL: FALSE means no popup for HR!
            "isReminderOn": False, 
            "showAs": "busy", 
        }
        
        primary_response = requests.post(primary_event_url, headers=headers, json=primary_payload)
        print("Primary Calendar Status (for HR):", primary_response.status_code)

    # ──────────────────────────────────────────────────────────────
    # Step 4: Schedule bot to auto-join at the meeting start time
    # ──────────────────────────────────────────────────────────────hea
    schedule_bot_join(
        join_url=join_url, 
        start_time=start_time
    )

    print("Scheduling bot join")
    print("Start Time:", start_time)

    return {
        "meeting_link": join_url, 
        "event_id": event.get("id", ""), 
        "candidate_email": candidate_email, 
        "start_time": start_time.isoformat(), 
        "end_time": end_time.isoformat()
    }





    <a href="https://interview.adamsbridgestage.com/api/join-redirect?url={urllib.parse.quote(join_url)}" 




    @router.get("/join-redirect")
def join_redirect(url: str):
    return RedirectResponse(url=url)



    from fastapi.responses import RedirectResponse









































import requests
import urllib.parse
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

    # ──────────────────────────────────────────────────────────────
    # Step 1: Get or Create "AI Interviews" secondary calendar
    #   - We place the real Teams Meeting here so the candidate gets
    #     the popup, but the HR (dev.test) does NOT get the popup!
    # ──────────────────────────────────────────────────────────────
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
        new_cal_response = requests.post(calendars_url, headers=headers, json={"name": "AI Interviews"})
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

    # ──────────────────────────────────────────────────────────────
    # Step 2: Create the Event & Teams Meeting (for the candidate)
    #   - isOnlineMeeting=True generates native Teams meeting
    #   - Candidate gets added as attendee and gets the POPUP!
    # ──────────────────────────────────────────────────────────────
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
        "responseRequested": False,
    }

    event_response = requests.post(event_url, headers=headers, json=event_payload)

    print("Secondary Calendar Event Status:", event_response.status_code)

    if event_response.status_code != 201:
        raise Exception(f"Failed to create event: {event_response.text}")

    event = event_response.json()
    join_url = event["onlineMeeting"]["joinUrl"]

    print("Meeting Join URL:", join_url)

    # ──────────────────────────────────────────────────────────────
    # Step 3: Create Placeholder Event in Primary Calendar for HR
    #   - No attendees (so candidate doesn't get duplicate invite)
    #   - isOnlineMeeting=False (so dev.test gets NO POPUP)
    #   - But it is visually on dev.test's main calendar!
    # ──────────────────────────────────────────────────────────────
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
            "body": {
                "contentType": "HTML", 
                "content": f"""
                    <div style="font-family: Segoe UI, sans-serif; padding: 16px;">
                        <h2>AI Interview Session</h2>
                        <p>This is the placeholder for the AI Interview with <b>{candidate_email}</b>.</p>
                        <br/>
                        <a href="{join_url}" 
                           style="background-color: #6264A7; color: white; padding: 10px 24px; 
                                  text-decoration: none; border-radius: 4px; font-weight: bold;">
                           Join Teams Meeting
                        </a>
                        <br/><br/>
                        <p>Link to join: <a href="{join_url}">{join_url}</a></p>
                    </div>
                """
            },
            "location": {
                "displayName": f"Interview w/ {candidate_email}"
            },
            "attendees": [], 
            "isOnlineMeeting": False, 
            
            # Explicitly turning on reminders so dev.test gets notified
            "isReminderOn": True,
            "reminderMinutesBeforeStart": 15,
            
            "showAs": "busy", 
        }
        
        primary_response = requests.post(primary_event_url, headers=headers, json=primary_payload)
        print("Primary Calendar Status (for HR):", primary_response.status_code)

    # ──────────────────────────────────────────────────────────────
    # Step 4: Schedule bot to auto-join at the meeting start time
    # ──────────────────────────────────────────────────────────────
    schedule_bot_join(
        join_url=join_url, 
        start_time=start_time
    )

    print("Scheduling bot join")
    print("Start Time:", start_time)

    return {
        "meeting_link": join_url, 
        "event_id": event.get("id", ""), 
        "candidate_email": candidate_email, 
        "start_time": start_time.isoformat(), 
        "end_time": end_time.isoformat()
    }




from motor.motor_asyncio import AsyncIOMotorClient
from app.core.config import settings

# Initialize Motor Client
client = AsyncIOMotorClient(settings.MONGO_URI)

# Define reference to our specific Database
db = client.ai_interview_db

# Export specific collections for ease of access
candidates_collection = db.candidates










from pydantic import BaseModel, EmailStr
from typing import List, Optional
from enum import Enum

class QuestionType(str, Enum):
    introductory = "Introductory"
    basic = "Basic"
    technical = "Technical"

class QuestionModel(BaseModel):
    text: str
    type: QuestionType
    expected_answer: Optional[str] = None

class CandidatePrepareRequest(BaseModel):
    candidate_email: EmailStr
    resume_text: str
    job_description_text: str

class CandidateModel(BaseModel):
    candidate_email: EmailStr
    resume_text: str
    job_description_text: str
    questions: List[QuestionModel]

















import google.generativeai as genai
from app.core.config import settings
import json

genai.configure(api_key=settings.GEMINI_API_KEY)

# We use the user's requested model
MODEL_NAME = "gemini-2.0-flash"

SYSTEM_PROMPT = """
You are an expert technical interviewer and recruiter. 
Given a Candidate's Resume and a Job Description, you must generate exactly 9 interview questions:
- 3 Introductory questions (assessing cultural fit, background, and soft skills).
- 3 Basic technical questions (assessing fundamental knowledge required for the role).
- 3 Technical questions (challenging questions assessing deep expertise based on the resume and JD).

You must output ONLY valid JSON in the exact format defined below without any markdown formatting or extra text:
[
  {
    "text": "The question...?",
    "type": "Introductory",
    "expected_answer": "Brief summary of what a good answer sounds like."
  },
  ...
]
"""

async def generate_interview_questions(resume_text: str, jd_text: str) -> list:
    """
    Calls Gemini to generate 9 structure questions based on JD and Resume.
    """
    prompt = f"Resume:\n{resume_text}\n\nJob Description:\n{jd_text}"
    
    model = genai.GenerativeModel(
        model_name=MODEL_NAME,
        system_instruction=SYSTEM_PROMPT,
        generation_config={"response_mime_type": "application/json"}
    )
    
    response = model.generate_content(prompt)
    
    try:
        # Load the generated string as JSON
        questions = json.loads(response.text)
        return questions
    except json.JSONDecodeError as e:
        print("Failed to parse Gemini output as JSON:", response.text)
        raise e














from fastapi import APIRouter, HTTPException, status
from app.schemas.candidate_schema import CandidatePrepareRequest, CandidateModel
from app.services.gemini_service import generate_interview_questions
# from app.db.database import candidates_collection

router = APIRouter(prefix="/candidates", tags=["Candidates"])

@router.post("/prepare", response_model=CandidateModel)
async def prepare_candidate(request: CandidatePrepareRequest):
    """
    Ingests a candidate's resume and JD, generates questions via Gemini,
    and stores the aggregated profile in MongoDB.
    """
    try:
        # 1. Generate Questions
        questions_data = await generate_interview_questions(
            resume_text=request.resume_text,
            jd_text=request.job_description_text
        )
        
        # 2. Build the candidate record
        candidate_data = {
            "candidate_email": request.candidate_email,
            "resume_text": request.resume_text,
            "job_description_text": request.job_description_text,
            "questions": questions_data
        }
        
        # Validate data using our Pydantic model
        candidate = CandidateModel(**candidate_data)
        
        # 3. Store in MongoDB (Disabled temporarily)
        # Motor requires dict so we can use model_dump()
        # c_dict = candidate.model_dump()
        # result = await candidates_collection.insert_one(c_dict)
        # 
        # if not result.inserted_id:
        #     raise HTTPException(
        #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #         detail="Failed to save candidate to Database"
        #     )
            
        return candidate
    except Exception as e:
        print(f"Error preparing candidate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )











from fastapi import FastAPI
from app.api import interview_routes, candidate_routes
from app.services.scheduler_service import start_schedule

app = FastAPI()

app.include_router(interview_routes.router)
app.include_router(candidate_routes.router)

@app.on_event("startup")
def startup_event():
    start_schedule()







from google import genai
from google.genai import types
from app.core.config import settings
import json

client = genai.Client(api_key=settings.GEMINI_API_KEY)

# We use the user's requested model
MODEL_NAME = "gemini-2.0-flash"

SYSTEM_PROMPT = """
You are an expert technical interviewer and recruiter. 
Given a Candidate's Resume and a Job Description, you must generate exactly 9 interview questions:
- 3 Introductory questions (assessing cultural fit, background, and soft skills).
- 3 Basic technical questions (assessing fundamental knowledge required for the role).
- 3 Technical questions (challenging questions assessing deep expertise based on the resume and JD).

You must output ONLY valid JSON in the exact format defined below without any markdown formatting or extra text:
[
  {
    "text": "The question...?",
    "type": "Introductory",
    "expected_answer": "Brief summary of what a good answer sounds like."
  }
]
"""

async def generate_interview_questions(resume_text: str, jd_text: str) -> list:
    """
    Calls Gemini to generate 9 structure questions based on JD and Resume.
    """
    prompt = f"Resume:\n{resume_text}\n\nJob Description:\n{jd_text}"
    
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json"
        )
    )
    
    try:
        # Load the generated string as JSON
        questions = json.loads(response.text)
        return questions
    except json.JSONDecodeError as e:
        print("Failed to parse Gemini output as JSON:", response.text)
        raise e





import requests
import urllib.parse
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

    # ──────────────────────────────────────────────────────────────
    # Step 1: Get or Create "AI Interviews" secondary calendar
    #   - We place the real Teams Meeting here so the candidate gets
    #     the popup, but the HR (dev.test) does NOT get the popup!
    # ──────────────────────────────────────────────────────────────
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
        new_cal_response = requests.post(calendars_url, headers=headers, json={"name": "AI Interviews"})
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

    # ──────────────────────────────────────────────────────────────
    # Step 2: Create the Event & Teams Meeting (for the candidate)
    #   - isOnlineMeeting=True generates native Teams meeting
    #   - Candidate gets added as attendee and gets the POPUP!
    # ──────────────────────────────────────────────────────────────
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
        "responseRequested": False,
    }

    event_response = requests.post(event_url, headers=headers, json=event_payload)

    print("Secondary Calendar Event Status:", event_response.status_code)

    if event_response.status_code != 201:
        raise Exception(f"Failed to create event: {event_response.text}")

    event = event_response.json()
    join_url = event["onlineMeeting"]["joinUrl"]

    print("Meeting Join URL:", join_url)

    # ──────────────────────────────────────────────────────────────
    # Step 3: Create Placeholder Event in Primary Calendar for HR
    #   - No attendees (so candidate doesn't get duplicate invite)
    #   - isOnlineMeeting=False (so dev.test gets NO POPUP)
    #   - But it is visually on dev.test's main calendar!
    # ──────────────────────────────────────────────────────────────
    if calendar_id:
        primary_event_url = f"https://graph.microsoft.com/v1.0/users/{organizer}/events"
        
        redirect_url = f"https://interview.adamsbridgestage.com/api/join-redirect?url={urllib.parse.quote(join_url)}"
        
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
            "body": {
                "contentType": "HTML", 
                "content": f"""
                    <div style="font-family: Segoe UI, sans-serif; padding: 16px;">
                        <h2>AI Interview Session</h2>
                        <p>This is the placeholder for the AI Interview with <b>{candidate_email}</b>.</p>
                        <br/>
                        <a href="{redirect_url}" 
                           style="background-color: #6264A7; color: white; padding: 10px 24px; 
                                  text-decoration: none; border-radius: 4px; font-weight: bold;">
                           Join Teams Meeting Manually
                        </a>
                        <br/><br/>
                        <p>If the button is not clickable in this preview, click the link below:<br/>
                        <a href="{redirect_url}">{redirect_url}</a></p>
                    </div>
                """
            },
            "location": {
                "displayName": f"Microsoft Teams - {candidate_email}"
            },
            "attendees": [], 
            "isOnlineMeeting": False, # CRITICAL: FALSE means no popup for HR!
            "isReminderOn": False, 
            "showAs": "busy", 
        }
        
        primary_response = requests.post(primary_event_url, headers=headers, json=primary_payload)
        print("Primary Calendar Status (for HR):", primary_response.status_code)

    # ──────────────────────────────────────────────────────────────
    # Step 4: Schedule bot to auto-join at the meeting start time
    # ──────────────────────────────────────────────────────────────
    schedule_bot_join(
        join_url=join_url, 
        start_time=start_time
    )

    print("Scheduling bot join")
    print("Start Time:", start_time)

    return {
        "meeting_link": join_url, 
        "event_id": event.get("id", ""), 
        "candidate_email": candidate_email, 
        "start_time": start_time.isoformat(), 
        "end_time": end_time.isoformat()
    }






    from google.genai import Client, types
from app.core.config import settings
import json

client = Client(api_key=settings.GEMINI_API_KEY)






            response_mime_type="application/json",
            response_schema=list[QuestionModel],




            from app.schemas.candidate_schema import QuestionModel




SYSTEM_PROMPT = """
You are an expert technical interviewer and hiring manager. Your goal is to prepare a comprehensive and well-rounded set of interview questions to ask a candidate during a live interview.

You must read the provided Candidate's Resume and Job Description carefully. Based on the analysis, generate questions directed AT THE CANDIDATE in the second person (e.g., "Can you tell me about your experience...", "How would you design..."). Do NOT ask questions about the candidate in the third person.

Please categorize the questions logically to assess the candidate fully:
- Introductory: Assess cultural fit, background, and general communication skills.
- Basic: Assess fundamental domain knowledge required for the role.
- Technical/Advanced: Challenge the candidate by assessing deep expertise, system design, or specific challenging scenarios based on their resume and the JD.

For each question's "expected_answer", provide a 1-2 sentence rubric of what a strong, competent response should sound like.
"""












SYSTEM_PROMPT = """
You are an expert technical interviewer and hiring manager acting on behalf of the organization. 
Your objective is to design a comprehensive, well-rounded set of interview questions to evaluate a candidate during a live interview session.

Please analyze the provided Candidate Request data, which contains the candidate's professional resume alongside the official Job Description for the open position.

Guidelines for formulating questions:
1. Interrogative Formulation: Ensure every output item is structured as a direct, second-person interrogative question directed at the candidate. Avoid declarative statements or third-person summaries.
2. Comprehensive Assessment: Categorize the generated questions to assess three primary domains:
   - Introductory: Evaluate cultural alignment, professional background, and core communication skills.
   - Basic: Evaluate foundational domain knowledge essential for the role.
   - Technical: Provide inquiries that assess deep technical expertise, architectural design capabilities, or problem-solving skills based on the candidate's stated experience.
3. Evaluation Rubric: For the 'expected_answer', provide a concise rubric outlining the key points a highly qualified candidate should cover.
"""






























from fastapi import APIRouter, HTTPException, status, UploadFile, File, Form
from pydantic import EmailStr
from app.schemas.candidate_schema import CandidateModel
from app.services.gemini_service import generate_interview_questions
from app.utils.file_parser import extract_text_from_file
# from app.db.database import candidates_collection

router = APIRouter(prefix="/candidates", tags=["Candidates"])

@router.post("/prepare", response_model=CandidateModel)
async def prepare_candidate(
    candidate_email: EmailStr = Form(...),
    resume_file: UploadFile = File(...),
    jd_file: UploadFile = File(...)
):
    """
    Ingests a candidate's resume and JD files, parses them, 
    generates questions via Gemini, and stores the aggregated profile.
    """
    try:
        # 0. Extract text from uploaded documents
        resume_text = await extract_text_from_file(resume_file)
        job_description_text = await extract_text_from_file(jd_file)

        # 1. Generate Questions
        questions_data = await generate_interview_questions(
            resume_text=resume_text,
            jd_text=job_description_text
        )
        
        # 2. Build the candidate record
        candidate_data = {
            "candidate_email": candidate_email,
            "resume_text": resume_text,
            "job_description_text": job_description_text,
            "questions": questions_data
        }
        
        # Validate data using our Pydantic model
        candidate = CandidateModel(**candidate_data)
        
        # 3. Store in MongoDB (Disabled temporarily)
        # Motor requires dict so we can use model_dump()
        # c_dict = candidate.model_dump()
        # result = await candidates_collection.insert_one(c_dict)
        # 
        # if not result.inserted_id:
        #     raise HTTPException(
        #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #         detail="Failed to save candidate to Database"
        #     )
            
        return candidate
    except Exception as e:
        print(f"Error preparing candidate: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
















import io
import fitz  # PyMuPDF
import docx
from fastapi import UploadFile, HTTPException, status

async def extract_text_from_file(file: UploadFile) -> str:
    """
    Extracts raw text from an uploaded file.
    Supports: .txt, .pdf, .docx
    """
    filename = file.filename.lower()
    content = await file.read()
    
    text = ""

    try:
        if filename.endswith(".txt"):
            text = content.decode("utf-8")
            
        elif filename.endswith(".pdf"):
            # Open PDF using PyMuPDF from memory stream
            pdf_document = fitz.open(stream=content, filetype="pdf")
            for page in pdf_document:
                text += page.get_text("text") + "\n"
            pdf_document.close()
            
        elif filename.endswith(".docx"):
            # Parse DOCX using python-docx from memory stream
            doc = docx.Document(io.BytesIO(content))
            text = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
        else:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"Unsupported file extension for {filename}. Only .pdf, .docx, and .txt are allowed."
            )
            
        if not text.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"No text could be extracted from {filename}."
            )
            
        return text

    except Exception as e:
        # Rethrow HTTPExceptions directly
        if isinstance(e, HTTPException):
            raise e
            
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to parse file {filename}: {str(e)}"
        )













from pydantic import BaseModel
from typing import List, Optional
from enum import Enum

class QuestionType(str, Enum):
    introductory = "Introductory"
    basic = "Basic"
    technical = "Technical"

class QuestionModel(BaseModel):
    text: str
    type: QuestionType

class CandidatePrepareRequest(BaseModel):
    resume_text: str
    job_description_text: str

class CandidateModel(BaseModel):
    resume_text: str
    job_description_text: str
    questions: List[QuestionModel]













from google.genai import Client, types
from app.core.config import settings
from app.schemas.candidate_schema import QuestionModel
import json

client = Client(api_key=settings.GEMINI_API_KEY)

# We use the user's requested model
MODEL_NAME = "gemini-2.0-flash"

SYSTEM_PROMPT = """
You are an expert technical interviewer conducting a live interview directly with the candidate.

You must read the Candidate's Resume and Job Description and generate EXACTLY 10 interview questions addressed DIRECTLY TO THE CANDIDATE. 

CRITICAL RULE: You MUST speak exactly as if you are talking to the candidate face-to-face. Use "you" and "your". Do NOT ever use the candidate's name or refer to them in the third person.

Structure your 10 questions logically in this exact chronological interview sequence:
- Question 1 (Introductory): Must be asking the candidate to introduce themselves and walk through their professional background.
- Questions 2 and 3 (Introductory): Ask about their professional strengths, career goals, or general soft skills based on their resume.
- Questions 4 to 10 (Technical/Basic): Shift entirely to technical questions evaluating their specific skills, domain knowledge, architectural design capabilities, and problem-solving abilities directly related to the Job Description and their past experience.
"""

async def generate_interview_questions(resume_text: str, jd_text: str) -> list:
    """
    Calls Gemini to generate 9 structure questions based on JD and Resume.
    """
    prompt = f"Resume:\n{resume_text}\n\nJob Description:\n{jd_text}"
    
    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=list[QuestionModel],
        )
    )
    
    try:
        # Load the generated string as JSON
        questions = json.loads(response.text)
        return questions
    except json.JSONDecodeError as e:
        print("Failed to parse Gemini output as JSON:", response.text)
        raise e


















from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum

class QuestionType(str, Enum):
    introductory = "Introductory"
    basic = "Basic"
    technical = "Technical"

class QuestionModel(BaseModel):
    text: str = Field(description="The exact interview question to ask the candidate directly. Must be an interrogative sentence ending in a question mark. Do NOT output a summary statement.")
    type: QuestionType

class CandidatePrepareRequest(BaseModel):
    resume_text: str
    job_description_text: str

class CandidateModel(BaseModel):
    resume_text: str
    job_description_text: str
    questions: List[QuestionModel] = Field(
        min_length=10, 
        max_length=10, 
        description="A list of exactly 10 generated interview questions."
    )







from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from enum import Enum

class QuestionType(str, Enum):
    introductory = "Introductory"
    basic = "Basic"
    technical = "Technical"

class QuestionModel(BaseModel):
    text: str = Field(description="The exact interview question to ask the candidate directly. Must be an interrogative sentence ending in a question mark. Do NOT output a summary statement.")
    type: QuestionType

class GeminiOutputModel(BaseModel):
    candidate_name: str = Field(description="The full name of the candidate extracted from the resume.")
    candidate_email: EmailStr = Field(description="The primary email address of the candidate extracted from the resume.")
    questions: List[QuestionModel] = Field(
        min_length=10,
        max_length=10,
        description="A list of exactly 10 generated interview questions."
    )

class CandidatePrepareRequest(BaseModel):
    resume_text: str
    job_description_text: str

class InterviewResponseModel(BaseModel):
    candidate_name: str
    candidate_email: str
    resume_text: str
    job_description_text: str
    questions: List[QuestionModel]
    meeting_link: str
    event_id: str
    start_time: str
    end_time: str













from google.genai import Client, types
from app.core.config import settings
from app.schemas.candidate_schema import GeminiOutputModel
import json

client = Client(api_key=settings.GEMINI_API_KEY)

# We use the user's requested model
MODEL_NAME = "gemini-2.0-flash"

SYSTEM_PROMPT = """
You are an expert technical interviewer conducting a live interview directly with the candidate.

Your task has two parts:
1. Extract the candidate's full name and primary email address from the provided Resume.
2. Generate EXACTLY 10 interview questions addressed DIRECTLY TO THE CANDIDATE.

CRITICAL RULE: You MUST speak exactly as if you are talking to the candidate face-to-face. Use "you" and "your". Do NOT ever use the candidate's name or refer to them in the third person.

Structure your 10 questions logically in this exact chronological interview sequence:
- Question 1 (Introductory): Must be asking the candidate to introduce themselves and walk through their professional background.
- Questions 2 and 3 (Introductory): Ask about their professional strengths, career goals, or general soft skills based on their resume.
- Questions 4 to 10 (Technical/Basic): Shift entirely to technical questions evaluating their specific skills, domain knowledge, architectural design capabilities, and problem-solving abilities directly related to the Job Description and their past experience.
"""

async def generate_interview_questions(resume_text: str, jd_text: str) -> GeminiOutputModel:
    """
    Calls Gemini to extract candidate info and generate 10 interview questions.
    Returns a GeminiOutputModel with candidate_name, candidate_email, and questions.
    """
    prompt = f"Resume:\n{resume_text}\n\nJob Description:\n{jd_text}"

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=GeminiOutputModel,
        )
    )

    try:
        data = json.loads(response.text)
        return GeminiOutputModel(**data)
    except (json.JSONDecodeError, Exception) as e:
        print("Failed to parse Gemini output:", response.text)
        raise e






























from fastapi import APIRouter, UploadFile, File
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta
from app.services.interviewer_scheduler import schedule_interview
from app.services.gemini_service import generate_interview_questions
from app.utils.file_parser import extract_text_from_file

router = APIRouter()

import base64

@router.get("/join-redirect")
def join_redirect(url: str):
    try:
        decoded_url = base64.b64decode(url).decode('utf-8')
    except Exception:
        decoded_url = url
    return RedirectResponse(url=decoded_url)


@router.post("/start-interview")
async def start_interview(
    resume_file: UploadFile = File(...),
    jd_file: UploadFile = File(...)
):
    """
    Dynamically extracts the candidate's email from the uploaded resume via Gemini,
    then schedules a Microsoft Teams interview for that email automatically.
    """
    # Step 1: Extract raw text from uploaded files
    resume_text = await extract_text_from_file(resume_file)
    jd_text = await extract_text_from_file(jd_file)

    # Step 2: Gemini extracts candidate name, email, and generates questions
    gemini_output = await generate_interview_questions(
        resume_text=resume_text,
        jd_text=jd_text
    )

    # Step 3: Use the dynamically extracted email to schedule the Teams meeting
    start_time = datetime.utcnow() + timedelta(minutes=2)
    end_time = start_time + timedelta(minutes=60)

    meeting = schedule_interview(
        candidate_email=str(gemini_output.candidate_email),
        start_time=start_time,
        end_time=end_time
    )

    return {
        "candidate_name": gemini_output.candidate_name,
        "candidate_email": str(gemini_output.candidate_email),
        "meeting_link": meeting["meeting_link"],
        "event_id": meeting["event_id"],
        "start_time": meeting["start_time"],
        "end_time": meeting["end_time"]
    }








from fastapi import APIRouter, HTTPException, status, UploadFile, File
from datetime import datetime, timedelta
from app.schemas.candidate_schema import InterviewResponseModel
from app.services.gemini_service import generate_interview_questions
from app.services.interviewer_scheduler import schedule_interview
from app.utils.file_parser import extract_text_from_file
# from app.db.database import candidates_collection

router = APIRouter(prefix="/candidates", tags=["Candidates"])

@router.post("/prepare", response_model=InterviewResponseModel)
async def prepare_candidate(
    resume_file: UploadFile = File(...),
    jd_file: UploadFile = File(...)
):
    """
    Full pipeline:
    1. Parses uploaded Resume (PDF/DOCX) and Job Description files.
    2. Sends both to Gemini to extract candidate name, email, and generate 10 interview questions.
    3. Schedules a Microsoft Teams interview for the extracted candidate email.
    4. Returns the full response including the Teams meeting link.
    """
    try:
        # Step 1: Extract raw text from uploaded files
        resume_text = await extract_text_from_file(resume_file)
        job_description_text = await extract_text_from_file(jd_file)

        # Step 2: Call Gemini — extract name, email, and generate 10 questions in one call
        gemini_output = await generate_interview_questions(
            resume_text=resume_text,
            jd_text=job_description_text
        )

        # Step 3: Schedule Teams meeting (2 minutes from now for testing)
        start_time = datetime.utcnow() + timedelta(minutes=2)
        end_time = start_time + timedelta(minutes=60)

        meeting = schedule_interview(
            candidate_email=str(gemini_output.candidate_email),
            start_time=start_time,
            end_time=end_time
        )

        # Step 4: Build and return the full response
        return InterviewResponseModel(
            candidate_name=gemini_output.candidate_name,
            candidate_email=str(gemini_output.candidate_email),
            resume_text=resume_text,
            job_description_text=job_description_text,
            questions=gemini_output.questions,
            meeting_link=meeting["meeting_link"],
            event_id=meeting["event_id"],
            start_time=meeting["start_time"],
            end_time=meeting["end_time"]
        )

    except Exception as e:
        print(f"Error in prepare_candidate pipeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


  






  from fastapi import FastAPI
from app.api import interview_routes
from app.services.scheduler_service import start_schedule

app = FastAPI()

app.include_router(interview_routes.router)

@app.on_event("startup")
def startup_event():
    print("Starting AI Interview Platform")
    start_schedule()
    print("Scheduler Started")






from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta
from app.services.interviewer_scheduler import schedule_interview
from app.services.gemini_service import generate_interview_questions
from app.utils.file_parser import extract_text_from_file
from app.schemas.candidate_schema import InterviewResponseModel
import base64

router = APIRouter()

@router.get("/join-redirect")
def join_redirect(url: str):
    try:
        decoded_url = base64.b64decode(url).decode('utf-8')
    except Exception:
        decoded_url = url
    return RedirectResponse(url=decoded_url)


@router.post("/start-interview", response_model=InterviewResponseModel)
async def start_interview(
    resume_file: UploadFile = File(...),
    jd_file: UploadFile = File(...)
):
    """
    Full AI Interview Pipeline:
    1. Parses uploaded Resume and Job Description files.
    2. Gemini extracts candidate name, email and generates 10 interview questions.
    3. Schedules a Microsoft Teams meeting for the extracted candidate email.
    4. Returns the complete response including meeting link and questions.
    """
    try:
        # Step 1: Extract raw text from uploaded files
        resume_text = await extract_text_from_file(resume_file)
        jd_text = await extract_text_from_file(jd_file)

        # Step 2: Gemini extracts candidate info and generates 10 questions
        gemini_output = await generate_interview_questions(
            resume_text=resume_text,
            jd_text=jd_text
        )

        # Step 3: Schedule Teams meeting using the extracted candidate email
        start_time = datetime.utcnow() + timedelta(minutes=2)
        end_time = start_time + timedelta(minutes=60)

        meeting = schedule_interview(
            candidate_email=str(gemini_output.candidate_email),
            start_time=start_time,
            end_time=end_time
        )

        # Step 4: Return full response
        return InterviewResponseModel(
            candidate_name=gemini_output.candidate_name,
            candidate_email=str(gemini_output.candidate_email),
            resume_text=resume_text,
            job_description_text=jd_text,
            questions=gemini_output.questions,
            meeting_link=meeting["meeting_link"],
            event_id=meeting["event_id"],
            start_time=meeting["start_time"],
            end_time=meeting["end_time"]
        )

    except Exception as e:
        print(f"Error in start_interview pipeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )









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
    """
    Creates a Microsoft Teams Online Meeting using the /onlineMeetings API.
    This approach does NOT require Exchange Online — only a Teams license.
    Then sends the candidate an email invite with the join link via Graph Mail API.
    """
    token = get_graph_token()
    organizer = settings.TEAMS_ORGANIZER_EMAIL

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # ──────────────────────────────────────────────────────────────
    # Step 1: Create Teams Online Meeting via /onlineMeetings
    #   - Does NOT touch Exchange/Calendar at all
    #   - Only requires OnlineMeetings.ReadWrite.All app permission
    # ──────────────────────────────────────────────────────────────
    meeting_payload = {
        "subject": "AI Interview Session",
        "startDateTime": start_time.strftime("%Y-%m-%dT%H:%M:%S.0000000Z"),
        "endDateTime": end_time.strftime("%Y-%m-%dT%H:%M:%S.0000000Z"),
        "lobbyBypassSettings": {
            "scope": "everyone",
            "isDialInBypassEnabled": True
        },
        "allowedPresenters": "everyone",
        "isEntryExitAnnounced": False,
    }

    meeting_url = f"https://graph.microsoft.com/v1.0/users/{organizer}/onlineMeetings"
    meeting_response = requests.post(meeting_url, headers=headers, json=meeting_payload)

    print("Online Meeting API Status:", meeting_response.status_code)

    if meeting_response.status_code not in (200, 201):
        raise Exception(f"Failed to create Teams meeting: {meeting_response.text}")

    meeting_data = meeting_response.json()
    join_url = meeting_data.get("joinWebUrl") or meeting_data.get("joinUrl")
    meeting_id = meeting_data.get("id", "")

    print("Meeting Join URL:", join_url)

    # ──────────────────────────────────────────────────────────────
    # Step 2: Send Email Invite to Candidate via Graph Mail API
    #   - Sends the join link directly to the candidate's inbox
    #   - Falls back gracefully if mail send fails (non-fatal)
    # ──────────────────────────────────────────────────────────────
    _send_email_invite(
        token=token,
        organizer=organizer,
        candidate_email=candidate_email,
        join_url=join_url,
        start_time=start_time,
        end_time=end_time
    )

    # ──────────────────────────────────────────────────────────────
    # Step 3: Schedule bot to auto-join at the meeting start time
    # ──────────────────────────────────────────────────────────────
    schedule_bot_join(
        join_url=join_url,
        start_time=start_time
    )

    print("Bot join scheduled for:", start_time)

    return {
        "meeting_link": join_url,
        "event_id": meeting_id,
        "candidate_email": candidate_email,
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat()
    }


def _send_email_invite(
        token: str,
        organizer: str,
        candidate_email: str,
        join_url: str,
        start_time: datetime,
        end_time: datetime
):
    """
    Sends a plain HTML email to the candidate with the Teams meeting join link.
    Uses Graph API sendMail — requires Mail.Send app permission.
    Failure is non-fatal (logged as a warning).
    """
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    start_str = start_time.strftime("%B %d, %Y at %I:%M %p UTC")
    end_str = end_time.strftime("%I:%M %p UTC")

    email_body = f"""
    <html>
    <body style="font-family: Arial, sans-serif; color: #333;">
        <p>Dear Candidate,</p>
        <p>You have been invited to an <strong>AI Interview Session</strong>.</p>
        <table>
            <tr><td><strong>Date &amp; Time:</strong></td><td>{start_str} – {end_str}</td></tr>
        </table>
        <br/>
        <p>
            <a href="{join_url}"
               style="background:#6264A7;color:white;padding:12px 24px;
                      text-decoration:none;border-radius:4px;font-size:14px;">
                Join Microsoft Teams Meeting
            </a>
        </p>
        <br/>
        <p>Or copy this link into your browser:<br/>
           <a href="{join_url}">{join_url}</a>
        </p>
        <p>Best regards,<br/>AI Interview Platform</p>
    </body>
    </html>
    """

    mail_payload = {
        "message": {
            "subject": "Your AI Interview Session — Join Link Inside",
            "body": {
                "contentType": "HTML",
                "content": email_body
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": candidate_email
                    }
                }
            ]
        },
        "saveToSentItems": False
    }

    send_mail_url = f"https://graph.microsoft.com/v1.0/users/{organizer}/sendMail"
    mail_response = requests.post(send_mail_url, headers=headers, json=mail_payload)

    if mail_response.status_code == 202:
        print(f"Email invite sent to {candidate_email}")
    else:
        # Non-fatal — meeting is already created, just log the warning
        print(f"Warning: Could not send email invite to {candidate_email}: "
              f"{mail_response.status_code} — {mail_response.text}")







               raise ValueError(f"Unexpected Gemini response shape ({type(data).__name__}): {data}")






from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta
from app.services.interviewer_scheduler import schedule_interview
from app.services.gemini_service import generate_interview_questions
from app.utils.file_parser import extract_text_from_file
from app.schemas.candidate_schema import InterviewResponseModel
import base64

router = APIRouter()

@router.get("/join-redirect")
def join_redirect(url: str):
    try:
        decoded_url = base64.b64decode(url).decode('utf-8')
    except Exception:
        decoded_url = url
    return RedirectResponse(url=decoded_url)


@router.post("/start-interview", response_model=InterviewResponseModel)
async def start_interview(
    resume_file: UploadFile = File(...),
    jd_file: UploadFile = File(...)
):
    """
    Full AI Interview Pipeline:
    1. Parses uploaded Resume and Job Description files.
    2. Gemini extracts candidate name, email and generates 10 interview questions.
    3. Schedules a Microsoft Teams meeting for the extracted candidate email.
    4. Returns the complete response including meeting link and questions.
    """
    try:
        # Step 1: Extract raw text from uploaded files
        resume_text = await extract_text_from_file(resume_file)
        jd_text = await extract_text_from_file(jd_file)

        # Step 2: Gemini extracts candidate info and generates 10 questions
        gemini_output = await generate_interview_questions(
            resume_text=resume_text,
            jd_text=jd_text
        )

        print(f"Gemini extracted — Name: {gemini_output.candidate_name}, Email: {gemini_output.candidate_email}")

        # Step 3: Schedule Teams meeting using the extracted candidate email
        start_time = datetime.utcnow() + timedelta(minutes=2)
        end_time = start_time + timedelta(minutes=60)

        meeting = schedule_interview(
            candidate_email=str(gemini_output.candidate_email),
            start_time=start_time,
            end_time=end_time
        )

        # Step 4: Return full response
        return InterviewResponseModel(
            candidate_name=gemini_output.candidate_name,
            candidate_email=str(gemini_output.candidate_email),
            resume_text=resume_text,
            job_description_text=jd_text,
            questions=gemini_output.questions,
            meeting_link=meeting["meeting_link"],
            event_id=meeting["event_id"],
            start_time=meeting["start_time"],
            end_time=meeting["end_time"]
        )

    except Exception as e:
        print(f"Error in start_interview pipeline: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )


















        from google.genai import Client, types
from app.core.config import settings
from app.schemas.candidate_schema import GeminiOutputModel
import json

client = Client(api_key=settings.GEMINI_API_KEY)

MODEL_NAME = "gemini-2.0-flash"

SYSTEM_PROMPT = """
You are an expert technical interviewer conducting a live interview directly with the candidate.

Your task has two parts:
1. Extract the candidate's full name and primary email address from the provided Resume.
2. Generate EXACTLY 10 interview questions addressed DIRECTLY TO THE CANDIDATE.

CRITICAL RULE: You MUST speak exactly as if you are talking to the candidate face-to-face. Use "you" and "your". Do NOT ever use the candidate's name or refer to them in the third person.

Structure your 10 questions logically in this exact chronological interview sequence:
- Question 1 (Introductory): Must be asking the candidate to introduce themselves and walk through their professional background.
- Questions 2 and 3 (Introductory): Ask about their professional strengths, career goals, or general soft skills based on their resume.
- Questions 4 to 10 (Technical/Basic): Shift entirely to technical questions evaluating their specific skills, domain knowledge, architectural design capabilities, and problem-solving abilities directly related to the Job Description and their past experience.
"""

async def generate_interview_questions(resume_text: str, jd_text: str) -> GeminiOutputModel:
    """
    Calls Gemini to extract candidate info and generate 10 interview questions.
    Returns a GeminiOutputModel with candidate_name, candidate_email, and questions.
    """
    prompt = f"Resume:\n{resume_text}\n\nJob Description:\n{jd_text}"

    response = client.models.generate_content(
        model=MODEL_NAME,
        contents=prompt,
        config=types.GenerateContentConfig(
            system_instruction=SYSTEM_PROMPT,
            response_mime_type="application/json",
            response_schema=GeminiOutputModel,
        )
    )

    try:
        # Some Gemini SDK versions pre-parse the response — use it directly
        if hasattr(response, "parsed") and response.parsed is not None:
            parsed = response.parsed
            if isinstance(parsed, GeminiOutputModel):
                return parsed
            if isinstance(parsed, list) and len(parsed) == 1:
                parsed = parsed[0]
            if isinstance(parsed, dict):
                return GeminiOutputModel(**parsed)

        # Fallback: manually parse the raw JSON text
        data = json.loads(response.text)
        print("Gemini raw response type:", type(data).__name__)

        # Gemini sometimes wraps the object in a list — unwrap it
        if isinstance(data, list):
            if len(data) == 0:
                raise ValueError("Gemini returned an empty list — no candidate data found.")
            data = data[0]

        if not isinstance(data, dict):
            raise ValueError(f"Unexpected Gemini response shape ({type(data).__name__}): {data}")

        return GeminiOutputModel(**data)

    except (json.JSONDecodeError, ValueError, Exception) as e:
        print("Failed to parse Gemini output:", response.text)
        raise e




        "source": {
            "@odata.type": "#microsoft.graph.participantInfo",
            "identity": {
                "@odata.type": "#microsoft.graph.identitySet",
                "application": {
                    "@odata.type": "#microsoft.graph.identity",
                    "displayName": "AI Interview Bot",
                    "id": process.env.CLIENT_ID
                }
            }
        },














require("dotenv").config();



            const payload = {
        "@odata.type": "#microsoft.graph.call",

        "callbackUri": "https://interview.adamsbridgestage.com/bot-test/calls-test",

        "requestedModalities": ["audio"],

        "mediaConfig": {
            "@odata.type": "#microsoft.graph.serviceHostedMediaConfig"
        },

        "chatInfo": {
            "@odata.type": "#microsoft.graph.chatInfo",
            "threadId": threadId,
            "messageId": "0"
        },

        // 👇 THIS IS THE NEW PART THAT FIXES THE NAME 👇
        "source": {
            "@odata.type": "#microsoft.graph.participantInfo",
            "identity": {
                "@odata.type": "#microsoft.graph.identitySet",
                "application": {
                    "@odata.type": "#microsoft.graph.identity",
                    "displayName": "AI Interview Bot",
                    "id": process.env.CLIENT_ID
                }
            }
        },
        // 👆 NEW PART ENDS HERE 👆

        "meetingInfo": {
            "@odata.type": "#microsoft.graph.organizerMeetingInfo",
            "organizer": {
                "@odata.type": "#microsoft.graph.identitySet",
                "user": {
                    "@odata.type": "#microsoft.graph.identity",
                    "id": organizerId,
                    "tenantId": tenantId
                }
            }
        },

        "tenantId": tenantId
    };
