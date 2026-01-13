from supabase_client import supabase_user

def create_user(email: str, password: str) -> bool:
    try:
        res = supabase_user.auth.sign_up({
            "email": email,
            "password": password
        })
        return res.user is not None
    except Exception as e:
        print(f"[create_user] Error: {e}")
        return False


def authenticate_user(email: str, password: str):
    try:
        res = supabase_user.auth.sign_in_with_password({
            "email": email,
            "password": password
        })
        return res.user.id if res.user else None
    except Exception as e:
        print(f"[authenticate_user] Error: {e}")
        return None
