from fastapi import FastAPI, Depends, HTTPException,BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
import models.models as models, schemas.schemas as schemas
from pydantic import EmailStr
from database.db import SessionLocal, engine
from utils.utils import hash_password,verify_password
from utils.email_utils import generate_otp,sent_otp__email
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from auth.auth import create_access_token
from schemas.schemas import Token
from auth.auth import decode_access_token
from fastapi.openapi.utils import get_openapi


# Create the tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()



def custom_openapi():  #to set up pop-up swaggerdocs(in browser) like token input setup
    if app.openapi_schema: #with out this setup swaggerdocs pop-up looks like login page
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="My Secure API",
        version="1.0.0",
        description="This API uses JWT for authorization",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "apiKey",
            "in": "header",
            "name": "Authorization",
            "description": "Paste your JWT token like: Bearer <token>"
        }
    }
    for path in openapi_schema["paths"]:
        for method in openapi_schema["paths"][path]:
            openapi_schema["paths"][path][method]["security"] = [{"BearerAuth": []}]
    
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi



# @app.post("/register/", response_model=schemas.UserOut)
# def create_user(user: schemas.UserCreate, db: Session = Depends(get_db),background_tasks:BackgroundTasks=None):
#     existing_user=db.query(models.User).filter(models.User.email==user.email).first()
#     if  existing_user:
#         raise HTTPException(status_code=409,detail="email already registered try another email")
    
#     hashed_pw=hash_password(user.password)
#     otp=generate_otp()


#     db_user = models.User(name=user.name,email=user.email,password=hashed_pw,otp=otp)
#     db.add(db_user)
#     db.commit()
#     db.refresh(db_user)
#     background_tasks.add_task(sent_otp__email,user.email,otp)
#     return {
#     "name": db_user.name,
#     "email": db_user.email,
    
# }

# @app.post("/register",response_model=schemas.UserOut)
# def create_user(user:schemas.UserCreate,background_tasks:BackgroundTasks,
#                 db:Session=Depends(get_db)):
#     existing_user=db.query(models.User).filter(models.User.email==user.email).first()
#     if existing_user:
#         raise HTTPException(status_code=404,detail="Email already registered")
#     hashpwd=hash_password(user.password)
#     otp=generate_otp()
#     db_user=models.User(name=user.name,email=user.email,password=hashpwd,otp=otp)
#     db.add(db_user)
#     db.commit()  
#     db.refresh(db_user)
#     background_tasks.add_task(sent_otp__email,user.email,otp)
#     return db_user 

@app.post("/register",response_model=schemas.UserOut)
def create_user(user:schemas.UserCreate,background_tasks:BackgroundTasks,db:Session=Depends(get_db)):
    existing_user=db.query(models.User).filter(models.User.email==user.email).first()
    if existing_user:
        raise HTTPException(status_code=404,detail="Email already registered")
    hashpwd=hash_password(user.password)
    otp=generate_otp()
    db_user=models.User(name=user.name,email=user.email,password=hashpwd,otp=otp)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    background_tasks.add_task(sent_otp__email,user.email,otp)
    return db_user




# @app.post("/verify-otp")
# def verify_otp(email: EmailStr, otp: str, db: Session = Depends(get_db)):
#     user = db.query(models.User).filter(models.User.email == email).first()
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found")

#     if user.otp != otp:
#         raise HTTPException(status_code=400, detail="Invalid OTP")

#     user.is_verified = True
#     user.otp = None  # Clear OTP after verification
#     db.commit()
#     return {"message": "Email verified successfully"}

# @app.post("/verify_otp")
# def verify_otp(email:EmailStr,otp:str,db:Session=Depends(get_db)):
#     user=db.query(models.User).filter(models.User.email==email).first()
#     if not user:
#         raise HTTPException(status_code=404,detail="invalid email")
#     if user.otp!=otp:
#         raise HTTPException(status_code=404,detail="otp incorrect")
#     user.is_verified=True
#     user.otp=None
#     db.commit()
#     return{"message":"Email verification completed successfully"}

@app.post("/verify otp")
def verify_otp(email:EmailStr,otp:str,db:Session=Depends(get_db)):
    user=db.query(models.User).filter(models.User.email==email).first()
    if not user:
        raise HTTPException(status_code=404,detail="invalid email")
    if otp !=otp:
        raise HTTPException(status_code=404,detail="invalid otp")
    user.is_verified=True
    user.otp=None
    db.commit()
    return {"message":f"Email verification is completed successfully for {user.name} "}
    

@app.post("/login",response_model=Token)
def login(user: schemas.Login, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(models.User.email == user.email).first()
    if not db_user:
        raise HTTPException(status_code=400, detail="Invalid email")
    
    if not verify_password(user.password, db_user.password):
        raise HTTPException(status_code=400, detail="Incorrect password")

    token = create_access_token(data={"sub": db_user.email})
    return {"message":"login successfully","access_token": token, "token_type": "bearer"}

@app.get("/user", response_model=schemas.UserOut)
def read_user(user_name: str=None, email:str=None,db: Session = Depends(get_db)):
    if user_name:
        user = db.query(models.User).filter(models.User.name == user_name).first()
    elif email:
        user = db.query(models.User).filter(models.User.email == email).first()
    if user is None:
        raise HTTPException(status_code=404,detail="user not found please provide valid name or valid email")
    return user    

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    email = payload["sub"]
    user = db.query(models.User).filter(models.User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user
@app.get("/profile", response_model=schemas.UserOut)
def read_profile(current_user: models.User = Depends(get_current_user)):
    return current_user

@app.get("/get_all",response_model=List[schemas.UserOut])
def get_all_users(current_user: models.User=Depends(get_current_user),
                  db:Session=Depends(get_db)):
    all_user= db.query(models.User).all()
    return all_user

@app.get("/get_by_id",response_model=schemas.UserOut)
def get_by_id(user_id:int ,current_user:models.User=Depends(get_current_user),
              db:Session=Depends(get_db)):
    user=db.query(models.User).filter(models.User.id==user_id).first()
    if not user:
        raise HTTPException (status_code=404,detail=" id not found")
    return user

@app.get("/get_by_name",response_model=schemas.UserOut)
def get_by_name(user_name:str ,current_user:models.User=Depends(get_current_user),
              db:Session=Depends(get_db)):
    user=db.query(models.User).filter(models.User.name==user_name).first()
    if not user:
        raise HTTPException (status_code=404,detail=" user not found")
    return user

@app.put("/update_user", response_model=schemas.UserOut)
def update_user(updated_data: schemas.UserUpdate, current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == current_user.email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if updated_data.name:
        user.name = updated_data.name
    if updated_data.password:
        user.password = hash_password(updated_data.password)
    db.commit()
    db.refresh(user)
    return user

# @app.get("/user/{user_email}", response_model=schemas.UserOut)
# def read_user(user_email: str, db: Session = Depends(get_db)):
#     user = db.query(models.User).filter(models.User.email == user_email).first()
#     print(user)
#     if user is None:
#         raise HTTPException(status_code=404, detail="User not found")
#     return user

# @app.get("/users")
# def get_all_users(db:Session=Depends(get_db)):
#     return db.query(models.User).all()
@app.delete("/delete_user")
def delete_user(current_user: models.User = Depends(get_current_user),db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == current_user.email).first()
   
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    db.delete(user)
    db.commit()
    return {"detail": "User deleted successfully"}

    
