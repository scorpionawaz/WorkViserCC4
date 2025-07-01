#information: this file contains our controller for manager
from app.models.Manager import Manager
from app.APIValidation.TaskSchema import TaskCreate,TaskAssignResponse
from app.models.Employee import Employee
from app.database import employee_collection
from app.database import task_collection
from app.database import manager_collection
from fastapi import HTTPException,status
from app.database import project_collection
# from app.services.firebase_fcm import send_fcm_notification_wrapper
from app.APIValidation.EmployeeSchema import ActiveEmployee, InactiveEmployee
from datetime import datetime
from typing import List
from uuid import uuid4
from passlib.context import CryptContext
import logging
logger = logging.getLogger(__name__)


#this controller is used to assign task to employee and sends FCM Notification to respective employee
async def assigntask(task: TaskCreate, manager_id: str, employee_id: str) -> TaskAssignResponse:
    try:
        logger.info(f"Looking for manager with id: {manager_id}")

        manager = await manager_collection.find_one({"id": manager_id})
        if not manager:
            raise HTTPException(status_code=404, detail="Manager not found")

        employee = await employee_collection.find_one({"id": employee_id})
        if not employee:
            raise HTTPException(status_code=404, detail="Employee not found or not under your management")

        if not employee.get("fcm_token"):
            raise HTTPException(
                status_code=400,
                detail=f"Employee {employee_id} has no FCM token registered"
            )

        task_data = task.model_dump()

        task_document = {
            **task_data,
            "id": str(uuid4()),
            "manager_id": manager_id,
            "employee_id": employee_id,
            "status": False,
            "Accepted_status": False,
             "created_at": datetime.now()
        }

       
        task_document['dateofassignment'] = task_document['dateofassignment'].isoformat()
        task_document['duration'] = task_document['duration'].isoformat()
        task_document['priority'] = task_document['priority'].value
        

        result = await task_collection.insert_one(task_document)
        if not result.inserted_id:
            raise HTTPException(status_code=500, detail="Failed to create task")

        task_id = str(result.inserted_id)

        # notification_sent =  send_fcm_notification_wrapper(
        #     token=employee["fcm_token"],
        #     task_id=task_id,
        #     task_name=task_data["name"],
        #     manager_name=manager.get("name", "Your manager"),
        # )

        # if not notification_sent:
        #     logger.error(f"Failed to send notification for task {task_id}")

        return TaskAssignResponse(
            message="Task assigned successfully",
            task_id=task_id
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error assigning task: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Internal Server Error")

async def find_optimal_employees_by_expertise(expertise_list: List[str]):
    try:
        if not expertise_list:
            return {}

        # Query database
        query = {"$or": [{f"expertise.{domain}": {"$exists": True}} for domain in expertise_list]}
        employees = await employee_collection.find(query).to_list(length=None)

        results = {}
        THRESHOLD = 80

        for domain in expertise_list:
            domain_employees = []
            
            for emp in employees:
                if domain in emp.get("expertise", {}):
                    score = emp["expertise"][domain]
                    is_active = emp.get("task_status", False)
                    avail_status = str(emp.get("availablity_status", "0")).strip()
                    
                    # Parse availability (NEW IMPROVED PARSING)
                    if is_active:
                        if avail_status.lower() == "available":
                            available_time = 0  # Immediately available
                        else:
                            # Handle numeric strings like "120"
                            available_time = int(float(avail_status)) if avail_status.replace('.','',1).isdigit() else 0
                    else:
                        available_time = 0  # Inactive employees always 0

                    # Create employee object
                    employee_data = {
                        "id": str(emp["_id"]),
                        "name": emp["name"],
                        "work_email": emp["work_email"],
                        "score": score,
                        "mental_status": emp.get("mental_status"),
                        "task_status": is_active,
                        "available_time": available_time
                    }

                    # Assign priority groups (CLEAR LOGIC)
                    if score >= THRESHOLD:
                        priority = 1 if not is_active else 2  # Inactive high first
                    else:
                        priority = 3 if not is_active else 4  # Inactive low before active low

                    domain_employees.append({
                        "priority": priority,
                        "sort_score": -score,  # Higher scores first
                        "sort_avail": available_time,
                        "data": ActiveEmployee(**employee_data) if is_active else InactiveEmployee(**employee_data)
                    })

            # FINAL SORT (GUARANTEED CORRECT)
            domain_employees.sort(key=lambda x: (
                x["priority"],  # Priority group first
                x["sort_score"],  # Higher scores next
                x["sort_avail"]  # Lower availability times first
            ))
            
            results[domain] = [emp["data"] for emp in domain_employees]
        
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

def get_tasks(manager_id: str):
    try:
        manager =  manager_collection.find_one({"id": manager_id})
        if manager is None:
            raise HTTPException(status_code=404, detail="Manager not found")

        tasks = task_collection.find({"manager_id": manager_id})

        return {"message": "Tasks retrieved successfully", "tasks": [task.model_dump() for task in tasks]}  
    
    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    

def signup_manager(manager: Manager):
    try:
        manager_data = manager.model_dump()
        manager_data["created_at"] = datetime.now()
        result = manager_collection.insert_one(manager_data)
        if result.inserted_id:
            return {"message": "Manager registered successfully", "manager_id": str(result.inserted_id)}
        else:
            raise HTTPException(status_code=500, detail="Internal Server Error")

    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    


def enroll_employee(employee:Employee):
    try:
        employee_data = employee.model_dump()
        employee_data["created_at"] = datetime.now()
        result = employee_collection.insert_one(employee_data)
        if result.inserted_id:
            return {"message": "Employee enrolled successfully", "employee_id": str(result.inserted_id)}
        else:
            raise HTTPException(status_code=500, detail="Internal Server Error")

    except HTTPException as http_exc:
        raise http_exc
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")



pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    return pwd_context.hash(password)


async def create_employee(employee: Employee):
    existing = await employee_collection.find_one({
        "$or": [{"work_email": employee.work_email}, {"id": employee.id}]
    })
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Employee with this ID or work email already exists."
        )

    # Hash the password before storing
    employee_dict = employee.model_dump()
    employee_dict["password"] = hash_password(employee.password.get_secret_value())

    # Set created_at and id if not already set
    employee_dict["created_at"] = datetime.utcnow()
    employee_dict["id"] = employee_dict.get("id", str(uuid4()))

    await employee_collection.insert_one(employee_dict)
    return {"message": "Employee registered successfully", "employee_id": employee_dict["id"]}


