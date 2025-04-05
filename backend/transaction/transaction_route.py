from fastapi import HTTPException,status,APIRouter,Depends
from fastapi.security import OAuth2PasswordBearer
from .models import Transaction
from jose import jwt
from config import SECRET_KEY,ALGORITHM
from database import get_db
from utils.serializer import serialize_documents,serialize_document

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
        return serialize_documents(transactions)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {str(e)}")
    


from bson import ObjectId

@router.get("/transactions/{id}")
async def get_transaction(id: str, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")

        user = await db.users.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        transaction = await db.transactions.find_one({"_id": ObjectId(id), "user_id": str(user["_id"])})
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")

        return serialize_document(transaction)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    


@router.put("/transactions/update/{id}")
async def update_transaction(id: str, updated_data: Transaction, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")

        user = await db.users.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        update_result = await db.transactions.update_one(
            {"_id": ObjectId(id), "user_id": str(user["_id"])},
            {"$set": updated_data.dict(exclude_unset = True)}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=404, detail="Transaction not updated")

        return {"message": "Transaction updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")



@router.delete("/transactions/delete/{id}")
async def delete_transaction(id: str, token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")

        user = await db.users.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        delete_result = await db.transactions.delete_one({"_id": ObjectId(id), "user_id": str(user["_id"])})

        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Transaction not found or already deleted")

        return {"message": "Transaction deleted successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")
    



from fastapi import Query
from typing import Optional
from datetime import datetime

@router.get("/transactions/filter")
async def filter_transactions(
    category: Optional[str] = None,
    min_amount: Optional[float] = None,
    max_amount: Optional[float] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    token: str = Depends(oauth2_scheme)
):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_email = payload.get("sub")

        user = await db.users.find_one({"email": user_email})
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        filters = {"user_id": str(user["_id"])}
        if category:
            filters["category"] = category
        if min_amount is not None or max_amount is not None:
            filters["amount"] = {}
            if min_amount is not None:
                filters["amount"]["$gte"] = min_amount
            if max_amount is not None:
                filters["amount"]["$lte"] = max_amount
        if start_date or end_date:
            filters["date"] = {}
            if start_date:
                filters["date"]["$gte"] = start_date
            if end_date:
                filters["date"]["$lte"] = end_date

        transactions = await db.transactions.find(filters).to_list(100)
        return transactions
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Error: {str(e)}")

