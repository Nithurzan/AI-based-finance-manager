from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import PyMongoError
from dotenv import load_dotenv
import logging
import os

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize database client
try:
    mongo_uri = os.getenv("MONGO_URI")
    if not mongo_uri:
        raise ValueError("MONGO_URI is not set in the .env file.")
    
    client = AsyncIOMotorClient(mongo_uri)
    logger.info("MongoDB client created successfully.")
    
    # Database initialization
    db = client["finance_manager"]
    logger.info("Connected to 'finance_manager' database.")
    
except PyMongoError as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    db = None
except Exception as e:
    logger.error(f"An error occurred: {str(e)}")
    db = None

def get_db():
    return db
