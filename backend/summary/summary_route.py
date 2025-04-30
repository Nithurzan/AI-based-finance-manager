from fastapi import APIRouter, HTTPException, Depends, Query
from datetime import datetime, timedelta
from database import get_db
from defendecies import get_current_user
from bson import ObjectId

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

        # Convert user_id to string
        user_id_str = str(user_id["_id"])

        # Match user's transactions within the date range
        pipeline = [
            {
                "$match": {
                    "user_id": user_id_str,
                    "date": {
                        "$gte": start_date,
                        "$lte": end_date
                    }
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
        print(f"pipeline: {pipeline}")
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




@router.get("/category-wise")
async def category_wise_expense(
    month: str = Query(None),
    user_id: str = Depends(get_current_user)
):
    try:
        db = get_db()
        target_month = month or datetime.now().strftime("%Y-%m")

         # Convert user_id to string
        user_id_str = str(user_id["_id"])

        pipeline = [
            {
                "$match": {
                    "user_id": user_id_str,
                    "type": "expense",
                    "date": {"$regex": f"^{target_month}"}
                }
            },
            {
                "$group": {
                    "_id": "$category",
                    "total": {"$sum": "$amount"}
                }
            }
        ]

        results = await db.transactions.aggregate(pipeline).to_list(None)

        total_expense = sum(item["total"] for item in results)
        breakdown = [{"category": item["_id"], "total": round(item["total"], 2)} for item in results]

        return {
            "month": target_month,
            "breakdown": breakdown,
            "total_expense": round(total_expense, 2)
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load category-wise breakdown: {str(e)}")



@router.get("/monthly-report")
async def monthly_report(
    month: str = Query(None),
    user_id: str = Depends(get_current_user)
):
    try:
        db = get_db()
        target_month = month or datetime.now().strftime("%Y-%m")

        user_id_str = str(user_id["_id"])

        # Aggregate income, expense, count
        pipeline1 = [
            {
                "$match": {
                    "user_id": user_id_str,
                    "date": {"$regex": f"^{target_month}"}
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
        summary = await db.transactions.aggregate(pipeline1).to_list(None)

        total_income = total_expense = transaction_count = 0
        for item in summary:
            if item["_id"] == "income":
                total_income = item["total"]
            elif item["_id"] == "expense":
                total_expense = item["total"]
            transaction_count += item["count"]

        # Category breakdown (only for expenses)   
        pipeline2 = [
            {
                "$match": {
                    "user_id": user_id_str,
                    "type": "expense",
                    "date": {"$regex": f"^{target_month}"}
                }
            },
            {
                "$group": {
                    "_id": "$category",
                    "amount": {"$sum": "$amount"}
                }
            }
        ]
        category_breakdown = await db.transactions.aggregate(pipeline2).to_list(None)
        category_breakdown = [{"category": item["_id"], "amount": round(item["amount"], 2)} for item in category_breakdown]

        return {
            "month": target_month,
            "total_income": round(total_income, 2),
            "total_expense": round(total_expense, 2),
            "net_balance": round(total_income - total_expense, 2),
            "transaction_count": transaction_count,
            "category_breakdown": category_breakdown
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate monthly report: {str(e)}")



@router.get("/yearly-report")
async def yearly_report(
    year: str = Query(None),
    user_id: str = Depends(get_current_user)
):
    try:
        db = get_db()
        target_year = year or datetime.now().strftime("%Y")

        user_id_str = str(user_id["_id"])

        # Aggregate income, expense, count for the year
        pipeline1 = [
            {
                "$match": {
                    "user_id": user_id_str,
                    "date": {"$regex": f"^{target_year}"}
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
        summary = await db.transactions.aggregate(pipeline1).to_list(None)

        total_income = total_expense = transaction_count = 0
        for item in summary:
            if item["_id"] == "income":
                total_income = item["total"]
            elif item["_id"] == "expense":
                total_expense = item["total"]
            transaction_count += item["count"]

        # Category breakdown (only for expenses)
        pipeline2 = [
            {
                "$match": {
                    "user_id": user_id_str,
                    "type": "expense",
                    "date": {"$regex": f"^{target_year}"}
                }
            },
            {
                "$group": {
                    "_id": "$category",
                    "amount": {"$sum": "$amount"}
                }
            }
        ]
        category_breakdown = await db.transactions.aggregate(pipeline2).to_list(None)
        category_breakdown = [{"category": item["_id"], "amount": round(item["amount"], 2)} for item in category_breakdown]

        return {
            "year": target_year,
            "total_income": round(total_income, 2),
            "total_expense": round(total_expense, 2),
            "net_balance": round(total_income - total_expense, 2),
            "transaction_count": transaction_count,
            "category_breakdown": category_breakdown
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate yearly report: {str(e)}")