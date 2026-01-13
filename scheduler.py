# scheduler.py
import time
from reminder import check_and_send_reminders

def start_scheduler(interval=30):
    while True:
        try:
            check_and_send_reminders()
        except Exception as e:
            print(f"[Scheduler Error] {e}")
        time.sleep(interval)
