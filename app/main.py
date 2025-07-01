import os
from fastapi import FastAPI
import uvicorn
from dotenv import load_dotenv
from app.routes.employee_routes import router as employee_router    
from app.routes.manager_routes import router as manager_router
from app.wwapicall.mental_state_analyzer import mental_status_analyzer

load_dotenv()

app = FastAPI()


app.include_router(employee_router, prefix="/employee", tags=["Employee"])
app.include_router(manager_router, prefix="/manager", tags=["Manager"])

@app.get("/health")
async def root():
    print("Server is running")
    return {"message": "server is running"}


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host=os.getenv("HOST", "127.0.0.1"), 
        port=int(os.getenv("PORT", 8000)),  
        reload=True, 
)
