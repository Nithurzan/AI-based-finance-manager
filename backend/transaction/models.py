from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from enum import Enum

class Type(str,Enum):
    INCOME = "income"
    EXPENSE = "expense"


class Transaction(BaseModel):
    amount: float
    category: str
    type: Type
    date : datetime = datetime.now()

class TransactionInDB(Transaction):
    user_id: str 
    transaction_id: Optional[str]  