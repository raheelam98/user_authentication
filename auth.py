# user_service_auth  -  app/utils/auth.py

from datetime import datetime, timedelta, timezone
from passlib.context import CryptContext
from jose import jwt

from app.models.user_model import User
from app.db.db_connector import DB_SESSION
from app.settings import SECRET_KEY, ALGORITHM

from fastapi.security import OAuth2PasswordBearer


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(subject: str, expires_delta: timedelta) -> str:
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {"sub": subject, "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def passwordIntoHash(password: str) -> str:
    return pwd_context.hash(password)

def verifyPassword(plainText: str, hashedPassword: str) -> bool:
    return pwd_context.verify(plainText, hashedPassword)











# oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token/v1")

# pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto" )

# ### ========================= *****  ========================= ###

# def create_access_token(subject: str, expires_delta: timedelta) -> str:
#     """
#     Generate a JSON Web Token (JWT) with an expiration time.

#     Args:
#         subject (str): The subject for whom the token is generated.
#         expires_delta (timedelta): The duration after which the token expires.

#     Returns:
#         str: The generated JWT token.
#     """
#     expire = datetime.now(timezone.utc) + expires_delta
#     to_encode = {"sub": subject, "exp": expire}
#     encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

#     print("Generated JWT", encoded_jwt )
#     return encoded_jwt

# ### ========================= *****  ========================= ###

# def passwordIntoHash(password: str) -> str:
#     """
#     Hashes the provided password using bcrypt.

#     Args:
#         password (str): The password to be hashed.

#     Returns:
#         str: The hashed password.
#     """
#     hash_password = pwd_context.hash(password)
#     return hash_password

# ### ========================= *****  ========================= ###

# def verifyPassword(plainText: str, hashedPassword: str) -> bool:
#     """
#     Verifies if the provided plaintext password matches the hashed password.

#     Args:
#         plainText (str): The plaintext password.
#         hashedPassword (str): The hashed password to compare against.

#     Returns:
#         bool: True if the passwords match, False otherwise.
#     """
#     # Print the plaintext and hashed passwords for debugging
#     print(plainText, hashedPassword)

#     # Verify if the plaintext password matches the hashed password
#     isPasswordCorrect = pwd_context.verify(plainText, hash=hashedPassword)

#     # Print the result of password verification for debugging
#     print(isPasswordCorrect)

#     return isPasswordCorrect




### ========================= *****  ========================= ###

# def generateToken(user: User, expires_delta: timedelta) -> str:
#     """
#     Generate a token.

#     Args:
#         data (dict): User data to be encoded.
#         expires_delta (timedelta): Expiry time for the token.

#     Returns:
#         str: Generated token.
#     """

#     # Calculate expiry time
#     expire = datetime.now(timezone.utc) + expires_delta
#     expire_delta = int(expire.timestamp())

#     payload = {
#         "user_name": user.user_name,
#         "user_email": user.user_email,
#         "exp": expire_delta
#     }
#     headers = {
#         "iss": user.kid,
#         "kid": user.kid
#     }


#     # Encode token with user data and secret key
#     token = jwt.encode(payload, SECRET_KEY,
#                        algorithm=ALGORITHM, headers=headers)
#     return token

### ========================= *****  ========================= ###

# def create_token(data: dict, expires_delta: timedelta):
#     to_encode = data.copy()

#     if expires_delta:
#         expire = datetime.now(timezone.utc) + expires_delta
#     else:
#         expire = datetime.now(timezone.utc) + timedelta(minutes=15)
#     to_encode.update({"exp": expire})
#     encoded_jwt_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

#     print("Generated JWT", encoded_jwt_token )

#     return encoded_jwt_token