async def showallmanagertask(manager_id:str):
    tasks_cursor = task_collection.find({"manager_id": manager_id})
    tasks = await tasks_cursor.to_list(length=100)

    if not tasks:
        raise HTTPException(status_code=404, detail="No tasks found for this manager.")

    enriched_tasks = []
    for task in tasks:
        # Fetch employee name
        employee = await employee_collection.find_one({"id": task["employee_id"]})
        employee_name = employee["name"] if employee else "Unknown"

        # Fetch project name
        project = await project_collection.find_one({"id": task["project_id"]})
        project_name = project["name"] if project else "Unknown"

        # Optionally fetch manager name (can be same for all)
        manager = await manager_collection.find_one({"id": manager_id})
        manager_name = manager["name"] if manager else "Unknown"

        # Enrich task data
        enriched_task = {
            "task_id": task["id"],
            "task_name": task["name"],
            "description": task["description"],
            "priority": task["priority"],
            "status": task["status"],
            "accepted": task.get("Accepted_status", False),
            "reject_reason": task.get("reject_reason"),
            "employee_name": employee_name,
            "manager_name": manager_name,
            "project_name": project_name,
            "created_at": task["created_at"]
        }

        enriched_tasks.append(enriched_task)

    return enriched_tasks


async def get_task_details(taskid: str):
    # Fetch the task
    task = await task_collection.find_one({"id": taskid})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found.")

    # Get employee name
    employee = await employee_collection.find_one({"id": task["employee_id"]})
    employee_name = employee["name"] if employee else "Unknown"

    # Get manager name
    manager = await manager_collection.find_one({"id": task["manager_id"]})
    manager_name = manager["name"] if manager else "Unknown"

    # Get project name
    project = await project_collection.find_one({"id": task["project_id"]})
    project_name = project["name"] if project else "Unknown"

    # Combine data
    task_details = {
        "task_id": task["id"],
        "task_name": task["name"],
        "description": task["description"],
        "priority": task["priority"],
        "status": task["status"],
        "accepted": task.get("Accepted_status", False),
        "reject_reason": task.get("reject_reason"),
        "duration": str(task["duration"]),
        "date_of_assignment": task["dateofassignment"],
        "employee_id": task["employee_id"],
        "employee_name": employee_name,
        "manager_id": task["manager_id"],
        "manager_name": manager_name,
        "project_id": task["project_id"],
        "project_name": project_name,
        "created_at": task["created_at"],
        "requirements": task.get("requirements", []),
        "image_url": task.get("image_url"),
        "document_url": task.get("document_url")
    }

    return task_details