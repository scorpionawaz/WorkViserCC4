from app.database import employee_collection,manager_collection,conversation_collection,task_collection,project_collection
from typing import Dict, List,Optional
from app.database import employee_collection
from app.models.Task import Task
from app.models.Employee import Employee
from collections import defaultdict
import heapq

async def find_alternative_employee(task: Task, current_employee_id: str) -> Optional[Employee]:
    """
    Finds the most suitable alternative employee for a task when the current employee fails.
    
    Args:
        task: The Task object containing requirements
        current_employee_id: ID of the employee who failed the task
    
    Returns:
        Employee object of the best alternative, or None if no suitable employee found
    """
    # 1. Get all employees except the current one
    all_employees = await employee_collection.find(
        {"id": {"$ne": current_employee_id}, "availablity_status": "Available"}
    ).to_list(None)
    
    if not all_employees:
        return None
    
    # 2. Score employees based on task requirements
    employee_scores = defaultdict(int)
    task_requirements = task.requirements or []
    
    for emp_data in all_employees:
        employee = Employee(**emp_data)
        
        # Skip if employee is manager (unless you want to include them)
        if employee.is_manager:
            continue
            
        # Calculate matching score
        if employee.expertise:
            for requirement in task_requirements:
                employee_scores[employee.id] += employee.expertise.get(requirement, 0)
    
    if not employee_scores:
        return None
    
    # 3. Find top 3 candidates
    top_3 = heapq.nlargest(3, employee_scores.items(), key=lambda x: x[1])
    
    # 4. Get full details of the best candidate
    best_employee_id = top_3[0][0]
    best_employee_data = await employee_collection.find_one({"id": best_employee_id})
    
    return Employee(**best_employee_data) if best_employee_data else None
