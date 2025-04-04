from fastapi import Depends, HTTPException,status,APIRouter
from .schema import User,UserInDB,Login
from .auth import password_hash,verify_password,create_access_token
from database import get_db
from fastapi.security import OAuth2PasswordBearer
from jose import jwt,JWTError
from config import SECRET_KEY,ALGORITHM



router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

@router.post("/register")
async def register_user(user:User):
    try:
        db =  get_db()
        user_dict = user.dict()

        # existing_user 
        existing_user = await db.users.find_one({'email':user_dict['email']})
        if  existing_user:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="User already exist!")
        
        user_dict["hashed_password"] = password_hash(user.password)
        

        result = await db.users.insert_one(user_dict)
        if not result.inserted_id:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="User regiestration fail")
        return {"message":"User regiestered successfully"}
    
    except Exception as e:
        raise HTTPException (status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error:{str(e)}")
    

@router.post("/login")
async def login (user:Login):
    try:
        db =  get_db()
        user_in_db = await db.users.find_one({'email':user.email})
        if not user_in_db:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credential")
        
        if not verify_password(user.password,user_in_db["hashed_password"]):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Invalid credential")
        
        token = create_access_token(data={"sub":user_in_db["email"]})
        return token
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Error:{str(e)}")
    

@router.get("/profile")
async def get_user_profile(token:str=Depends(oauth2_scheme)):
    try:
        db = get_db()
        play_load = jwt.decode(token,SECRET_KEY,algorithms=ALGORITHM)
        email = play_load.get("sub")

        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,detail="Could not valid credential")
        
        user = await db.users.find_one({"email":email})
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
        return user

    except JWTError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED , detail="Invalid token")
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail=f"Error:{str(e)}")