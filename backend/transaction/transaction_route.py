from fastapi import HTTPException,status,APIRouter,Depends
from fastapi.security import OAuth2PasswordBearer
from .models import Transaction
from jose import jwt
from config import SECRET_KEY,ALGORITHM
from database import get_db


router = APIRouter()

db = get_db()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/add")
async def add_transaction(transaction: Transaction, token: str = Depends(oauth2_scheme)):
    try:
        # Decode token to extract user details
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        if user_email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

        user = await db.users.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        # Prepare transaction data
        transaction_data = transaction.dict()
        transaction_data["user_id"] = str(user["_id"])

        # Insert into database
        result = await db.transactions.insert_one(transaction_data)
        if not result.inserted_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Transaction addition failed")

        return {"message": "Transaction added successfully", "transaction_id": str(result.inserted_id)}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {str(e)}")



@router.get("/transactions/")
async def get_transactions(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")
        if user_email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

        user = await db.users.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        
        transactions = await db.transactions.find({"user_id": str(user["_id"])}).to_list(100)  # Limit to 100 results
        return transactions

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {str(e)}")
