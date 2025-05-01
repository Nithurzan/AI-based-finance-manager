from pydantic import BaseModel

class Subscription(BaseModel):
    name: str
    amount: float
    due_date: str  # This can be a string or datetime depending on your needs
    category: str
   