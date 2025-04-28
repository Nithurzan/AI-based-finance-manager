from pydantic import BaseModel, Field, field_serializer
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

    @field_serializer("date")
    def serialize_date(self, date: datetime, _info):
        return date.strftime("%Y-%m-%d")  

class TransactionInDB(Transaction):
    user_id: str 
    transaction_id: Optional[str]  