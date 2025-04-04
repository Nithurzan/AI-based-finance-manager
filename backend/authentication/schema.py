from pydantic import BaseModel,EmailStr
from datetime import datetime



class User(BaseModel):
    username: str
    email: EmailStr
    password: str
    created_at: datetime = datetime.utcnow()

class Login(BaseModel):
    email: EmailStr
    password: str

class UserInDB(User):
    hashed_password: str
