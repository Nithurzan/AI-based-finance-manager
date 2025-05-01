from fastapi import APIRouter, Depends,HTTPException,Query
from .model import Subscription
from database import get_db
from defendecies import get_current_user
from datetime import datetime, timedelta
import re
from bson import ObjectId



router = APIRouter(prefix="/subscription")


@router.post("/create")
async def create_subscription(subscription: Subscription, user_id: str = Depends(get_current_user)):
    
    try:
        db = get_db()
        # Check if user_id is valid
        if not user_id:
            raise HTTPException(status_code=400, detail="Invalid user ID")
        
        # Parse due_date
        try:
            if re.match(r"^\d+\s+days$", subscription.due_date):  # Match format like "30 days"
                days = int(subscription.due_date.split()[0])
                due_date = datetime.utcnow() + timedelta(days=days)
            
            elif re.match(r"^\d{4}-\d{2}-\d{2}$", subscription.due_date):  # Match format like "YYYY-MM-DD"
                due_date = datetime.strptime(subscription.due_date, "%Y-%m-%d")
            else:
                raise ValueError("Invalid format")
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid due_date format. Use 'YYYY-MM-DD' or '<number> days'.")

        # Create subscription document
        subscription_data = subscription.dict()
        subscription_data["due_date"] = due_date
        subscription_data["created_at"] = datetime.utcnow() # Add created_at field
        subscription_data["user_id"] = str(user_id["_id"])  # Convert user to string
        subscription_data["status"] = "active"  # Default status

        # Save to the database
        result = await db.subscriptions.insert_one(subscription_data)
        return {"message": "Subscription added successfully.", "subscription_id": str(result.inserted_id)}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding subscription: {str(e)}")



@router.get("/all")
async def get_all_subscriptions(user_id: str = Depends(get_current_user)):
    try:
        db = get_db()
        user_id_str = str(user_id["_id"])  # Ensure user_id is a string

        # Fetch all subscriptions for the user
        subscriptions_cursor = db.subscriptions.find({"user_id": user_id_str})
        subscriptions = []


        async for subscription in subscriptions_cursor:
            # Handle due_date formatting
            due_date = subscription["due_date"]
            if isinstance(due_date, datetime):  # If due_date is a datetime object
                due_date = due_date.strftime("%Y-%m-%d")
            elif isinstance(due_date, str):  # If due_date is already a string
                pass
            else:
                raise ValueError("Invalid due_date format in the database.")

            # Check if the subscription is inactive
            is_inactive = datetime.strptime(due_date, "%Y-%m-%d") < datetime.utcnow()
            status = "inactive" if is_inactive else subscription.get("status", "active")

            subscriptions.append({
                "id": str(subscription["_id"]),
                "name": subscription["name"],
                "amount": subscription["amount"],
                "due_date": subscription["due_date"].strftime("%Y-%m-%d"),
                "category": subscription["category"],
                "status": status
            })

        return subscriptions

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching subscriptions: {str(e)}")



@router.get("/{id}")
async def get_subscription_by_id(id: str, user_id: str = Depends(get_current_user)):
    try:
        db = get_db()
        # Ensure user_id is a string
        user_id_str = str(user_id["_id"])

        subscription = await db.subscriptions.find_one({
            "_id": ObjectId(id),
            "user_id": user_id_str
        })

        if not subscription:
            raise HTTPException(status_code=404, detail="Subscription not found")

        # Handle due_date formatting
        due_date = subscription["due_date"]
        if isinstance(due_date, datetime):  # If due_date is a datetime object
            due_date = due_date.strftime("%Y-%m-%d")
        elif isinstance(due_date, str):  # If due_date is already a string
            pass
        else:
            raise ValueError("Invalid due_date format in the database.")


         # Check if the subscription is inactive
        is_inactive = datetime.strptime(due_date, "%Y-%m-%d") < datetime.utcnow()
        status = "inactive" if is_inactive else subscription.get("status", "active")


        return {
            "id": str(subscription["_id"]),
            "name": subscription["name"],
            "amount": subscription["amount"],
            "due_date":subscription["due_date"].strftime("%Y-%m-%d"),
            "category": subscription["category"],
            "status": status
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving subscription: {str(e)}")



@router.put("/{id}")
async def update_subscription(
    id: str,
    update_data: Subscription,
    user_id: dict = Depends(get_current_user)
):
    try:
        db = get_db()
        # Ensure user_id is a string
        user_id_str = str(user_id["_id"])

        # Convert update_data to a dictionary and exclude unset fields
        update_dict = update_data.dict(exclude_unset=True)

        # Validate and parse due_date if provided
        if "due_date" in update_dict:
            try:
                update_dict["due_date"] = datetime.strptime(update_dict["due_date"], "%Y-%m-%d")
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid due_date format. Use 'YYYY-MM-DD'.")

        # Perform the update
        result = await db.subscriptions.update_one(
            {"_id": ObjectId(id), "user_id": user_id_str},
            {"$set": update_dict}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Subscription not found or not authorized")

        # Fetch and return the updated document
        updated_subscription = await db.subscriptions.find_one({"_id": ObjectId(id), "user_id": user_id_str})
        if not updated_subscription:
            raise HTTPException(status_code=404, detail="Subscription not found after update")

        # Format due_date for the response
        due_date = updated_subscription["due_date"]
        if isinstance(due_date, datetime):
            due_date = due_date.strftime("%Y-%m-%d")

        return {
            "id": str(updated_subscription["_id"]),
            "name": updated_subscription["name"],
            "amount": updated_subscription["amount"],
            "due_date": due_date,
            "category": updated_subscription["category"]
        }

    except HTTPException as he:
        raise he  # Re-raise HTTP exceptions
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating subscription: {str(e)}")



@router.delete("/{id}")
async def delete_subscription(id: str, user_id: str = Depends(get_current_user)):
    try:
        db = get_db()
        # Ensure user_id is a string
        user_id_str = str(user_id["_id"])

        result = await db.subscriptions.delete_one({
            "_id": ObjectId(id),
            "user_id": user_id_str
        })

        if result.deleted_count == 0:
            raise HTTPException(status_code=404, detail="Subscription not found or not authorized")

        return {"message": "Subscription deleted successfully."}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting subscription: {str(e)}")

