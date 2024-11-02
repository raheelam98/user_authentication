# user_service_auth -  app/user_main.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import  Session, select
from typing import  Optional
import jwt
from datetime import datetime, timedelta

from app.db.db_connector import create_db_and_tables,  get_session,  DB_SESSION  
from app.models.user_model import Token, User, UserUpdateModel,  UserModel 
from app.controllers.user_crud import (add_user_into_db, get_user_from_db, update_user_from_db, delete_user_from_db)

from app.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

### ========================= *****  ========================= ###


# async def life_span(app: FastAPI):
#     print("Call create tables function during lifespan startup...")
#     await create_db_and_tables()  # Properly await table creation
#     yield  # Lifespan generator is working correctly

# # Lifespan function provided by FastAPI (creates DB table at program startup)
# # It creates the table only once; if the table already exists, it won't create it again
# # Create FastAPI instance
# app = FastAPI(lifespan=life_span, title='Product API')

app = FastAPI(lifespan = create_db_and_tables)

@app.get('/')
def root_route():
    return {"Welcome to": "User Service"}

### ========================= *****  ========================= ###

from passlib.context import CryptContext

# OAuth2PasswordBearer is used to provide the OAuth2 token URL for token generation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="user_login")

# CryptContext is used to handle password hashing and verification using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

### ========================= *****  ========================= ###

# Function to create a JWT access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()  # Create a copy of the data to encode
    if expires_delta:
        # Set the expiration time if provided
        expire = datetime.utcnow() + expires_delta
    else:
        # Default expiration time
        expire = datetime.utcnow() + ACCESS_TOKEN_EXPIRE_MINUTES
    to_encode.update({"exp": expire})  # Add the expiration time to the data
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Encode the JWT
    return encoded_jwt

### ========================= *****  ========================= ###

# Function to hash a password
def passwordIntoHash(password: str) -> str:
    return pwd_context.hash(password)

# Function to verify a plain text password against a hashed password
def verifyPassword(plainText: str, hashedPassword: str) -> bool:
    return pwd_context.verify(plainText, hashedPassword)

### ========================= *****  ========================= ###

# Function to get the current user from the provided token
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        # Decode the JWT token using the secret key and specified algorithm
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        
        # Extract the email (subject) from the decoded payload
        email: str = payload.get("sub")
        
        # If the email is not found in the payload, raise an unauthorized exception
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )
    except jwt.PyJWTError:
        # If there's an error decoding the token, raise an unauthorized exception
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    # Return the extracted email
    return email

### ========================= *****  ========================= ###

# POST route to add a new user
@app.post('/api/register_user')
def add_user(new_user: UserModel, session: DB_SESSION):
    # Call function to add user
    add_user = add_user_into_db(new_user, session)
    print("Add user route ...", add_user)
    return add_user

### ========================= *****  ========================= ###

@app.post("/user_login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    # Retrieve the user from the database using the provided email
    user = session.exec(select(User).where(User.user_email == form_data.username)).first()
    
    # If the user does not exist or the password is incorrect, raise an unauthorized exception
    if not user or not verifyPassword(form_data.password, user.user_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Set the token expiration time
    access_token_expires = ACCESS_TOKEN_EXPIRE_MINUTES
    
    # Create the access token with the user's email as the subject
    access_token = create_access_token(data={"sub": user.user_email}, expires_delta=access_token_expires)
    
    # Print the access token (for debugging purposes)
    print("access_token ...", access_token)
    
    # Return the access token and its type
    return {"access_token": access_token, "token_type": "bearer"}

### ========================= *****  ========================= ###

@app.get("/auth_users/profile", response_model=User)
def read_users_profile(current_user_email: str = Depends(get_current_user), session: Session = Depends(get_session)):
    # Retrieve the user from the database using the current user's email
    user = session.exec(select(User).where(User.user_email == current_user_email)).first()
    
    # If the user is not found, raise a 404 (Not Found) exception
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Return the user details
    return user

### ========================= *****  ========================= ###

# API endpoint to get users
@app.get('/api/get_users')
def get_users(session: DB_SESSION):
    # Call the function to retrieve user data from the database
    users = get_user_from_db(session)
    # Return the list of users
    return users

### ========================= *****  ========================= ###

@app.put('/api/update_user')
def update_user(id:int, user_detail: UserUpdateModel, session: DB_SESSION):
    # Call the function to retrieve data from the database
    user = update_user_from_db(id, user_detail, session)
    return user

### ========================= *****  ========================= ###

# API endpoint to delete a user
@app.delete('/api/delete_user')
def delete_user(id: int, session: DB_SESSION):
    # Call function to delete the user from the database
    deleted_user = delete_user_from_db(id, session)
    return f'User id {id} has been successfully deleted'

### ========================= *****  ========================= ###
