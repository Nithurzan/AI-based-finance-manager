from fastapi import HTTPException,status,APIRouter,Depends
from fastapi.security import OAuth2PasswordBearer
from defendecies import get_current_user
from .models import Transaction
from database import get_db
from utils.serializer import serialize_documents,serialize_document
from typing import Optional
from datetime import datetime
import joblib
from bson import ObjectId





router = APIRouter()


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
model = joblib.load("expense_categorizer.pkl")


@router.post("/add")
async def add_transaction(transaction: Transaction, token: str = Depends(oauth2_scheme)):
    try:
        db = get_db()
        user = await get_current_user(token)

        transaction_data = transaction.dict()

        if not transaction_data.get("category"):
            transaction_data["category"] = model.predict([transaction_data["description"]])[0]

        transaction_data["user_id"] = str(user["_id"])

        result = await db.transactions.insert_one(transaction_data)
        if not result.inserted_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Transaction addition failed")

        return {
            "message": "Transaction added successfully",
            "transaction_id": str(result.inserted_id)
        }

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {str(e)}")


@router.get("/transactions/")
async def get_transactions(token: str = Depends(oauth2_scheme)):
    try:
        db = get_db()
        user = await get_current_user(token)

        transactions = await db.transactions.find({"user_id": str(user["_id"])}).to_list(length=100)
        return serialize_documents(transactions)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {str(e)}")


@router.get("/transactions/{id}")
async def get_transaction(id: str, token: str = Depends(oauth2_scheme)):
    try:
        db = get_db()
        user = await get_current_user(token)

        transaction = await db.transactions.find_one({"_id": ObjectId(id), "user_id": str(user["_id"])})
        if not transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")

        return serialize_document(transaction)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {str(e)}")


@router.put("/transactions/update/{id}")
async def update_transaction(id: str, updated_data: Transaction, token: str = Depends(oauth2_scheme)):
    try:
        db = get_db()
        user = await get_current_user(token)

        update_result = await db.transactions.update_one(
            {"_id": ObjectId(id), "user_id": str(user["_id"])},
            {"$set": updated_data.dict(exclude_unset=True)}
        )

        if update_result.modified_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not updated")

        return {"message": "Transaction updated successfully"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {str(e)}")


@router.delete("/transactions/delete/{id}")
async def delete_transaction(id: str, token: str = Depends(oauth2_scheme)):
    try:
        db = get_db()
        user = await get_current_user(token)

        delete_result = await db.transactions.delete_one({"_id": ObjectId(id), "user_id": str(user["_id"])})

        if delete_result.deleted_count == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found or already deleted")

        return {"message": "Transaction deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {str(e)}")


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
        db = get_db()
        user = await get_current_user(token)

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

        transactions = await db.transactions.find(filters).to_list(length=100)
        return serialize_documents(transactions)

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error: {str(e)}")
