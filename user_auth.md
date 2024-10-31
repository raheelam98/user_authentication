# auth

pip install fastapi sqlmodel bcrypt pyjwt

poetry add fastapi sqlmodel bcrypt pyjwt

pip install bcrypt
poetry add  bcrypt


pip install pydantic

poetry add "pydantic[email]"

poetry add pydantic[email]

pip install python-multipart
poetry add python-multipart

**generate a secure random secret key**

```shell
openssl rand -hex 16
```

**`jose`** library in Python provides tools for handling JSON Web Tokens (JWTs), especially for encoding, decoding, and verifying them. `python-jose` to create and verify tokens.
```bash
pip install python-jose
```

**Encoding: `jwt.encode()`** creates a signed JWT using the specified payload, secret key, and algorithm.

**Decoding: `jwt.decode()`** verifies the token and extracts its payload. If the token is expired or invalid, it raises an error.

```bash
from jose import jwt

# Secret key for encoding/decoding
SECRET_KEY = "your_secret_key"

# Sample data payload
payload = {
    "user_id": 123,
    "username": "user_name",
    "exp": 1704067200  # expiration timestamp (epoch)
}

# Encoding the payload to create a token
token = jwt.encode(payload, SECRET_KEY, algorithm="HS256")
print("Generated JWT:", token)

# Decoding the token to verify and extract the payload
try:
    decoded_payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    print("Decoded payload:", decoded_payload)

except jwt.ExpiredSignatureError:
    print("Token has expired")
except jwt.JWTError:
    print("Invalid token")

```

#### Passlib is a password hashing library for Python
**`passlib`** library provides secure password hashing utilities, and `CryptContext` is a convenient way to manage hashing schemes.
```bash
pip install passlib
```

```bash
from passlib.context import CryptContext

# Define the CryptContext with a hashing scheme (bcrypt is commonly used)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Hashing a password
password = "my_secure_password"
hashed_password = pwd_context.hash(password)
print("Hashed password:", hashed_password)

# Verifying a password against the stored hash
is_correct = pwd_context.verify(password, hashed_password)
print("Password is correct:", is_correct)
```

**Hashing:`pwd_context.hash()`** hashes the password using the specified hashing scheme (e.g., bcrypt).

**Verification: `pwd_context.verify()`** checks if a provided password matches the stored hash, returning True if it matches and False otherwise.


#### Automatically Generating a Unique kid Value for Each Model Instance

```bash
kid: str = Field(default_factory=lambda: uuid.uuid4().hex)
```
This is commonly used in fields where a unique ID (such as kid in a JWT header) is required

 `uuid.uuid4()` generates a random UUID (Universally Unique Identifier).

 `.hex` converts the UUID into a hexadecimal string representation, which is a 32-character string.

`default_factory=lambda:` ... ensures that a new unique kid is generated automatically each time without needing an explicit assignment.

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

#### Tutorial

**OAuth2**

[OAuth2 with Password (and hashing), Bearer with JWT tokens](https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/)

[OAuth2 scopes](https://fastapi.tiangolo.com/advanced/security/oauth2-scopes/)

[Get Current User](https://fastapi.tiangolo.com/tutorial/security/get-current-user/#create-a-get_current_user-dependency)