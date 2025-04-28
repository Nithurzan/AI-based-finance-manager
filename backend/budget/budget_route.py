from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime
from .model import BudgetInput
from database import db  # your MongoDB client
from defendecies import get_current_user

router = APIRouter()

@router.post("/budget/set")
async def set_budget(data: BudgetInput, user_id: str = Depends(get_current_user)):
    try:
        # Use provided month or default to current month
        month = data.month or datetime.now().strftime("%Y-%m")
        
        # Check if budget already exists for this user and month
        existing_budget = await db.budgets.find_one({"user_id": user_id, "month": month})
        if existing_budget:
            raise HTTPException(status_code=400, detail="Budget already exists for this month")

        # Create budget entry
        budget_doc = {
            "user_id": user_id,
            "month": month,
            "amount": data.amount,
            "created_at": datetime.utcnow()
        }

        await db.budgets.insert_one(budget_doc)

        return {"message": "Budget set successfully", "month": month, "amount": data.amount}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set budget: {str(e)}")




@router.get("/budget/get")
async def get_budget(month: str = Query(None), user_id: str = Depends(get_current_user)):
    try:
        # Use current month if not provided
        target_month = month or datetime.now().strftime("%Y-%m")

        # Find the budget
        budget = await db.budgets.find_one({"user_id": user_id, "month": target_month})
        if not budget:
            raise HTTPException(status_code=404, detail="No budget found for the selected month")

        return {
            "month": budget["month"],
            "amount": budget["amount"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve budget: {str(e)}")
    



@router.put("/budget/update")
async def update_budget(data: BudgetInput, user_id: str = Depends(get_current_user)):
    try:
        month = data.month or datetime.now().strftime("%Y-%m")

        # Find and update budget
        result = await db.budgets.update_one(
            {"user_id": user_id, "month": month},
            {"$set": {"amount": data.amount}}
        )

        if result.modified_count == 0:
            raise HTTPException(status_code=404, detail="No budget found to update")

        return {"message": "Budget updated successfully", "month": month, "amount": data.amount}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update budget: {str(e)}")
    


@router.delete("/budget/delete")
async def delete_budget(month: str = Query(None), user_id: str = Depends(get_current_user)):
    try:
        target_month = month or datetime.now().strftime("%Y-%m")

        result = await db.budgets.delete_one({"user_id": user_id, "month": target_month})
        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="No budget found to delete")

        return {"message": "Budget deleted successfully", "month": target_month}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete budget: {str(e)}")
    


@router.get("/budget/track-progress")
async def track_budget_progress(month: str = Query(None), user_id: str = Depends(get_current_user)):
    try:
        target_month = month or datetime.now().strftime("%Y-%m")

        # Get budget
        budget = await db.budgets.find_one({"user_id": user_id, "month": target_month})
        if not budget:
            raise HTTPException(status_code=404, detail="No budget found for this month")

        # Get total spending for the month
        transactions = db.transactions.aggregate([
            {
                "$match": {
                    "user_id": user_id,
                    "date": {"$regex": f"^{target_month}"},
                    "type": "expense"
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_spent": {"$sum": "$amount"}
                }
            }
        ])

        spent_data = await transactions.to_list(1)
        total_spent = spent_data[0]["total_spent"] if spent_data else 0.0

        remaining = budget["amount"] - total_spent
        percentage_used = round((total_spent / budget["amount"]) * 100, 2)

        return {
            "month": target_month,
            "budget": budget["amount"],
            "total_spent": total_spent,
            "remaining_budget": remaining,
            "percentage_used": percentage_used
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to track budget progress: {str(e)}")

