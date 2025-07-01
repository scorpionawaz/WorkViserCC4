from pydantic import BaseModel, EmailStr, constr,SecretStr
from datetime import datetime
from typing import List, Optional,Annotated,Dict
from uuid import uuid4
from enum import Enum

# FCMToken = Annotated[str, constr(min_length=100, max_length=300)]

class Employee(BaseModel):
    #identity card id 
    id: str
    
    #managerial status , when employee gets promoted as manager , same details get copied to manager table
    is_manager: Optional[bool]=False
    
    #personal information
    name: str
    personal_email: Optional[EmailStr]
    age: int
    contact_number: str  #phone number
    created_at: datetime
    
    #based on our Model Prediction and work history 
    expertise: Optional[Dict[str, int]]   #add score based on skills


    #based on recuritment
    education: List[str]
    work_experience: Optional[List[str]] = None  

    #user device finding
    # fcm_token: FCMToken

    #AuthenticationDetails
    password: SecretStr

    #task 
    current_taskid:Optional[uuid4]=None
    task_status: Optional[bool]=False   #task is completed or not
    
    #available time
    availablity_status: Optional[str]= "Available"
    #   data form --> "2"  in minutes

    #mental status
    mental_status: Optional[str]=None

    #task mail 
    work_email: EmailStr

    #professional profile
    department: str
    position: str
    salary: float
    joining_date: datetime

    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
            uuid4: lambda v: str(v)
        }




        