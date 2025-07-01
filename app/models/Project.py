from pydantic import BaseModel, constr
from datetime import datetime
from typing import List, Optional
from uuid import uuid4

class Project(BaseModel):
#project
  id: uuid4 = uuid4()
  name: str
  description: str
  dateofassignement: datetime
  duration: str
  image_url : Optional[str]=None
  document_url: Optional[str]=None
  status:bool
  created_at: datetime

  #employee assigned
  employee_ids: list[str]
  manager_ids: list[str]

  #client infrormation
  client_name: str
  client_email: str