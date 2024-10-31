# user_service_auth -  user_main_auth.py

from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Session, select
from typing import List, Optional
import bcrypt
import jwt
from datetime import datetime, timedelta

from app.db.db_connector import create_db_and_tables,  get_session,  engine
from app.models.user_model import User, UserUpdateModel,  UserModel , Token

from app.settings import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

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
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Constant for token expiration time (in minutes)
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Dependency to get a database session
def get_session():
    with Session(engine) as session:
        yield session

# Function to hash a password using bcrypt
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

# Function to verify a plain password against a hashed password
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

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

@app.post("/signup", response_model=User)
def signup(user: UserModel, session: Session = Depends(get_session)):
    user.user_password = hash_password(user.user_password)  # Hash the user password
    db_user = User.from_orm(user)  # Create a User ORM instance
    session.add(db_user)  # Add the user to the session
    session.commit()  # Commit the transaction
    session.refresh(db_user)  # Refresh the user instance
    return db_user

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.user_email == form_data.username)).first()  # Retrieve user by email
    if not user or not verify_password(form_data.password, user.user_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)  # Set token expiration time
    access_token = create_access_token(data={"sub": user.user_email}, expires_delta=access_token_expires)  # Create access token
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me", response_model=User)
def read_users_me(current_user_email: str = Depends(get_current_user), session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.user_email == current_user_email)).first()  # Retrieve user by email
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@app.put("/users/{user_id}", response_model=User)
def update_user(user_id: int, user_update: UserUpdateModel, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)  # Retrieve user by ID
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    user_data = user_update.dict(exclude_unset=True)  # Get the user update data
    for key, value in user_data.items():
        setattr(db_user, key, value)  # Update the user attributes
    session.add(db_user)  # Add the user to the session
    session.commit()  # Commit the transaction
    session.refresh(db_user)  # Refresh the user instance
    return db_user

@app.delete("/users/{user_id}", response_model=User)
def delete_user(user_id: int, session: Session = Depends(get_session)):
    db_user = session.get(User, user_id)  # Retrieve user by ID
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    session.delete(db_user)  # Delete the user from the session
    session.commit()  # Commit the transaction
    return db_user

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

### ========================= *****  ========================= ###


