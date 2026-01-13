import os
from dotenv import load_dotenv

load_dotenv()  # load environment variables from .env

GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
if not GOOGLE_API_KEY:
    raise RuntimeError("GOOGLE_API_KEY not found")

RELAY_WEBHOOK_URL = os.getenv("RELAY_WEBHOOK_URL")
if not RELAY_WEBHOOK_URL:
    raise RuntimeError("RELAY_WEBHOOK_URL not found")

SUPABASE_URL = os.getenv("SUPABASE_URL")
if not SUPABASE_URL:
    raise RuntimeError("RSUPABASE_URL not found")

SUPABASE_URL = os.getenv("SUPABASE_URL")
if not SUPABASE_URL:
    raise RuntimeError("SUPABASE_URL not found")

SUPABASE_ANON_KEY = os.getenv("SUPABASE_ANON_KEY")
if not SUPABASE_ANON_KEY:
    raise RuntimeError("SUPABASE_ANON_KEY not found")

SUPABASE_SERVICE_ROLE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
if not SUPABASE_SERVICE_ROLE_KEY:
    raise RuntimeError("SUPABASE_SERVICE_ROLE_KEY not found")