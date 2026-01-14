from supabase_client import supabase_user

def create_user(email: str, password: str) -> bool:
    try:
        # Optional: check if user already exists
        existing = supabase_user.auth.admin.get_user_by_email(email)
        if existing.user:
            print("[create_user] User already exists")
            return False

        res = supabase_user.auth.sign_up({"email": email, "password": password})
        if res.error:
            print(f"[create_user] Supabase error: {res.error.message}")
            return False

        return True

    except Exception as e:
        print(f"[create_user] Exception: {e}")
        return False


def authenticate_user(email: str, password: str):
    try:
        res = supabase_user.auth.sign_in_with_password({"email": email, "password": password})
        if res.error:
            print(f"[authenticate_user] Error: {res.error.message}")
            return None
        return res.user.id if res.user else None
    except Exception as e:
        print(f"[authenticate_user] Exception: {e}")
        return None
