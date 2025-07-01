#information: this file contains our configuration for mongoDB

import motor.motor_asyncio
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DATABASE_NAME = os.getenv("DATABASE_NAME")

# MongoDB client setup
client = motor.motor_asyncio.AsyncIOMotorClient(MONGO_URI)
database = client[DATABASE_NAME]

# Collections
employee_collection = database.Employee
task_collection = database.Task
conversation_collection = database.Conversation
manager_collection = database.Manager
project_collection = database.Project

