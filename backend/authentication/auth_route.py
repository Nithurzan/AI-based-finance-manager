from fastapi import HTTPException,status,APIRouter
from models import User,UserInDB


router = APIRouter()


@router.post("/regiester")
async def register_user(user:User):
    try:
        user_dict = user.dict()
        # existing_user = await db.user.find_one({})
        user_dict["hashed_pssword"] = password_hash(user.password)
        del user_dict['password']

        # result = await db.users.insert_one(user_dict)
        # if not result.inserted_id:
            # raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User regiestration fail")
        return {"message":"User regiestered successfully"}
    
    except Exception as e:
        raise HTTPException (status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error:{str(e)}")