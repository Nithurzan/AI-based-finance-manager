from fastapi import HTTPException,status,APIRouter
from .schema import User
from .auth import password_hash
from Backend.database import get_db 


router = APIRouter()


@router.post("/regiester")
async def register_user(user:User):
    try:
        db = await get_db() 
        user_dict = user.dict()

        existing_user = await db.users.find_one({"email": user_dict["email"]})
        if existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")

        user_dict["hashed_pssword"] = password_hash(user.password)
        del user_dict['password']

        result = await db.users.insert_one(user_dict)
        if not result.inserted_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User regiestration fail")
        return {"message":"User regiestered successfully"}
    
    except Exception as e:
        raise HTTPException (status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error:{str(e)}")