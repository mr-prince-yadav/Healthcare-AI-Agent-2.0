import streamlit as st
import random
from reminder import send_appointment_email  


from relay_email import send_email
from dotenv import load_dotenv
from health_engine import generate_recommendations

from supabase_client import supabase_user, supabase_admin

import threading
from scheduler import start_scheduler



import json

from datetime import datetime, timedelta
from auth import create_user, authenticate_user

from graph_builder import build_graph
from functions import llm, HumanMessage
from ui import render_login, render_signup, render_profile_view, render_profile_edit

import base64
from PIL import Image
from io import BytesIO

supabase=supabase_user
load_dotenv()


# ---------------------- DATABASE HELPERS ----------------------
def load_profile(user_id):
    res = supabase.table("profiles").select("data").eq("user_id", user_id).execute()
    return res.data[0]["data"] if res.data else {}

def save_profile(user_id, profile):
    supabase.table("profiles").upsert({
        "user_id": user_id,
        "data": profile
    }).execute()


# ---------------------- INIT ----------------------
st.set_page_config(page_title="Healthcare Agent")
st.markdown("""
<style>

/* ================== ROOT / THEME ================== */
:root {
    --radius: 14px;
    --shadow: 0 8px 24px rgba(0,0,0,.08);
}

.stApp {
    background-color: var(--background-color);
    color: var(--text-color);
}

/* ================== LAYOUT FIXES ================== */
section.main > div {
    padding-top: 1rem;
    overflow-x: hidden;
}

/* ================== CARDS ================== */
.health-card,
.stAlert,
.stInfo,
.stSuccess,
.stWarning,
.stError {
    background-color: var(--secondary-background-color) !important;
    border-radius: var(--radius);
    box-shadow: var(--shadow);
    border: none !important;
}

/* ================== BUTTONS ================== */
.stButton button {
    border-radius: 12px;
    font-weight: 600;
    padding: 0.55rem 1rem;
}

.stButton button:hover {
    transform: translateY(-1px);
}

/* ================== INPUTS ================== */
input,
textarea,
select {
    background-color: var(--secondary-background-color) !important;
    color: var(--text-color) !important;
    border-radius: 12px !important;
    border: 1px solid rgba(128,128,128,0.25) !important;
}

/* ================== CHAT ================== */
.stChatMessage {
    background-color: var(--secondary-background-color);
    border-radius: 14px;
    padding: 10px;
    margin-bottom: 8px;
    box-shadow: var(--shadow);
}

.stChatInputContainer {
    position: sticky;
    bottom: 0;
    background-color: var(--background-color);
    padding-top: 10px;
}

/* ================== TABS (NO CLIPPING EVER) ================== */
div[data-baseweb="tab-list"] {
    display: flex !important;
    justify-content: flex-start !important;
    gap: 10px;
    padding: 10px 16px;
    background-color: var(--secondary-background-color);
    border-radius: 16px;
    overflow-x: auto !important;
    scrollbar-width: none;
}

div[data-baseweb="tab-list"]::-webkit-scrollbar {
    display: none;
}

button[data-baseweb="tab"] {
    min-width: 56px;
    height: 48px;
    background-color: var(--background-color);
    color: var(--text-color);
    border-radius: 14px;
    font-size: 18px;
    border: 1px solid rgba(128,128,128,0.2);
    transition: all 0.2s ease;
}

/* ACTIVE TAB */
button[data-baseweb="tab"][aria-selected="true"] {
    background: linear-gradient(135deg, #667eea, #764ba2);
    color: white !important;
    border: none;
    box-shadow: 0 6px 18px rgba(102,126,234,0.4);
}

/* ================== HEADERS ================== */
h1, h2, h3, h4 {
    font-weight: 700;
}

/* ================== METRICS ================== */
[data-testid="stMetricValue"] {
    font-size: 1.4rem;
}

/* ================== IMAGE ================== */
img {
    border-radius: 14px;
}

/* ================== MOBILE ================== */
@media (max-width: 768px) {
    section.main > div {
        padding: 0.5rem;
    }
    button[data-baseweb="tab"] {
        min-width: 46px;
        height: 42px;
        font-size: 16px;
    }
}

</style>
""", unsafe_allow_html=True)



# ---------------- SCHEDULER BOOTSTRAP ----------------
if "scheduler_started" not in st.session_state:
    scheduler_thread = threading.Thread(
        target=start_scheduler,
        daemon=True
    )
    scheduler_thread.start()
    st.session_state.scheduler_started = True

