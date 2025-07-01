from pydantic import BaseModel, constr,SecretStr,EmailStr
from datetime import datetime
from typing import List, Optional,Dict

class Manager(BaseModel):
    #identity card id 
    id : str

    #personal information
    name: str
    personal_email: str
    contact_number: str
    age: int
    salary: float

    #professional information
    department: str
    position: Optional[str]="Manager"
    joining_date: datetime
    expertise: Optional[Dict[str, int]]  
    status: Optional[bool]=False
    work_email: EmailStr


    password: SecretStr
    #based on recruitment
    education: List[str]
    work_experience: Optional[List[str]] = None

    #optional incase if desktop application is developed for manager
    fcm_token: Optional[str] = None

    created_at: datetime


    class Config:
        from_attributes = True
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            datetime: lambda v: v.isoformat(),
        }
    
