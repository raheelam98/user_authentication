# user_authentication
user authentication steps

# Authentication

# Authentication

```shell
pip install fastapi sqlmodel bcrypt pyjwt 

poetry add fastapi sqlmodel bcrypt pyjwt
```

```shell
poetry add pydantic[email]
```

```shell
pip install python-multipart

poetry add python-multipart
```


**generate a secure random secret key**

```shell
openssl rand -hex 16
```

**`jose`** library in Python provides tools for handling JSON Web Tokens (JWTs), especially for encoding, decoding, and verifying them. `python-jose` to create and verify tokens.
```bash
pip install python-jose
```

**Encoding: `jwt.encode()`** creates a signed JWT using the specified payload, secret key, and algorithm.
```bash
# Encoding the payload to create a token
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
```

**Decoding: `jwt.decode()`** verifies the token and extracts its payload. If the token is expired or invalid, it raises an error.

```bash
# Encoding the payload to create a token
decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
```

### Create a JWT access token
```bash
from typing import  Optional
import jwt
from datetime import datetime, timedelta

SECRET_KEY = 'secret key'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES =60

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
```

### Get the current user from the provided token
```bash
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import jwt

SECRET_KEY = 'secret key'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES =60

# OAuth2PasswordBearer is used to provide the OAuth2 token URL for token generation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

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
```

#### Passlib is a password hashing library for Python
**`passlib`** library provides secure password hashing utilities, and `CryptContext` is a convenient way to manage hashing schemes.
```bash
pip install passlib
```

```bash
from passlib.context import CryptContext

# CryptContext is used to handle password hashing and verification using bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Function to hash a password
def passwordIntoHash(password: str) -> str:
    return pwd_context.hash(password)

# Function to verify a plain text password against a hashed password
def verifyPassword(plainText: str, hashedPassword: str) -> bool:
    return pwd_context.verify(plainText, hashedPassword)
```

**Hashing:`pwd_context.hash()`** hashes the password using the specified hashing scheme (e.g., bcrypt).

**Verification: `pwd_context.verify()`** checks if a provided password matches the stored hash, returning True if it matches and False otherwise.

#### Login for access toke
```bash
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import SQLModel, Session, select

from app.db.db_connector import  get_session # import from database connector
from app.models.user_model import User  # import from user model
from app.main import verifyPassword, create_access_token # from above code

SECRET_KEY = 'secret key'
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES =60

class Token(SQLModel):
    access_token: str
    token_type: str

# OAuth2PasswordBearer is used to provide the OAuth2 token URL for token generation
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

@app.post("/token", response_model=Token)
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
```

#### calculates the expiration time as a Unix timestamp in seconds
```bash
expire = datetime.now(timezone.utc) + expires_delta
expire_delta = int(expire.timestamp())
```
it easy to store, compare, or include in a JWT (JSON Web Token) payload where a timestamp format is typically required for the exp (expiration) claim

**Calculate Expiration Time**
```bash
expire = datetime.now(timezone.utc) + expires_delta
```
`datetime.now(timezone.utc)` creates a timestamp of the current time in UTC.

`expires_delta` is a timedelta object, often representing the duration a token should be valid (e.g., 1 hour, 24 hours).

`+ expires_delta` adds this duration to the current time to determine the final expiration time (expire).

**Convert Expiration Time to Unix Timestamp**
```bash
expire_delta = int(expire.timestamp())
```

`expire.timestamp()` converts the datetime object to a Unix timestamp, which is the number of seconds that have elapsed since January 1, 1970 (UTC).

`int(...)` converts this float to an integer, stripping away any fractional seconds.

#### Automatically Generating a Unique kid Value for Each Model Instance

```bash
kid: str = Field(default_factory=lambda: uuid.uuid4().hex)
```
This is commonly used in fields where a unique ID (such as kid in a JWT header) is required

 `uuid.uuid4()` generates a random UUID (Universally Unique Identifier).

 `.hex` converts the UUID into a hexadecimal string representation, which is a 32-character string.

`default_factory=lambda:` ... ensures that a new unique kid is generated automatically each time without needing an explicit assignment.

#### Tutorial

**OAuth2**

[OAuth2 with Password (and hashing), Bearer with JWT tokens](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)

[OAuth2 scopes](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/)

[Get Current User](https://fastapi.tiangolo.com/tutorial/security/get-current-user/#create-a-get_current_user-dependency)