# ---------------------- MAIN ----------------------
def main():
    # ---------------- SESSION STATE ----------------
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    if "user_id" not in st.session_state:
        st.session_state.user_id = None

    if "profile" not in st.session_state:
        st.session_state.profile = {}
    if "profile_completed" not in st.session_state:
        st.session_state.profile_completed = False

    # ---------------- LOGIN / SIGNUP ----------------
    if not st.session_state.logged_in:
        img = Image.open("loading.png")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        st.markdown(f"""
            <div style='text-align: center;'>
                <img src="data:image/png;base64,{img_str}" width="300"/>
            </div>
        """, unsafe_allow_html=True)

        st.markdown(
            "<h1 style='text-align:center;'>🏥 Healthcare Agent</h1>",
                    unsafe_allow_html=True
                
        )
        t1, t2 = st.tabs(["Login", "Sign Up"])
        with t1:
            u, p = render_login()
    
            if st.button("Login"):
                user_id = authenticate_user(u, p)
                if user_id:
                    st.session_state.logged_in = True
                    st.session_state.user_id = user_id

                    profile = load_profile(user_id)
                    if profile:
                        st.session_state.profile = profile
                        st.session_state.profile_completed = True
                    else:
                        st.session_state.profile = {}
                        st.session_state.profile_completed = False

                    st.rerun()
                else:
                    st.error("Invalid credentials")

        with t2:
            u, p = render_signup()
            if st.button("Create Account"):
                if create_user(u, p):
                    st.success(
                         "Account created successfully.\n\n"
                         "🚨 A confirmation email has been sent to your registered email address.\n\n"
                         "🚨 Please confirm your email before logging in."
                    )
                else:
                    st.error(
                        "⚠️ Account already exists.\n\n"
                        "⚠️ A confirmation email has been sent to your registered email address.\n\n"
                        "⚠️ Please confirm your email before logging in."
                    )
        return  # Stop until login done

    # ---------------- FIRST TIME PROFILE COMPLETION ----------------
    if not st.session_state.profile_completed:
        st.warning("Please complete your profile first")
        render_profile_edit()
        required = ["name","age","weight","height","mobile"]
        p = st.session_state.profile
        if all(p.get(r) for r in required):
            if st.button("✅ Finish Profile Setup"):
                save_profile(st.session_state.user_id, p)

                st.session_state.profile_completed = True
                st.rerun()
        return  # Stop until profile completed

    # ---------------- MAIN TABS ----------------
    tabs = st.tabs([
        "👤",
        "🩺",
        "💊",
        "📊",
        "🧠",
        "📅",
        "🤖",
        "⚙️"
    ])

    # ---------------- PROFILE TAB ----------------
    with tabs[0]:
        render_profile_view()
        st.subheader("💡 Fitness & Wellness Tips")
        p = st.session_state.profile
        age = p.get("age",30)
        weight = p.get("weight",70)
        height_m = p.get("height",170)/100
        bmi = round(weight / (height_m**2),1)
        disease = p.get("disease","").lower()
        tips = [f"📏 Your BMI: {bmi}"]
        if age < 30:
            tips.append("🏃‍♂️ 30 min cardio daily")
        else:
            tips.append("🚶‍♀️ 20 min walking daily")
        if "diabetes" in disease:
            tips.append("🥗 Avoid sugary foods")
        else:
            tips.append("🥗 Eat balanced diet with vegetables and proteins")
        for t in tips:
            st.info(t)

        # Real-time reminders (visual in app)
        # Real-time reminders (visual in app)
        

        now = datetime.now()
        email = st.session_state.profile.get("email") or ""

        
        st.subheader("⏰ Real-time Reminders")
        current_day = now.strftime("%a")
        current_time = now.strftime("%H:%M")
        reminders = []

        

        now = datetime.now()
        current_day = now.strftime("%a")  # Mon, Tue, etc.

        reminders = []
        for m in st.session_state.profile.get("medication_list", []):
            if current_day not in m.get("days", []):
                continue
            med_time = datetime.strptime(m["time"], "%H:%M").time()
            med_dt = datetime.combine(now.date(), med_time)
            # 1-minute window for triggering reminder
            if med_dt - timedelta(minutes=1) <= now <= med_dt + timedelta(minutes=1):
                reminders.append(f"⏰ Time to take {m['med_name']}!")


        if reminders:
            st.warning("\n".join(reminders))
        else:
            st.info("No alarms currently.")
        # ✅ LOGOUT BUTTON (PASTE HERE)
        st.divider()
        if st.button("🚪 Logout", type="primary"):
            st.session_state.clear()
            st.rerun()

        ################### 
        st.divider()
        st.subheader("⚠️ Delete Account")

        if "show_delete_confirm" not in st.session_state:
            st.session_state.show_delete_confirm = False

        if st.button("🗑️ Delete My Account"):
            st.session_state.show_delete_confirm = True

        if st.session_state.show_delete_confirm:
            confirm_text = st.text_input(
                'Type "CONFIRM" to permanently delete your account',
                key="confirm_delete_text"
            )

            if st.button("OK", key="confirm_delete_btn"):
                if confirm_text != "CONFIRM":
                    st.error('You must type exactly "CONFIRM"')
                else:
                    user_id = st.session_state.user_id

                    # ---- DELETE USER DATA ----
                    supabase_admin.table("profiles").delete().eq("user_id", user_id).execute()

                    try:
                        supabase_admin.table("medications").delete().eq("user_id", user_id).execute()
                        supabase_admin.table("appointments").delete().eq("user_id", user_id).execute()
                        supabase_admin.table("health_logs").delete().eq("user_id", user_id).execute()
                    except:
                        pass

                    # ---- DELETE AUTH USER ----
                    supabase_admin.auth.admin.delete_user(user_id)

                    # ---- CLEAR SESSION ----
                    st.session_state.clear()
                    st.success("Account permanently deleted")
                    st.rerun()



    # ---------------- SYMPTOM CHECKER TAB ----------------
    with tabs[1]:
        st.subheader("🩺 Symptom Checker")
        symptom = st.text_input("Describe your symptom")
        if st.button("Analyze Symptom"):
            if symptom:
                graph = build_graph()
                result = graph.invoke({
                    "symptom": symptom,
                    "profile": st.session_state.profile
                })
                category = result.get("category")
                st.success(result.get("answer"))
                if category:
                    st.caption(f"Category: {category}")
                if category == "emergency":
                    st.warning("🚨 Emergency detected! Seek immediate attention.")
                st.session_state.profile["last_symptom"] = symptom
                save_profile(st.session_state.user_id,st.session_state.profile)

    # ---------------- MEDICATION REMINDER TAB ----------------
    with tabs[2]:
        st.subheader("💊 Medication Reminder")

        med_options = ["Aspirin","Vitamin D","Metformin","Ibuprofen","Other"]
        med_name = st.selectbox("Select Medication", med_options, key="med_select")

        if med_name == "Other":
            med_name = st.text_input("Enter Medication Name", key="other_med_name")

        med_time = st.time_input("Select Time", key="med_time_input", step=60)

        days = st.multiselect(
            "Select Day(s)", 
            ["Mon","Tue","Wed","Thu","Fri","Sat","Sun"],
            key="med_days_select"
        )

        if "medication_list" not in st.session_state.profile:
            st.session_state.profile["medication_list"] = []

        # ADD MEDICATION
        DAY_ABBR = {"Monday":"Mon","Tuesday":"Tue","Wednesday":"Wed","Thursday":"Thu",
            "Friday":"Fri","Saturday":"Sat","Sunday":"Sun"}

        if st.button("💾 Add Medication", key="add_med_button"):
            if med_name and days:
                DAY_ABBR = {"Monday":"Mon","Tuesday":"Tue","Wednesday":"Wed",
                            "Thursday":"Thu","Friday":"Fri","Saturday":"Sat","Sunday":"Sun"}

                # Normalize days before saving
                days = [DAY_ABBR.get(d, d) for d in days]

                entry = {"med_name": med_name, "time": med_time.strftime("%H:%M"), "days": days}
                st.session_state.profile["medication_list"].append(entry)
                save_profile(st.session_state.user_id,st.session_state.profile)

                st.success(f"{med_name} scheduled at {entry['time']} on {', '.join(days)}")
                # Remove direct assignment to session_state; rerun will reset multiselect
                st.rerun()

            else:
                st.error("Please enter medication name and select days.")


        # CLEAR ALL MEDICATIONS
        if st.button("🗑️ Clear All Medications"):
            st.session_state.profile["medication_list"] = []
            save_profile(st.session_state.user_id,st.session_state.profile)
            st.rerun()  # clear instantly

        # SHOW UPCOMING MEDICATIONS
        st.subheader("Upcoming Medications")
        med_list = st.session_state.profile.get("medication_list", [])
        if med_list:
            for i, m in enumerate(med_list):
                st.info(f"{m['med_name']} @ {m['time']} on {', '.join(m['days'])}")
        else:
            st.info("No upcoming medications scheduled.")

    # ---------------- HEALTH TRACKER TAB ----------------
    with tabs[3]:
        st.subheader("📊 Health Tracker")
        p = st.session_state.profile
        p["heart_rate"] = st.number_input("Heart Rate (bpm)",value=p.get("heart_rate",70))
        p["sleep_hours"] = st.number_input("Sleep Hours",value=p.get("sleep_hours",7))
        p["steps"] = st.number_input("Steps Today",value=p.get("steps",0))
        p["glucose"] = st.number_input("Blood Glucose (mg/dL)",value=p.get("glucose",90))
        if st.button("💾 Save Health Data"):
            st.session_state.profile = p
            save_profile(st.session_state.user_id, p)


            weight = p.get("weight",70)
            height_m = p.get("height",170)/100
            bmi = round(weight/(height_m**2),1)
            condition = "Stable"
            tasks = []
            if bmi<18.5:
                condition="Needs Attention"
                tasks.append("Increase caloric intake with protein and healthy fats")
            elif bmi>25 or p.get("glucose",90)>140:
                condition="Critical"
                tasks.append("Reduce sugar intake and consult a doctor")
            if p.get("sleep_hours",7)<6:
                condition="Needs Attention"
                tasks.append("Sleep 7-8 hours daily")
            if p.get("steps",0)<5000:
                tasks.append("Walk at least 5000 steps daily")
            if p.get("heart_rate",70)<50 or p.get("heart_rate",70)>100:
                tasks.append("Monitor heart rate; consult a doctor if abnormal")
            st.info(f"Condition: {condition}")
            if tasks:
                st.write("Tasks to improve your health:")
                for t in tasks:
                    st.success(f"- {t}")

            st.subheader("🍎 Personalized Diet Suggestions")
            age = p.get("age",30)
            diet=[]
            if bmi<18.5:
                diet.append("Include protein-rich foods and healthy fats")
            elif bmi>25:
                diet.append("Reduce sugar, refined carbs, increase vegetables and fruits")
            else:
                diet.append("Maintain balanced diet with fruits, veggies, proteins")
            if "diabetes" in p.get("disease","").lower():
                diet.append("Avoid sugary drinks and desserts")
            for d in diet:
                st.info(d)

            # ---- AI HEALTH RECOMMENDATIONS ----
            st.subheader("🧠 Health Recommendations")

            for r in generate_recommendations(p):
                st.success(r)

    # ---------------- MENTAL HEALTH TAB ----------------
    with tabs[4]:
        st.subheader("🧠 Mental Health Chat")

        if "mental_chat" not in st.session_state:
            st.session_state.mental_chat = []

        # Show Clear Chat button
        if st.button("🗑️ Clear Chat"):
            st.session_state.mental_chat = []
            st.success("Chat cleared!")

        msg = st.text_input("Type your message")

        if st.button("Send", key="mental_chat_send"):
            if msg.strip():
                st.session_state.mental_chat.append(("user", msg))

                prompt = f"""
                You are a mental health and healthcare assistant.
                User profile: {json.dumps(st.session_state.profile)}
                Conversation: {st.session_state.mental_chat}
                """

                reply = llm.invoke([HumanMessage(content=prompt)]).content
                st.session_state.mental_chat.append(("assistant", reply))

        # Display chat
        for role, m in st.session_state.mental_chat:
            st.chat_message(role).write(m)


    # ---------------- APPOINTMENTS TAB ----------------
    # ---------------- APPOINTMENTS TAB ----------------
    with tabs[5]:
        st.subheader("📅 Appointment Scheduler")
        email = st.session_state.profile.get("email") or ""


        # Doctor categories
        DOCTORS = {
            "General": ["Dr. Anil", "Dr. Meera", "Dr. Ramesh"],
            "Emergency": ["Dr. Karthik", "Dr. Priya", "Dr. Rohan"],
            "Mental Health": ["Dr. Maya", "Dr. Sanjay", "Dr. Neha"]
        }

        # Schedule new appointment
        st.markdown("### Schedule New Appointment")
        date = st.date_input("Select Date", key="appt_date_new")
        time_input = st.time_input("Select Time", key="appt_time_new")
        doctor_type = st.selectbox("Select Doctor Type", ["General", "Emergency", "Mental Health"])
        doctor = random.choice(DOCTORS[doctor_type])
        st.markdown(f"**Assigned Doctor:** {doctor}")

        if st.button("Schedule Appointment"):
            appointments = st.session_state.profile.get("appointments", [])
            appt_str = f"{date} {time_input} with {doctor} ({doctor_type})"
            appointments.append(appt_str)
            st.session_state.profile["appointments"] = appointments
            save_profile(st.session_state.user_id,st.session_state.profile)

            # Send instant email after scheduling
            
            send_appointment_email(st.session_state.user_id, appt_str, action="scheduled")

            st.success(f"Appointment scheduled with {doctor}!")
            st.info("Reminder emails will be sent automatically by the background scheduler.")

        # Display upcoming appointments with delete/reschedule
        st.markdown("### Upcoming Appointments")
        appointments = st.session_state.profile.get("appointments", [])

        for i, a in enumerate(appointments):
            st.info(a)
            col1, col2 = st.columns([1, 1])

            # Delete appointment
            with col1:
                if st.button(f"🗑️ Delete #{i}", key=f"del_{i}"):
                    removed = appointments.pop(i)
                    st.session_state.profile["appointments"] = appointments
                    save_profile(st.session_state.user_id,st.session_state.profile)

                    # Send instant email after deletion
                    
                    send_appointment_email(st.session_state.user_id, removed, action="deleted")

                    st.success(f"Appointment deleted: {removed}")
                    st.rerun()

            # Reschedule appointment
            with col2:
                resch_key = f"resch_inputs_{i}"
                if resch_key not in st.session_state:
                    st.session_state[resch_key] = {
                        "show": False,
                        "new_date": None,
                        "new_time": None
                    }

                if st.button(f"🔄 Reschedule #{i}", key=f"resch_{i}"):
                    st.session_state[resch_key]["show"] = True
                    old_appt = appointments[i]
                    st.session_state[resch_key]["new_date"] = datetime.strptime(old_appt.split()[0], "%Y-%m-%d").date()
                    st.session_state[resch_key]["new_time"] = datetime.strptime(old_appt.split()[1], "%H:%M:%S").time()

                if st.session_state[resch_key]["show"]:
                    old_appt = appointments[i]
                    new_date = st.date_input(f"New Date #{i}",
                                            value=st.session_state[resch_key]["new_date"],
                                            key=f"new_date_{i}")
                    new_time = st.time_input(f"New Time #{i}",
                                            value=st.session_state[resch_key]["new_time"],
                                            key=f"new_time_{i}")
                    st.session_state[resch_key]["new_date"] = new_date
                    st.session_state[resch_key]["new_time"] = new_time

                    old_type = old_appt.split("(")[-1].replace(")", "")
                    new_doctor = random.choice(DOCTORS[old_type])
                    st.markdown(f"**New Assigned Doctor:** {new_doctor}")

                    if st.button(f"💾 Save Reschedule #{i}", key=f"save_resch_{i}"):
                        old_appt = appointments[i]
                        appointments[i] = f"{new_date} {new_time} with {new_doctor} ({old_type})"
                        st.session_state.profile["appointments"] = appointments
                        save_profile(st.session_state.user_id,st.session_state.profile)

                        # Send instant email after reschedule
                        
                        send_appointment_email(
                            st.session_state.user_id,
                            old_appt,
                            action="rescheduled"
                        )

                        st.success(f"Appointment rescheduled:\nFrom: {old_appt}\nTo: {appointments[i]}")
                        st.session_state[resch_key]["show"] = False
                        st.rerun()

    # ---------------- HELP TAB ----------------
    with tabs[6]:
        st.subheader("🤖 Help Chatbot")
        query = st.text_input("Ask a question")
        if st.button("Send", key="help_chat_send"):
            if query:
                prompt = f"User profile: {json.dumps(st.session_state.profile)}\nUser question: {query}"
                response = llm.invoke([HumanMessage(content=prompt)])
                st.info(response.content)
       
        # ---------------- SETTINGS TAB ----------------
    with tabs[7]:
        st.subheader("⚙️ Settings")

        # Toggle between Edit and Saved, default to Saved
        mode = st.radio("Mode:", ["Saved", "Edit"], index=0, horizontal=True)  # Saved default

        p = st.session_state.profile

        if mode == "Edit":
            render_profile_edit()  # Editable
            if st.button("💾 Save Profile Changes"):
                save_profile(st.session_state.user_id, st.session_state.profile)
                st.success("Profile updated!")
        else:
            # Read-only view: show all fields from render_profile_edit
            st.write("### Your Profile Data")
            st.text(f"Name: {p.get('name','')}")
            st.text(f"Age: {p.get('age','')}")
            st.text(f"Weight: {p.get('weight','')} kg")
            st.text(f"Height: {p.get('height','')} cm")
            st.text(f"Mobile: {p.get('mobile','')}")
            st.text(f"Email: {p.get('email','')}")
            st.text(f"Disease: {p.get('disease','')}")
            st.text(f"Blood Group: {p.get('blood_group','')}")
            st.text(f"Medications: {', '.join([m['med_name'] for m in p.get('medication_list', [])])}")
            st.text(f"Appointments: {len(p.get('appointments', []))} scheduled")

if __name__=="__main__":
    main()










