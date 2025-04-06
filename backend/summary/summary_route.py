from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timedelta
from database import get_db
from defendecies import get_current_user

router = APIRouter(prefix='/dashboard')

@router.get("/summary")
async def dashboard_summary(
    start_date: str = Query(None),
    end_date: str = Query(None),
    user_id: str = Depends(get_current_user)
):
    try:
        db = get_db()
        # Default to current month if dates not provided
        today = datetime.today()
        if not start_date:
            start_date = today.replace(day=1).strftime('%Y-%m-%d')
        if not end_date:
            end_date = (today.replace(day=1) + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            end_date = end_date.strftime('%Y-%m-%d')

        # Match user's transactions within the date range
        pipeline = [
            {
                "$match": {
                    "user_id": user_id,
                    "date": {"$gte": start_date, "$lte": end_date}
                }
            },
            {
                "$group": {
                    "_id": "$type",
                    "total": {"$sum": "$amount"},
                    "count": {"$sum": 1}
                }
            }
        ]

        data = await db.transactions.aggregate(pipeline).to_list(None)

        total_income = total_expense = transaction_count = 0

        for item in data:
            if item["_id"] == "income":
                total_income = item["total"]
            elif item["_id"] == "expense":
                total_expense = item["total"]
            transaction_count += item["count"]

        return {
            "start_date": start_date,
            "end_date": end_date,
            "total_income": round(total_income, 2),
            "total_expense": round(total_expense, 2),
            "net_balance": round(total_income - total_expense, 2),
            "transaction_count": transaction_count
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load summary: {str(e)}")
