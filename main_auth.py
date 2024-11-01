# user_service_auth -  app/user_main_auth.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Session, select
from typing import List, Optional
import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext


from app.db.db_connector import create_db_and_tables, DB_SESSION,  get_session,  engine
from app.models.user_model import User, UserUpdateModel,  UserModel , Token, ResetPasswordModel, MessageResponse
from app.schemas.user import RefreshTokenResponse

from app.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_MINUTES

### ========================= *****  ========================= ###

# Lifespan function provided by FastAPI (creates DB table at program startup)
# It creates the table only once; if the table already exists, it won't create it again
async def life_span(app: FastAPI):
    print("Call create tables function during lifespan startup...")
    await create_db_and_tables()  # Properly await table creation
    yield  # Lifespan generator is working correctly

# Create FastAPI instance
app = FastAPI(lifespan=life_span, title='User API')

@app.get('/')
def root_route():
    return {"Welcome to": "User Service"}

### ========================= *****  ========================= ###

# oauth2_scheme sets up the OAuth2 Password Bearer token URL for authentication
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# CryptContext is used to handle password hashing and verification using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Constant for token expiration time (in minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Dependency to get a database session
def get_session():
    with Session(engine) as session:
        yield session

# Function to hash a password
def hash_password(password: str) -> str:
    return pwd_context.hash(password)

# Function to verify a plain text password against a hashed password
def verify_password(plainText: str, hashedPassword: str) -> bool:
    return pwd_context.verify(plainText, hashedPassword)

### ========================= *****  ========================= ###


# Function to create a JWT access token
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()  # Copy the data to encode
    if expires_delta:
        expire = datetime.utcnow() + expires_delta  # Set expiration time if provided
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # Set default expiration time
    to_encode.update({"exp": expire})  # Add expiration time to the data
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Encode the JWT
    return encoded_jwt

# Dependency to get the current user from the token
def get_current_user(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])  # Decode the JWT
        email: str = payload.get("sub")  # Extract email from the token payload
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    except jwt.PyJWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid authentication credentials")
    return email

### ========================= *****  ========================= ###
    
@app.post("/register", response_model=User)
async def register_user(new_user: UserModel, session: DB_SESSION):
    # Check if user already exists
    db_user = session.exec(select(User).where(User.user_email == new_user.user_email)).first()
    print("db_user", db_user)

    if db_user:
        raise HTTPException(
            status_code=409, detail="User with these credentials already exists"
        )

    # Create a new user object
    user = User(
        user_name=new_user.user_name,
        user_email=new_user.user_email,
        user_password= hash_password(new_user.user_password) , # Hash the user password
        user_address=new_user.user_address,
        user_country=new_user.user_country,
        phone_number=new_user.phone_number
    )

    # Add the user to the session
    session.add(user) # Add the user to the session
    session.commit()  # Commit to get the user ID
    session.refresh(user)  # Refresh the user instance
    print("user", user)
    return user

### ========================= *****  ========================= ###    

@app.post("/login", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.user_email == form_data.username)).first()  # Retrieve user by email
    if not user or not verify_password(form_data.password, user.user_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # Set token expiration time
    access_token = create_access_token(data={"sub": user.user_email}, expires_delta=access_token_expires)  # Create access token
    return {"access_token": access_token, "token_type": "bearer"}

### ========================= *****  ========================= ###

@app.get("/users/profile", response_model=User)
def read_users_profile(current_user_email: str = Depends(get_current_user), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.user_email == current_user_email)).first()  # Retrieve user by email
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

### ========================= *****  ========================= ###

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user_update: UserUpdateModel, session: DB_SESSION):
    db_user = session.get(User, user_id)  # Retrieve user by ID
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user_update.model_dump(exclude_unset=True)  # Get the user update data
    for key, value in user_data.items():
        setattr(db_user, key, value)  # Update the user attributes
    session.add(db_user)  # Add the user to the session
    session.commit()  # Commit the transaction
    session.refresh(db_user)  # Refresh the user instance
    return db_user

### ========================= *****  ========================= ###

# Profile section
@app.patch("/profile", response_model=MessageResponse)
async def update_user_profile(profile_data: UserUpdateModel, current_user_email: str = Depends(get_current_user), session: Session = Depends(get_session)):
    # Fetch the current user from the database
    current_user = session.exec(select(User).where(User.user_email == current_user_email)).first()

    # Ensure the current user is a User object
    if not current_user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    # Update the user's profile
    updates = profile_data.model_dump(exclude_unset=True)  # Exclude unset fields
    for key, value in updates.items():
        setattr(current_user, key, value)
    session.add(current_user)
    session.commit()
    
    return {"message": "Profile updated successfully."}

### ========================= *****  ========================= ###

@app.get('/api/get_users')
# Function to retrieve user data from the database
def get_user_from_db(session: DB_SESSION):
    # Create a SQL statement to select all users
    statement = select(User)
    # Execute the statement and get the list of users
    user_list = session.exec(statement).all()

    # If no users found, raise an HTTPException with status code 404
    if not user_list:
        raise HTTPException(status_code=404, detail="User Not Found")
    # Otherwise, return the list of users
    else:
        return user_list
    
### ========================= *****  ========================= ###  
       
# Endpoint to reset password
@app.post("/reset-password", response_model=MessageResponse)
async def reset_password(reset_data: ResetPasswordModel, session: DB_SESSION):
    user = session.exec(select(User).where(User.user_email == reset_data.user_email)).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist"
        )
    
    user.user_password = hash_password(reset_data.new_password)
    session.add(user)
    session.commit()
    session.refresh(user)
    
    return {"message": "Password updated successfully"}

### ========================= *****  ========================= ###

# Endpoint to refresh both access and refresh tokens
@app.post("/refresh", response_model=RefreshTokenResponse)
async def refresh_token(email: str, session: Session = Depends(get_session)):
    """Endpoint to refresh both access and refresh tokens using the user's email."""
    user = session.exec(select(User).where(User.user_email == email)).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Generate a new access token
    new_access_token = create_access_token(data={"sub": user.user_email, "purpose": "access"})
    
    # Generate a new refresh token
    new_refresh_token = create_access_token(
        data={"sub": user.user_email, "purpose": "refresh"},
        expires_delta=timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    )
    
    # Return both tokens
    return {
        "access_token": new_access_token,
        "refresh_token": new_refresh_token,
        "token_type": "bearer"
    }
  
### ========================= *****  ========================= ###

@app.delete("/users/{user_id}", response_model=User)
def delete_user(user_id: int, session: DB_SESSION):
    db_user = session.get(User, user_id)  # Retrieve user by ID
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(db_user)  # Delete the user from the session
    session.commit()  # Commit the transaction
    return db_user

### ========================= *****  ========================= ###
 
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
