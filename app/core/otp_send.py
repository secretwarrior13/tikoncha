import asyncio
import hashlib
import json
import os
import random
import time

import httpx
from dotenv import load_dotenv

load_dotenv()

API_BASE_URL = os.getenv("OTP_API_BASE_URL")
SMS_ENDPOINT = os.getenv("OTP_SMS_ENDPOINT")
USERNAME = os.getenv("OTP_USERNAME")
SECRET_KEY = os.getenv("OTP_SECRET_KEY")
SERVICE_ID = os.getenv("OTP_SERVICE_ID")


def generate_otp(length: int = 6) -> str:
    digits = "0123456789"
    return "".join(random.choice(digits) for _ in range(length))


def generate_transmit_access_token(username: str, secret_key: str, utime: int) -> str:
    access_string = f"TransmitSMS {username} {secret_key} {utime}"
    return hashlib.md5(access_string.encode()).hexdigest()


async def send_otp(phone_number: str, otp_code: str) -> tuple[bool, dict]:

    utime = int(time.time())
    access_token = generate_transmit_access_token(USERNAME, SECRET_KEY, utime)

    headers = {"Content-Type": "application/json", "X-Access-Token": access_token}

    payload = {
        "utime": utime,
        "username": USERNAME,
        "service": {"service": SERVICE_ID},
        "message": {
            "smsid": str(int(time.time())),
            "phone": phone_number,
            "text": f"Tikoncha mobil ilovasida ro'yxatdan o'tish uchun tasdiqlash kodi - {otp_code}",
        },
    }

    try:
        async with httpx.AsyncClient(timeout=10) as client:
            response = await client.post(
                f"{API_BASE_URL}{SMS_ENDPOINT}", headers=headers, json=payload
            )

        if response.status_code == 200:
            result = response.json()
            print("SMS sent successfully!")
            print(f"Transaction ID: {result.get('transactionid')}")
            print(f"SMS ID: {result.get('smsid')}")
            print(f"Parts: {result.get('parts')}")
            return True, result
        else:
            error = response.json()
            print(f"Error sending SMS: {error.get('errorMsg', 'Unknown error')}")
            print(f"Error code: {error.get('errorCode', 'N/A')}")
            return False, error

    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return False, {"error": str(e)}
