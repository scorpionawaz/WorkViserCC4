from fastapi import APIRouter,Body,Query,status
from app.APIValidation.TaskSchema import TaskCreate,TaskAssignResponse
from typing import List, Dict
from app.APIValidation.EmployeeSchema import ActiveEmployee, InactiveEmployee, ExpertiseRequest
from app.controller.manager_controller import assigntask
from app.controller.manager_controller import find_optimal_employees_by_expertise

from app.controller.manager_controller import showallmanagertask
from app.controller.manager_controller import get_task_details
from app.models.Employee import Employee
from app.controller.manager_controller import create_employee

# from app.controller.manager_controller import signup_manager
# from app.controller.manager_controller import enroll_employee
router = APIRouter()

# @router.post("/login",)

# @router.post("/register",)
# def register_manager(manager: Manager):
#    return signup_manager(manager)

# @router.post("/enroll_employee")
# def enroll_employee(employee: Employee):
#    return enroll_employee(employee)

# In your route:
@router.post("/assign_task", status_code=201, response_model=TaskAssignResponse)
async def assign_task(
    task_data: TaskCreate=Body(...),
    manager_id: str=Query(...) ,
    employee_id: str=Query(...) 
):
    return await assigntask(task_data, manager_id, employee_id)

@router.post("/optimalexpertise", response_model=Dict[str, List[ActiveEmployee | InactiveEmployee]],
    summary="Get employees sorted by optimal expertise",
    description="Returns employees grouped by expertise domains with hybrid sorting: "
              "1. Inactive high-scorers (≥80) first, "
              "2. Active high-scorers (≥80) by availability, "
              "3. Inactive low-scorers (<80), "
              "4. Active low-scorers (<80) by availability"
)
async def get_optimal_employees(request: ExpertiseRequest):
    return await find_optimal_employees_by_expertise(request.expertise_list)

@router.post("/register", status_code=status.HTTP_201_CREATED)
async def createemployee(
    employee:Employee=Body(...)
):return await create_employee(employee) 


@router.get("/get_tasks")
async def get_tasks(manager_id: str=Query(...)):
   return await showallmanagertask(manager_id)

@router.get("/view_task")
async def viewtaskdetails(taskid : str=Query(...)):
    return get_task_details(taskid)

# @router.put("/update_task/{task_id}")

# @router.delete("/delete_task/{task_id}")

# @router.get("/free_employee")

# @router.get("/task_status/{task_id}")

# @router.get("/get_project_status")
