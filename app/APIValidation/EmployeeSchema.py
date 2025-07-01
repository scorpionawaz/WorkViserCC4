from typing import List, Dict, Optional
from pydantic import BaseModel, EmailStr
from uuid import UUID

class EmployeeBase(BaseModel):
    id: str
    name: str
    work_email: EmailStr
    score: int
    mental_status: Optional[str] = None

class ActiveEmployee(EmployeeBase):
    task_status: bool = True
    available_time: int  # in minutes

class InactiveEmployee(EmployeeBase):
    task_status: bool = False
    available_time: int = 0

class ExpertiseResponse(BaseModel):
    domain: str
    employees: List[Dict[str, ActiveEmployee | InactiveEmployee]]

class ExpertiseRequest(BaseModel):
    expertise_list: List[str]