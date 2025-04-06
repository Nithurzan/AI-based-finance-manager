from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from enum import Enum

class Type(str,Enum):
    INCOME = "income"
    EXPENSE = "expense"


class Transaction(BaseModel):
    amount: float
    category: str = None
    type: Type
    description:str
    date: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.strftime('%Y-%m-%d')  # <-- Format here
        }

class TransactionInDB(Transaction):
    user_id: str 
    transaction_id: Optional[str]  