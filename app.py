from fastapi import FastAPI, HTTPException 
from models.schema import AgentRequest
from agents.executor import execute_plan
from agents.planner import create_plan
# from tools.doc_builder import build_docx
import uvicorn  

app = FastAPI(
    title="Autonomous AI Agent",
    description="AI agent for autonomous planning, task execution and document generation.",
    version="1.0.0"
)

# Health check endpoint
@app.get("/")
def home():

    return {
        "status": "running",
        "message": "Autonomous AI Agent API is operational"
    }


# Main agent endpoint
@app.post("/agent")
def run_agent(payload: AgentRequest):

    user_request = payload.request 
    plan = create_plan(user_request) 
    sections = execute_plan(plan) 
    for sec in sections:
        print(sec)
    # path = build_docx(plan ,sections) 

    return {
        "status": "received",
        "user_request": user_request,
        "message": "Request received successfully."
    }

if __name__ == "__main__":

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )