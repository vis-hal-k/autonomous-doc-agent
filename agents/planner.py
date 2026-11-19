from llm_int import llm 
from models.schema import Plan 

planner_llm = llm.with_structured_output(Plan) 



def create_plan(user_request: str) -> Plan:
    print(f"Invoking the Planner Agent")
    prompt = f""" 
                You are a planning agent that creates business documents
                (proposal, meeting minutes, project plan, report, SOP, technical design...).
                Your task is to analyze the user's request and create an execution plan. 
                
                # Given the request below:
                    1. Choose the document type and a title. 
                    2. If the request is ambiguous, missing info, or has conflicting requirements, do NOT ask
                    questions. Make reasonable assumptions and list them in 'assumptions'
                    (say how you resolve any conflict).
                    3. Must Create between 5 and 8 tasks, never more. 
                    Each task is ONE section of the document, with clear instructions.
                    Start with an executive summary and end with next steps. 
                Request: {user_request} 
                    """ 
    return planner_llm.invoke(prompt) 


