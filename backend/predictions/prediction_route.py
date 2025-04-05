from statistics import LinearRegression
from fastapi import APIRouter,status,HTTPException,Depends
from fastapi.security import OAuth2PasswordBearer
import joblib
import numpy as np
from database import get_db
from collections import defaultdict
from datetime import datetime
from defendecies import get_current_user



router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")



@router.get("/ai/spending-analyseis")
async def spending_analysis(token:str = Depends(oauth2_scheme)):
    try:
        db = get_db()

        user = await get_current_user(token)

        pipeline = [
            {"$match": {"user_id": str(user["_id"])}},
            {"$group": {
                "_id": {
                    "month": {"$substr": ["$date", 0, 7]},
                    "category": "$category"
                },
                "total": {"$sum": "$amount"}
            }},
            {"$sort": {"_id.month": 1, "total": -1}}
        ]
        result = await db.transactions.aggregate(pipeline).to_list(None)

        monthly_spending = defaultdict(lambda: {})
        for r in result:
            month = r["_id"]["month"]
            cat = r["_id"]["category"]
            amt = r["total"]
            monthly_spending[month][cat] = amt

        return {"monthly_spending": monthly_spending}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
    




@router.get("/ai/budget-prediction")
async def budget_prediction(token: str = Depends(oauth2_scheme)):
    try:
        db = get_db()
        user = await get_current_user(token)
       
        pipeline = [
            {"$match": {"user_id": str(user["_id"])}},
            {"$group": {
                "_id": {"$substr": ["$date", 0, 7]},  # YYYY-MM
                "total": {"$sum": "$amount"}
            }},
            {"$sort": {"_id": 1}}  # Sort by month
        ]
        monthly_data = await db.transactions.aggregate(pipeline).to_list(None)

        if len(monthly_data) < 2:
            raise HTTPException(status_code=400, detail="Not enough data for prediction")

        
        months = list(range(len(monthly_data)))
        totals = [entry["total"] for entry in monthly_data]

        X = np.array(months).reshape(-1, 1)
        y = np.array(totals)

        model = LinearRegression()
        model.fit(X, y)

        # Predict next month
        next_month_index = [[len(monthly_data)]]
        prediction = model.predict(next_month_index)[0]

        return {"next_month_expense_prediction": round(prediction, 2)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction error: {str(e)}")




@router.get("/ai/savings-suggestions")
async def savings_suggestions(token: str = Depends(oauth2_scheme)):
    try:
        db = get_db()
        
        user = await get_current_user(token)

        # Calculate category-wise spending
        pipeline = [
            {"$match": {"user_id": str(user["_id"])}},
            {"$group": {"_id": "$category", "total": {"$sum": "$amount"}}},
            {"$sort": {"total": -1}}
        ]
        spending = await db.transactions.aggregate(pipeline).to_list(None)

        tips = []
        for item in spending[:3]:
            cat = item["_id"]
            if cat.lower() in ["entertainment", "food & drink", "shopping"]:
                tips.append(f"Consider reducing your spending on '{cat}'")

        return {
            "suggestions": tips or ["Spending is balanced. Keep it up!"]
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")
