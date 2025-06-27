from sqlalchemy import Column, Integer, String,Boolean
from database.db import Base
   

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100))
    email = Column(String(100), unique=True, index=True)
    password=Column(String(100))
    otp = Column(String(6))  # store OTP
    is_verified = Column(Boolean, default=False)
