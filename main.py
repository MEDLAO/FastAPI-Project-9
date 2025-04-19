from fastapi import FastAPI, HTTPException
import requests
import random
import string
import re

app = FastAPI()

BASE_URL = "https://api.mail.tm"


@app.get("/health")  # Health check endpoint
def health_check():
    return {"status": "healthy"}


@app.get("/")  # Welcome message in multiple languages
def read_root():
    welcome_message = (
        "Welcome! "
        "¡Bienvenido! "
        "欢迎! "
        "नमस्ते! "
        "مرحبًا! "
        "Olá! "
        "Здравствуйте! "
        "Bonjour! "
        "বাংলা! "
        "こんにちは!"
    )
    return {"message": welcome_message}


# Generate a random email address with a fixed secure password
def get_random_email():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    domain_resp = requests.get(f"{BASE_URL}/domains").json()
    domain = domain_resp["hydra:member"][0]["domain"]
    return f"{username}@{domain}", "SuperSecure123!"


# Try to create a new email account, retry up to 5 times if needed
def create_unique_email():
    for _ in range(5):
        email, password = get_random_email()
        response = requests.post(f"{BASE_URL}/accounts", json={
            "address": email,
            "password": password
        })
        if response.status_code == 201:  # Success
            return email, password
        elif response.status_code == 422:  # Already exists
            continue
        else:
            break
    return None, None


# Request JWT token using email and password
def get_token(email, password):
    response = requests.post(f"{BASE_URL}/token", json={
        "address": email,
        "password": password
    })
    if response.status_code == 200:
        return response.json().get("token")
    return None


# Retrieve all messages for a given token
def check_inbox(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/messages", headers=headers)
    return response.json()


@app.post("/create-temp-email")  # Endpoint to create a new temporary email
def create_temp_email():
    email, password = create_unique_email()
    if not email:
        raise HTTPException(status_code=500, detail="Failed to create email")
    return {"email": email, "password": password}


@app.post("/get-inbox")  # Endpoint to get inbox using email credentials
def get_inbox(email: str, password: str):
    token = get_token(email, password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    inbox = check_inbox(token)
    return {"inbox": inbox}


@app.post("/confirm-latest")  # Endpoint to extract and confirm the latest email link
def confirm_latest(email: str, password: str):
    token = get_token(email, password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    inbox = check_inbox(token)
    if inbox["hydra:totalItems"] == 0:
        raise HTTPException(status_code=404, detail="Inbox is empty")

    # Get the ID of the most recent message
    msg_id = inbox["hydra:member"][0]["id"]
    headers = {"Authorization": f"Bearer {token}"}
    message = requests.get(f"{BASE_URL}/messages/{msg_id}", headers=headers).json()

    # Combine plain text and HTML content
    content = message.get("text", "") + message.get("html", "")

    # Search for the first URL in the message content
    match = re.search(r'https?://[^\s"\']+', content)
    if not match:
        raise HTTPException(status_code=404, detail="No confirmation link found")

    link = match.group(0)
    try:
        # Attempt to visit the confirmation link
        confirm_response = requests.get(link, timeout=10)
        return {
            "confirmation_link": link,
            "confirmation_status": confirm_response.status_code
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to visit link: {e}")
