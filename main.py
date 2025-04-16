import requests
import random
import string


BASE_URL = "https://api.mail.tm"


def get_random_email():
    username = ''.join(random.choices(string.ascii_lowercase + string.digits, k=10))
    domain_resp = requests.get(f"{BASE_URL}/domains").json()
    domain = domain_resp["hydra:member"][0]["domain"]
    return f"{username}@{domain}", "SuperSecure123!"


def create_unique_email():
    for _ in range(5):  # Try up to 5 times
        email, password = get_random_email()
        response = requests.post(f"{BASE_URL}/accounts", json={
            "address": email,
            "password": password
        })
        if response.status_code == 201:
            print(f"✅ Email created: {email}")
            return email, password
        elif response.status_code == 422:
            print("⚠️ Email already exists, retrying...")
            continue
        else:
            print("❌ Unexpected error:", response.json())
            break
    return None, None


def get_token(email, password):
    response = requests.post(f"{BASE_URL}/token", json={
        "address": email,
        "password": password
    })
    return response.json().get("token")


def check_inbox(token):
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/messages", headers=headers)
    return response.json()


# --- Run ---
# email, password = create_unique_email()
# if email:
#     token = get_token(email, password)
#     print("🔑 Token:", token)
#
#     print("📥 Inbox:")
#     print(check_inbox(token))

email = "iwiy5trtyd@ptct.net"
password = "SuperSecure123!"  # Use the correct password!

# Get token
response = requests.post("https://api.mail.tm/token", json={
    "address": email,
    "password": password
})

print("Status Code:", response.status_code)
print("Response JSON:", response.json())

# Only try to get token if it exists
if response.status_code == 200 and "token" in response.json():
    token = response.json()["token"]
    print("🔑 Token:", token)

    # Check inbox
    headers = {"Authorization": f"Bearer {token}"}
    inbox = requests.get("https://api.mail.tm/messages", headers=headers).json()
    print("📥 Inbox:")
    print(inbox)
else:
    print("❌ Login failed. Check your email and password.")
