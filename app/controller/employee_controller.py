from datetime import datetime, timedelta
import re
from uuid import uuid4
from fastapi import HTTPException
from app.models.Task import Task
from app.APIValidation.accept_reject_status import accceptrequest,acceptresponse
from app.APIValidation.TaskSchema import TaskNotification
from app.models.Conversation import EmployeeStatus
from app.database import task_collection, manager_collection,employee_collection,conversation_collection

async def get_task_notification(employee_id: str):
    task = await task_collection.find_one(
        {
            "employee_id": employee_id,
            "Accepted_status": False,
            "created_at": {"$gte": datetime.now() - timedelta(hours=1080)}
        },
        sort=[("created_at", -1)]
    )
    if not task:
        raise HTTPException(404, "No new task notifications")

    manager = await manager_collection.find_one({"id": task["manager_id"]})
    if not manager:
        raise HTTPException(404, "Manager not found")

    duration_minutes = convert_duration_to_minutes(task.get("duration", "00:00:00"))

    task_notification = TaskNotification(
        name=task["name"],
        description=task["description"],
        duration=duration_minutes, 
        manager_name=manager.get("name", "Unknown Manager"),
        priority=task["priority"]
    )
    
    return {"Task": task_notification}


def convert_duration_to_minutes(duration_input) -> int:

    if isinstance(duration_input, timedelta):
        return int(duration_input.total_seconds() // 60)
    
    if not isinstance(duration_input, str):
        return 0 
    
    if duration_input.startswith("PT"):
        hours = minutes = 0
        if "H" in duration_input:
            hours = int(duration_input.split("H")[0].replace("PT", ""))
        if "M" in duration_input:
            minutes_part = duration_input.split("H")[-1] if "H" in duration_input else duration_input.replace("PT", "")
            minutes = int(minutes_part.split("M")[0])
        return hours * 60 + minutes
    
    if re.match(r"^\d{1,2}:\d{2}:\d{2}$", duration_input):
        hours, minutes, _ = map(int, duration_input.split(":"))
        return hours * 60 + minutes
    
    return 0 

async def accept_reject_taskcontroller(data: accceptrequest, taskid: str):
    task = await task_collection.find_one({"id": taskid})
    if not task:
        return {"error": "Task not found"}

    if data.acceptstatus:
        await task_collection.update_one({"id": taskid}, {"$set": {"Accepted_status": True}})
        task = await task_collection.find_one({"id": taskid})

        employee = await employee_collection.find_one({"id": data.employeeid})
        if not employee:
            return {"error": "Employee not found"}
        minutes=convert_duration_to_minutes(task["duration"])
        employee["availablity_status"]=str(minutes)

        conversation = await conversation_collection.find_one({"task_id": taskid})
        if conversation:
            await conversation_collection.delete_one({"task_id": taskid})

        await create_empty_conversation(task,data.employeeid,taskid)

        response = acceptresponse(cs_value=10)
        return response

    else:
        await task_collection.update_one({"id": taskid}, {"$set": {"reject_reason": data.reason}})
        response = acceptresponse(cs_value=0)
        return response
    


async def create_empty_conversation(task, employee_id: str, task_id: str):
    await conversation_collection.insert_one({
        "id": str(uuid4()),
        "employee_id": employee_id,
        "task_id": task_id,
        "manager_id": task.get("manager_id"),
        "employee_message": "",
        "manager_message": None,
        "workviser_message": "What is Task Status?",
        "task_Conversation_history": [],
        "status": EmployeeStatus.Trying.value,
        "task_status": False
    })


async def complete_task(task_id: str, completion_status: bool = True, notes: str = None):
    """
    Marks a task as complete and updates all related entities
    Args:
        task_id: ID of the task to complete
        completion_status: True if successful, False if failed
        notes: Optional completion notes or failure reasons
    Returns:
        Updated task object
    """
    # 1. Verify task exists and isn't already completed
    task = await task_collection.find_one({"id": task_id})
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if task.get("status"):
        raise HTTPException(status_code=400, detail="Task already completed")

    # 2. Update task status and completion time
    updates = {
        "status": completion_status,
        "completed_at": datetime.now(),
        "notes": notes
    }
    
    if not completion_status:
        updates["reject_reason"] = notes  # Track failure reason

    await task_collection.update_one(
        {"id": task_id},
        {"$set": updates}
    )

    # 3. Update employee's current task and availability
    employee_id = task["employee_id"]
    await employee_collection.update_one(
        {"id": employee_id},
        {
            "$set": {
                "current_taskid": None,
                "task_status": False,  # Reset for new tasks
                "availablity_status": "Available",
                "mental_status": "Idle" if completion_status else "NeedsSupport"
            }
        }
    )

    # 4. Close related conversation
    await conversation_collection.update_one(
        {"task_id": task_id},
        {
            "$set": {
                "task_status": completion_status,
                "status": "Completed" if completion_status else "Failed",
                "workviser_message": "Task completed successfully!" if completion_status 
                                   else "Task failed - needs review"
            }
        }
    )

    # 5. Return updated task
    updated_task = await task_collection.find_one({"id": task_id})
    return Task(**updated_task)




    




