from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
import logging
import os

load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


try:
    client = AsyncIOMotorClient(os.getenv("MONGO_URI"))
    db = client["finance_manager"]
except PyMongoError as e:
    logger.info(f"Failed to connect database")
    db = None

def get_db():
    return db