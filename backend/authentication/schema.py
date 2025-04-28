from pydantic import BaseModel,EmailStr
from datetime import datetime



class User(BaseModel):
    username: str
    email: EmailStr
    password: str
    

class Login(BaseModel):
    email: EmailStr
    password: str

class UserInDB(User):
    hashed_password: str
