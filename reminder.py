# reminder.py
from supabase_client import supabase_admin
from datetime import datetime, timedelta
from relay_email import send_email
import pytz
import traceback

IST = pytz.timezone("Asia/Kolkata")

# -------------------- Database helpers --------------------
def load_all_profiles():
    """Fetch all profiles from Supabase."""
    res = supabase_admin.table("profiles").select("user_id, data").execute()
    return {row["user_id"]: row["data"] for row in res.data}

# -------------------- Sent trackers --------------------
sent_medication_reminders = set()         # (user_id, med_name, date)
sent_appointment_reminders = set()        # (user_id, appt_str)
sent_immediate_appointments = set()       # (user_id, appt_str, action)

# -------------------- Reminder & Immediate email logic --------------------
DAY_ABBR = {"Monday":"Mon","Tuesday":"Tue","Wednesday":"Wed",
            "Thursday":"Thu","Friday":"Fri","Saturday":"Sat","Sunday":"Sun"}

def check_and_send_reminders():
    now = datetime.now(IST)
    today_str = now.strftime("%Y-%m-%d")
    current_day_abbr = now.strftime("%a")  # "Mon", "Tue", etc.

    profiles = load_all_profiles()

    for user_id, profile in profiles.items():
        email = profile.get("email")
        if not email:
            continue

        # ----- Medication reminders (1 min before) -----
        for med in profile.get("medication_list", []):
            med_name = med.get("med_name")
            med_time_str = med.get("time")
            med_days = med.get("days", [])

            if not med_name or not med_time_str or not med_days:
                continue

            med_days = [DAY_ABBR.get(d, d) for d in med_days]
            if current_day_abbr not in med_days:
                continue

            try:
                med_dt = IST.localize(datetime.combine(now.date(), datetime.strptime(med_time_str, "%H:%M").time()))
                reminder_dt = med_dt - timedelta(minutes=1)
            except Exception:
                continue

            key = (user_id, med_name, today_str)
            if key in sent_medication_reminders:
                continue

            # Send if current time is within ±1 minute of reminder
            if abs((now - reminder_dt).total_seconds()) <= 60:
                subject = f"Medication Reminder: {med_name}"
                body = f"Dear {profile.get('name','User')},\n\nIt's time to take {med_name} at {med_time_str} today."
                try:
                    sent = send_email(to=email, subject=subject, body=body)
                    if sent:
                        sent_medication_reminders.add(key)
                        print(f"[{now}] Medication reminder sent to {user_id} for {med_name}")
                    else:
                        print(f"[{now}] Failed to send medication reminder to {user_id}")
                except Exception:
                    print(f"[{now}] Error sending medication reminder to {user_id}:\n{traceback.format_exc()}")

        # ----- Appointment reminders (1 min before) -----
        for appt in profile.get("appointments", []):
            try:
                appt_dt = IST.localize(datetime.fromisoformat(appt))
                reminder_dt = appt_dt - timedelta(minutes=1)
                key = (user_id, appt)

                if key not in sent_appointment_reminders:
                    if abs((now - reminder_dt).total_seconds()) <= 60:
                        subject = "Appointment Reminder"
                        body = f"Dear {profile.get('name','User')},\n\nReminder: You have an upcoming appointment:\n{appt}"
                        sent = send_email(to=email, subject=subject, body=body)
                        if sent:
                            sent_appointment_reminders.add(key)
                            print(f"[{now}] Appointment reminder sent to {user_id} for {appt}")
                        else:
                            print(f"[{now}] Failed to send appointment reminder to {user_id}")
            except Exception:
                print(f"[{now}] Error parsing appointment for {user_id}:\n{traceback.format_exc()}")

# ----- Immediate appointment emails -----
def send_appointment_email(user_id, appointment_str, action, new_appt=None):
    profiles = load_all_profiles()
    profile = profiles.get(user_id)
    if not profile:
        return

    email = profile.get("email")
    if not email:
        return

    key = (user_id, appointment_str, action)
    if key in sent_immediate_appointments:
        return

    if action == "scheduled":
        subject = "Appointment Scheduled"
        body = f"Dear {profile.get('name','User')},\n\nYour appointment has been scheduled:\n{appointment_str}"
    elif action == "deleted":
        subject = "Appointment Cancelled"
        body = f"Dear {profile.get('name','User')},\n\nYour appointment scheduled for {appointment_str} has been cancelled."
    elif action == "rescheduled":
        subject = "Appointment Rescheduled"
        if new_appt:
            body = f"Dear {profile.get('name','User')},\n\nYour appointment has been rescheduled:\nFrom: {appointment_str}\nTo: {new_appt}"
        else:
            body = f"Dear {profile.get('name','User')},\n\nYour appointment has been rescheduled:\n{appointment_str}"
    else:
        return

    try:
        sent = send_email(to=email, subject=subject, body=body)
        if sent:
            sent_immediate_appointments.add(key)
            print(f"[{datetime.now()}] {action.capitalize()} email sent to {user_id} for {appointment_str}")
        else:
            print(f"[{datetime.now()}] Failed to send {action} email to {user_id}")
    except Exception:
        print(f"[{datetime.now()}] Error sending {action} email to {user_id}:\n{traceback.format_exc()}")
