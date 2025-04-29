from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class BudgetInput(BaseModel):
    amount: float
    month: Optional[str] = None  #

class BudgetUpdate(BaseModel):
    amount: float

class BudgetResponse(BaseModel):
    user_id: str
    month: str
    amount: float
    created_at: datetime
