from fastapi import FastAPI, HTTPException
import requests
import random
import string

app = FastAPI()

BASE_URL = "https://api.mail.tm"


def get_random_email():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    domain_resp = requests.get(f"{BASE_URL}/domains").json()
    domain = domain_resp["hydra:member"][0]["domain"]
    return f"{username}@{domain}", "SuperSecure123!"


def create_unique_email():
    for _ in range(5):
        email, password = get_random_email()
        response = requests.post(f"{BASE_URL}/accounts", json={
            "address": email,
            "password": password
        })
        if response.status_code == 201:
            return email, password
        elif response.status_code == 422:
            continue
        else:
            break
    return None, None


def get_token(email, password):
    response = requests.post(f"{BASE_URL}/token", json={
        "address": email,
        "password": password
    })
    if response.status_code == 200:
        return response.json().get("token")
    return None


def check_inbox(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/messages", headers=headers)
    return response.json()


@app.get("/")
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


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/create-temp-email")
def create_temp_email():
    email, password = create_unique_email()
    if not email:
        raise HTTPException(status_code=500, detail="Failed to create email")
    return {"email": email, "password": password}


@app.post("/get-inbox")
def get_inbox(email: str, password: str):
    token = get_token(email, password)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid email or password")
    inbox = check_inbox(token)
    return {"inbox": inbox}
