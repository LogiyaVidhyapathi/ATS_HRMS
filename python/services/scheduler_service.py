from apscheduler.schedulers.background import BackgroundScheduler
from app.services.bot_trigger_service import trigger_bot_join
import pytz

scheduler = BackgroundScheduler(timezone =pytz.UTC)

def start_schedule():
    print("Scheduler Started")
    scheduler.start()

def schedule_bot_join(join_url, start_time):

    print("Scheduling bot join")
    print("join_url:", join_url)
    print("start_time:", start_time)

    scheduler.add_job(
        trigger_bot_join, 
        trigger = "date", 
        run_date = start_time, 
        args = [join_url]
    )