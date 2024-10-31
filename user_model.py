# # user_service_auth -  user_model.py
# from sqlmodel import SQLModel, Field
# from typing import Optional
# from pydantic import EmailStr
# # import uuid

# #Create Database Schema using SQLMode
# # Define the UserBase and User models
# class UserBase(SQLModel):
#     user_name: str
#     user_address: str
#     user_country: str
#     phone_number: int = Field(ge=100000000, le=999999999999, description="Must be valid Phone Number with 9 10 11 digit")
          
# class UserAuth(SQLModel):
#     user_email: EmailStr
#     user_password: str

# class UserModel(UserAuth, UserBase):
#     pass 

# class User(UserModel, table=True):
#     user_id: Optional[int] = Field(default=None, primary_key=True)
#     # kid: str = Field(default_factory=lambda: uuid.uuid4().hex)

# class UserUpdateModel(SQLModel):
#     user_name: str | None
#     user_password: str | None
#     user_address: str | None
#     user_country: str | None
#     phone_number: int | None = Field(ge=100000000, le=999999999999, description="Must be valid Phone Number with 9 10 11 digit")
    
# ### ========================= *****  ========================= ###


from sqlmodel import SQLModel, Field
from typing import Optional
from pydantic import EmailStr

class UserBase(SQLModel):
    user_name: str
    user_address: str
    user_country: str
    phone_number: int = Field(ge=100000000, le=999999999999, description="Must be valid Phone Number with 9, 10, or 11 digits")

class UserAuth(SQLModel):
    user_email: EmailStr
    user_password: str

class UserModel(UserAuth, UserBase):
    pass

class User(UserModel, table=True):
    user_id: Optional[int] = Field(default=None, primary_key=True)

class UserUpdateModel(SQLModel):
    user_name: Optional[str]
    user_password: Optional[str]
    user_address: Optional[str]
    user_country: Optional[str]
    phone_number: Optional[int] = Field(ge=100000000, le=999999999999, description="Must be valid Phone Number with 9, 10, or 11 digits")

class Token(SQLModel):
    access_token: str
    token_type: str
     