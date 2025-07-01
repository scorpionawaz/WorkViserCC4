from pydantic import BaseModel, constr
from datetime import datetime
from typing import List, Optional
from uuid import uuid4
from enum import Enum

class EmployeeStatus(str, Enum):
    NeedAssitance = "Need Assitance"
    WaitingForResponse = "Waiting For Response"
    Trying = "Trying"
    givenup = "giveup"

class TaskConversationEntry(BaseModel):
    timestamp: datetime
    message: str
    mental_status: str

class Conversation(BaseModel):
    #conversation entities
    id: uuid4 = uuid4()
    employee_id: str
    manager_id:str
    task_id: str
    
    #employee message
    employee_message: str

    #manager message
    manager_message: Optional[str]=None
    workviser_message: Optional[str]="What is Task Status?"

    #include current message and look for history , only include employee conversation 
    task_Conversation_history: Optional[List[TaskConversationEntry]] = None

    #current status predicted by our Model 
    status:EmployeeStatus

    #task status
    task_status: Optional[bool]=False

    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            uuid4: lambda v: str(v)
        }
    

#as task end , conversation is ended and based on conversation , expertise is computed 

