import streamlit as st
import base64
import io

# ------------------- AUTH -------------------
def render_login():
    st.subheader("🔐 Login")
    username = st.text_input("Username", key="login_user")
    password = st.text_input("Password", type="password", key="login_pass")
    return username, password

def render_signup():
    st.subheader("📝 Create Account")
    username = st.text_input("New Username", key="signup_user")
    password = st.text_input("New Password", type="password", key="signup_pass")
    return username, password

def render_logout():
    if st.button("🚪 Logout"):
        st.session_state.clear()
        st.rerun()

# ------------------- LOCATION -------------------
CITY_STATE_DATA = {
    "Delhi": "Delhi", "Mumbai": "Maharashtra", "Pune": "Maharashtra",
    "Bengaluru": "Karnataka", "Chennai": "Tamil Nadu", "Hyderabad": "Telangana",
    "Kolkata": "West Bengal", "Jaipur": "Rajasthan", "Ahmedabad": "Gujarat",
    "Surat": "Gujarat"
}

def get_country_list():
    return ["India", "United States", "United Kingdom", "Canada",
            "Australia", "Germany", "France", "Japan", "Singapore"]

# ------------------- PROFILE VIEW -------------------


def render_profile_view():
    st.header("👤 Profile")
    p = st.session_state.get("profile", {})

    # Create two columns: image | info
    col1, col2 = st.columns([1, 2])  # Adjust ratio as needed

    with col1:
        if "image" in p and p["image"]:
            try:
                img_bytes = base64.b64decode(p["image"])
                st.image(io.BytesIO(img_bytes), width=160)
            except Exception:
                st.warning("Profile image could not be displayed.")

    with col2:
        st.markdown(f"**Name:** {p.get('name','-')}")
        st.markdown(f"**Age:** {p.get('age','-')}")
        st.markdown(f"**Weight:** {p.get('weight','-')} kg")
        st.markdown(f"**Height:** {p.get('height','-')} cm")
        st.markdown(f"**Mobile:** {p.get('mobile','-')}")
        st.markdown(f"**Address:** {p.get('address','-')}")
        city = p.get("city","")
        state = p.get("state","")
        country = p.get("country","")
        st.markdown(f"**Location:** {city}, {state}, {country}")

    st.divider()
    st.info("Edit profile from Settings tab")



# ------------------- PROFILE EDIT / SETTINGS -------------------
def render_profile_edit():
    st.header("⚙️ Settings")

    st.subheader("🧑‍💼 Personal")
    if "profile" not in st.session_state:
        st.session_state.profile = {}
    p = st.session_state.profile

# Image

    image = st.file_uploader("Profile Image", ["png","jpg","jpeg"])
    if image:
        p["image"] = base64.b64encode(image.read()).decode("utf-8")


    p["name"] = st.text_input("Full Name", p.get("name",""))
    p["age"] = st.number_input("Age",0,120,p.get("age",0))
    p["weight"] = st.number_input("Weight (kg)",0,300,p.get("weight",70))
    p["height"] = st.number_input("Height (cm)",50,250,p.get("height",170))
    p["mobile"] = st.text_input("Mobile Number", p.get("mobile",""))

    # ------------------ EMAIL SETTINGS ------------------
    st.subheader("📧 Email Settings")

    # Email input
    p["email"] = st.text_input("Email", p.get("email",""))

    st.info("Emails will be sent via SendGrid. No App Password required.")


    # ------------------------------------------------------



    p["address"] = st.text_area("Address", p.get("address",""))
    st.subheader("📍 Location")
    city_query = st.text_input("Type City", p.get("city_query",""))
    p["city_query"] = city_query
    matches = [c for c in CITY_STATE_DATA if c.lower().startswith(city_query.lower())] if city_query else []
    if matches:
        city = st.selectbox("Select City", matches)
        p["city"] = city
        p["state"] = CITY_STATE_DATA[city]
    p["state"] = st.text_input("State", p.get("state",""))
    p["country"] = st.selectbox("Country", get_country_list(), index=get_country_list().index(p.get("country","India")) if p.get("country","India") in get_country_list() else 0)

    p["blood_group"] = st.selectbox(
        "Blood Group",
        ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"],
        index=["A+","A-","B+","B-","AB+","AB-","O+","O-"].index(p.get("blood_group","A+"))
    )

    p["disease"] = st.text_area("Diseases", p.get("disease",""))
    p["medications"] = st.text_area("Medications", p.get("medications",""))
    p["handicapped"] = st.radio("Physically Handicapped?", ["No","Yes"])

