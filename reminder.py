# reminder.py
from supabase_client import supabase_admin
from datetime import datetime, timedelta
from relay_email import send_email

import pytz
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
        DAY_ABBR = {"Monday":"Mon","Tuesday":"Tue","Wednesday":"Wed",
                    "Thursday":"Thu","Friday":"Fri","Saturday":"Sat","Sunday":"Sun"}

        for med in profile.get("medication_list", []):
            med_time_str = med.get("time")
            med_days = med.get("days", [])

            if not med_time_str or not med_days:
                continue

            # Normalize day abbreviations
            med_days = [DAY_ABBR.get(d, d) for d in med_days]

            # Only send if today is in selected days
            if current_day_abbr not in med_days:
                continue

            # Combine date + time
            med_dt = datetime.combine(now.date(), datetime.strptime(med_time_str, "%H:%M").time())
            reminder_dt = med_dt - timedelta(minutes=1)

            key = (user_id, med["med_name"], med_time_str, today_str)
            if key in sent_medication_reminders:
                continue

            # Send if current time is within ±1 minute of med time
            if abs((reminder_dt - now).total_seconds()) <= 180:
                subject = f"Medication Reminder: {med['med_name']}"
                body = (
                    f"Dear {profile.get('name','User')},\n\n"
                    f"It's time to take {med['med_name']} at {med_time_str} today."
                )
                sent = send_email(to=email, subject=subject, body=body)
                print("[REMINDER EMAIL]", email, "SENT =", sent)
                if sent:
                    sent_medication_reminders.add(key)
                    print(f"[{now}] Medication reminder sent to {user_id} for {med['med_name']}")
                else:
                    print(f"[{now}] Failed to send medication reminder to {user_id}")

            # Debug
            print(f"[{now}] Checked medication {med['med_name']} for {profile.get('name')}, today is {current_day_abbr}, med_days={med_days}")

        # ----- Appointment reminders (1 min before) -----
        for appt in profile.get("appointments", []):
            try:
                appt_date = datetime.strptime(appt.split()[0], "%Y-%m-%d").date()
                appt_time = datetime.strptime(appt.split()[1], "%H:%M:%S").time()
                appt_dt = datetime.combine(appt_date, appt_time)
                reminder_dt = appt_dt - timedelta(minutes=1)

                key = (user_id, appt)
                if key not in sent_appointment_reminders:
                    if reminder_dt <= now <= reminder_dt + timedelta(minutes=1):
                        subject = "Appointment Reminder"
                        body = (
                            f"Dear {profile.get('name','User')},\n\n"
                            f"Reminder: You have an upcoming appointment:\n{appt}"
                        )
                        sent = send_email(to=email, subject=subject, body=body)
                        if sent:
                            sent_appointment_reminders.add(key)
                            print(f"[{now}] Appointment reminder sent to {user_id} for {appt}")
                        else:
                            print(f"[{now}] Failed to send appointment reminder to {user_id}")
            except Exception as e:
                print(f"[{now}] Error parsing appointment for {user_id}: {e}")

# ----- Immediate appointment emails -----
def send_appointment_email(user_id, appointment_str, action, new_appt=None):
    """
    Sends immediate email notifications for appointments.
    action: 'scheduled', 'deleted', 'rescheduled'
    new_appt: optional, required if action=='rescheduled'
    """
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
        body = (
            f"Dear {profile.get('name','User')},\n\n"
            f"Your appointment has been scheduled:\n{appointment_str}"
        )
    elif action == "deleted":
        subject = "Appointment Cancelled"
        body = (
            f"Dear {profile.get('name','User')},\n\n"
            f"Your appointment scheduled for {appointment_str} has been cancelled."
        )
    elif action == "rescheduled":
        subject = "Appointment Rescheduled"
        if new_appt:
            body = (
                f"Dear {profile.get('name','User')},\n\n"
                f"Your appointment has been rescheduled:\nFrom: {appointment_str}\nTo: {new_appt}"
            )
        else:
            body = (
                f"Dear {profile.get('name','User')},\n\n"
                f"Your appointment has been rescheduled:\n{appointment_str}"
            )
    else:
        return

    sent = send_email(to=email, subject=subject, body=body)
    if sent:
        sent_immediate_appointments.add(key)
        print(f"[{datetime.now()}] {action.capitalize()} email sent to {user_id} for {appointment_str}")
    else:
        print(f"[{datetime.now()}] Failed to send {action} email to {user_id}")


