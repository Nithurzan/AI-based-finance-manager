from pydantic import BaseModel
from datetime import datetime


class User(BaseModel):
    username: str
    email: str
    password: str
    created_at: datetime = datetime.utcnow()


class UserInDB(User):
    hashed_password: str