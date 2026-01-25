
# 🩺 Healthcare Agent AI

**Healthcare Agent AI** is a Streamlit-based web application that provides a personal healthcare assistant with features such as symptom checking, medication reminders, health tracking, mental health support, appointment scheduling, and personalized recommendations. The backend uses Python and Supabase for user management and data persistence, and AI modules for intelligent insights.

---

## Features

- **User Authentication**
  - Signup/Login with Supabase
  - Profile setup and management
- **Profile Management**
  - Personal details: Name, Age, Weight, Height, Blood Group
  - Location, Address, and Contact
  - Profile image upload
  - Edit and view profile
- **Symptom Checker**
  - AI-powered symptom analysis
  - Categorizes emergency and general symptoms
- **Medication Reminder**
  - Schedule medications by time and day
  - Visual reminders in the app
  - Automatic email reminders
- **Health Tracker**
  - Log heart rate, sleep, steps, glucose
  - BMI calculation and health suggestions
  - AI-based health recommendations
- **Mental Health Support**
  - Conversational AI for mental well-being
  - Chat history and session storage
- **Appointments**
  - Schedule, delete, and reschedule appointments
  - Automatic email notifications
- **Settings**
  - Edit profile, blood group, diseases, medications
  - Save preferences to Supabase
- **Help Chatbot**
  - Ask questions and get AI-driven responses

---

## Technology Stack

- **Frontend:** Streamlit  
- **Backend:** Python 3.x  
- **Database:** Supabase (PostgreSQL)  
- **AI:** LangGraph + LLM (for symptom, health, and mental health analysis)  
- **Email Notifications:** Relay / SendGrid  
- **Scheduler:** Python threading for real-time reminders  

---

## Installation

1. Clone the repository:

```bash
git clone <your-repo-url>
cd healthcare-agent-ai
```

2. Create a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Create a `.env` file in the root directory with your configuration:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your-anon-key
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key

RELAY_API_KEY=your-relay-api-key
RELAY_WORKFLOW_ID=your-workflow-id

EMAIL_HOST=smtp.example.com
EMAIL_PORT=587
EMAIL_USER=your-email
EMAIL_PASS=your-password
```

---

## Running Locally

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## Deployment

### Streamlit Cloud

1. Push your repository to GitHub.  
2. Go to [Streamlit Cloud](https://streamlit.io/cloud) and deploy your app.  
3. Add environment variables in the Streamlit Cloud settings.

### Render

1. Push your repository to GitHub.  
2. Create a new Web Service on [Render](https://render.com).  
3. Set the start command to:

```bash
#!/usr/bin/env bash
streamlit run app.py --server.port $PORT --server.enableCORS false
```

4. Add environment variables in the Render dashboard.  
5. Deploy. Render provides free uptime with some limitations on always-on services.

---

## Project Structure

```
├─ app.py               # Main Streamlit app
├─ auth.py              # Authentication helpers
├─ functions.py         # AI & helper functions
├─ graph_builder.py     # Symptom/Health AI graph
├─ ui.py                # Login, Signup, Profile forms
├─ scheduler.py         # Background scheduler for reminders
├─ supabase_client.py   # Supabase integration
├─ relay_email.py       # Email notifications
├─ requirements.txt
├─ .env
└─ README.md
```

---

## Contributing

1. Fork the repository.  
2. Create a feature branch (`git checkout -b feature/new-feature`).  
3. Commit changes (`git commit -am 'Add new feature'`).  
4. Push to the branch (`git push origin feature/new-feature`).  
5. Create a Pull Request.

---

## Security

- Passwords are hashed  
- No plaintext credentials stored  
- Medical data stored securely using Supabase  

---

## Future Enhancements

- Predictive Health Analytics: Use AI/ML models to analyze trends in user vitals and predict potential health risks  
- SMS & Mobile Push Notifications: Real-time reminders for medications, appointments, and health check-ins via SMS or push notifications  
- Telemedicine & Video Consultations: Integrate virtual doctor appointments and live video consultations  
- Multi-language Support: Add support for multiple languages to reach a wider user base  
- Wearable Device Integration: Connect with smartwatches or fitness trackers to automatically sync heart rate, steps, sleep, and other metrics  
- Advanced Symptom Checker: Expand AI symptom analysis with probabilistic disease predictions and suggested next steps  
- Customizable Dashboard: Allow users to personalize which health metrics and reminders are displayed prominently  
- Family & Caregiver Accounts: Enable users to add dependents and manage their health data collaboratively  
- Data Export & Reports: Generate downloadable health reports (PDF/CSV) for doctors or personal records  
- Enhanced Security & Compliance: Implement encryption at rest, HIPAA/GDPR compliance, and two-factor authentication  
- Integration with External APIs: Incorporate APIs for lab results, pharmacy orders, or nutrition tracking  
- Gamification & Engagement: Add badges, streaks, or challenges to motivate consistent health tracking  

---


## 📃 License

[![License](https://img.shields.io/badge/License-MIT-green.svg)](./LICENSE) This project is open source and intended for educational use.


---
## 👤 About the Author
I am Prince Yadav, a Aspiring Data Analyst!
<br><br>Connect with Me

<p align="left">
  <strong>📧 Email:</strong> <a href= mailto:py63535@gmail.com> py63535@gmail.com </a> <br>
  <strong>🔗 LinkedIn:</strong> <a href="https://www.linkedin.com/in/mr-prince-yadav/">linkedin.com/in/mr-prince-yadav</a>
</p>
<br>
⭐ If you find this repository helpful, please consider giving it a star! <br>

---
