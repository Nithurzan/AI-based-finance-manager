from passlib.context import CryptContext
from config import ACCESS_TOKEN_EXPIRE_MINUTES,ALGORITHM,SECRET_KEY
from datetime import datetime, timedelta
from jose import jwt,JWTError




pwd_context = CryptContext(schemes=["bcrypt"], deprecated='auto')

def password_hash(password):
    return pwd_context.hash(password)

def verify_password(plain_password,hashed_password):
    return pwd_context.verify(plain_password,hashed_password)

def create_access_token(data:dict,expires_delta:timedelta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)):
    to_encode = data.copy()
    expires = datetime.utcnow() + expires_delta
    to_encode.update({'exp':expires})
    encoded_jwt = jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt