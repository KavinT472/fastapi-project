from fastapi_mail import FastMail,MessageSchema,ConnectionConfig
from pydantic import EmailStr
import random

conf=ConnectionConfig(
    MAIL_USERNAME="kavindspsp@gmail.com",
    MAIL_PASSWORD="qeuscdtfpmesicah",
    MAIL_FROM="kavindspsp@gmail.com",
    MAIL_PORT=587,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=True,       # ✅ Correct TLS setting
    MAIL_SSL_TLS=False,
    USE_CREDENTIALS=True)

def generate_otp():
    return str(random.randint(100000,999999))

async def sent_otp__email(email:EmailStr,otp:str):
    message=MessageSchema(
        subject="Your otp code",
        recipients=[email],
        body=f"Your verification otp is {otp}",
        subtype="plain"
    )
    fm=FastMail(conf)
    await fm.send_message(message)
