from threading import Event, Thread

import schedule

from utils.config_reader import ConfigReader
from utils.jobs import (
    generate_token_every_morning_mtof,
    run_job_every_mon_fri,
    scheduled_jobs_instrument,
)

config = ConfigReader()

# Global event for graceful shutdown
schedule_shutdown_event = Event()

#schedules
def run_schedules():
    schedule.every().sunday.do(scheduled_jobs_instrument, "IDX")
    run_job_every_mon_fri("08:00", scheduled_jobs_instrument, "EQ")
    run_job_every_mon_fri("06:00", generate_token_every_morning_mtof)

    # Run the scheduler loop continuously
    while not schedule_shutdown_event.is_set():
        schedule.run_pending()
        if schedule_shutdown_event.wait(60):
            break


if __name__ == "__main__":
    if config.get("schedule_thread"):
        schedules = Thread(target=run_schedules, name="ScheduleThread")
        schedules.daemon = False
        schedules.start()
