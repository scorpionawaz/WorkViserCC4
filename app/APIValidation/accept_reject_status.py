from typing import  Optional
from pydantic import BaseModel

class accceptrequest(BaseModel):
    acceptstatus: bool
    reason : Optional[str]
    employeeid: str

class acceptresponse(BaseModel):
    cs_value:Optional[int]
    text:Optional[str]="Your Task Timer is Started!"
