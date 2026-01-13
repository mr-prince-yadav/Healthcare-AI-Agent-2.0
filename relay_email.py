# relay_email.py
import requests
import os
import json

# Load webhook URL from environment
RELAY_WEBHOOK_URL = os.getenv("RELAY_WEBHOOK_URL")

def send_email(to: str, subject: str, body: str) -> bool:
    """
    Sends an email via Relay webhook.
    Returns True if sent successfully, False otherwise.
    """
    webhook_url = os.getenv("RELAY_WEBHOOK_URL")
    if not webhook_url:
        print("Error: RELAY_WEBHOOK_URL missing in environment!")
        return False

    if not to or not subject or not body:
        print("Error: Missing required email fields (to, subject, body).")
        return False

    payload = {
        "to": to,
        "subject": subject,
        "body": body
    }

    print(f"[Relay Email] Sending payload:\n{json.dumps(payload, indent=2)}")

    try:
        response = requests.post(webhook_url, json=payload, timeout=15)
        response.raise_for_status()
        print(f"[Relay Email] Success: Email sent to {to}")
        return True
    except requests.exceptions.Timeout:
        print(f"[Relay Email] Failed: Request timed out when sending to {to}")
    except requests.exceptions.HTTPError as http_err:
        print(f"[Relay Email] HTTP error occurred: {http_err} - Response: {response.text}")
    except requests.exceptions.RequestException as err:
        print(f"[Relay Email] Request failed: {err}")
    except Exception as e:
        print(f"[Relay Email] Unexpected error: {e}")

    return False
