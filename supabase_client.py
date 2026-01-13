# supabase_client.py
from supabase import create_client
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Hard fail if required env vars are missing
if not SUPABASE_URL or not SUPABASE_ANON_KEY or not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("Supabase environment variables not loaded")

# Create two clients
# User-level client (ANON key) for normal login/signup/profile edits
supabase_user = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

# Admin-level client (SERVICE_ROLE_KEY) for backend scripts / reminders / reading all profiles
supabase_admin = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
