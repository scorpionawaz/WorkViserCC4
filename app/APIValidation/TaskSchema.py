from datetime import date, time, datetime,timedelta
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, Field, validator, HttpUrl
import logging
logger = logging.getLogger(__name__)


class PriorityLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    URGENT = "urgent"


class TaskBase(BaseModel):
    """Base model for task data"""
    name: str = Field(
        ...,
        min_length=3,
        max_length=100,
        example="Implement user authentication",
        description="Name of the task",
        pattern=r'^[a-zA-Z0-9\s\-_]+$' 
    )
    description: str = Field(
        ...,
        min_length=10,
        max_length=1000,
        example="Create login and registration endpoints with JWT",
        description="Detailed description of the task"
    )

#this is the API Validation for TaskCreate
class TaskCreate(TaskBase):
    """Schema for creating new tasks with enhanced validation"""
    dateofassignment: date = Field(
        ...,
        example="2023-12-01",
        description="Date when task was assigned (future or current date)"
    ) 
    duration: time = Field(
        ...,
        example="02:30:00",
        description="Estimated time to complete the task (HH:MM:SS)"
    )
    image_url: Optional[HttpUrl] = Field(
        None,
        example="https://example.com/task-image.jpg",
        description="URL to task-related image (must be valid HTTPS URL)"
    )
    document_url: Optional[HttpUrl] = Field(
        None,
        example="https://example.com/task-doc.pdf",
        description="URL to task-related document (must be valid HTTPS URL)"
    )
    priority: PriorityLevel = Field(
        ...,
        example=PriorityLevel.MEDIUM,
        description="Priority level of the task"
    )
    requirements: Optional[List[str]] = Field(
        None,
        min_items=0,
        max_items=20,
        example=["Python 3.8+", "FastAPI", "PostgreSQL"],
        description="List of requirements needed (max 20 items)"
    )
    project_id: str = Field(
        ...,
        min_length=1,
        max_length=50,
        example="proj_12345",
        description="ID of the project this task belongs to",
        pattern=r'^[a-zA-Z0-9_]+$'
    )


    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            date: lambda v: v.isoformat(),
            time: lambda v: v.isoformat()
        }
        schema_extra = {
            "example": {
                "name": "API Documentation",
                "description": "Write comprehensive documentation for all endpoints",
                "dateofassignment": "2023-12-01",
                "duration": "04:00:00",
                "priority": "medium",
                "project_id": "proj_98765",
                "requirements": ["Markdown", "Swagger UI", "Examples"]
            }
        }


class TaskAssignResponse(BaseModel):
    """Response model for task assignment"""
    message: str
    task_id: str


from pydantic import BaseModel

class TaskNotificationResponse(BaseModel):
    Task: 'TaskNotification'

class TaskNotification(BaseModel):
    name: str
    description: str
    duration: int 
    manager_name: str
    priority: str