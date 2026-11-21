# app.py
from fastapi import FastAPI, HTTPException 
from models.schema import AgentRequest
from agents.executor import execute_plan
from agents.planner import create_plan
from agents.reflection import review_plan
from tools.doc_builder import build_docx
import uvicorn  
import mammoth
from pathlib import Path 
from fastapi.responses import FileResponse, HTMLResponse

# anchor to the app's location so it works no matter where you start uvicorn
OUTPUT_DIR = (Path(__file__).parent / "output").resolve()
DOCX_MIME = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"

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
    print(f"Number of tasks is generated : {len(plan.tasks)}")
    results = execute_plan(plan) 
    review = review_plan(user_request , plan , results) 
    print(f"Review Status : {review.ok}") 
    added = []  
    if not review.ok and review.missing_tasks:
        next_id = max(t.id for t in plan.tasks) + 1 
        for i , task in enumerate(review.missing_tasks[:3]):
            print(f"Missing Task: {task.title}")
            # what the LLM asked for
            print(f"[INSERT] reviewer asked: insert_after_id = {task.insert_after_id}")

            task.id = next_id + i  # ids always assigned by code 
            task.status = "pending" 
            ids = [t.id for t in plan.tasks] # we get all the ids 
            pos = ids.index(task.insert_after_id) + 1 if task.insert_after_id in ids else len(ids) 
            plan.tasks.insert(pos, task) # it insert the the particular position.
            added.append(task.title) 
        execute_plan(plan, results)   # only pending tasks run, results is updated in place


    path = build_docx(plan ,results)  

    return {
        "path" : path ,
        "user_request": user_request,
        "message": "Request received successfully."
    }

# OUTPUT_DIR = Path("outputs").resolve() 


@app.get("/open-doc")
def open_latest_docx():
    docs = list(OUTPUT_DIR.glob("*.docx"))
    if not docs:
        raise HTTPException(status_code=404, detail="No documents found")
    latest = max(docs, key=lambda p: p.stat().st_mtime)
    with latest.open("rb") as f:
        html = mammoth.convert_to_html(f).value

    return HTMLResponse(f"<html><body style='max-width:800px;margin:auto'>{html}</body></html>")
    # return FileResponse(path=latest, media_type=DOCX_MIME, filename=latest.name)





if __name__ == "__main__":

    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )