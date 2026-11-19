from llm_int import llm 
from models.schema import Plan , SectionContent 

writer_llm  = llm.with_structured_output(SectionContent) 

def execute_task(plan:Plan , task ) -> SectionContent:
   
    prompt = f"""
                You are writer one section of a professional business document.
                Document : {plan.title} ({plan.document_type}) 
                Assumption : {plan.assumptions} 
                Other Section (Don't repeat them) : {[t.title for t in plan.tasks if t.id != task.id]} 

                Wrtie the Section : {task.title} 
                Instruction : {task.instructions}

                Formatting rules:
                - Maximum 2 short paragraphs, each at most 3 sentences.
                - Put lists, steps, risks, owners, deadlines into 'bullets' (4-6 bullets, one line each).
                - Never write long dense paragraphs.
                - Be specific and concise. No placeholders like TBD.
            """
    #  In the Other section in the prompt : It takes the titles of every task in the plan except the one currently being written.
    return writer_llm.invoke(prompt) 

def execute_plan(plan:Plan, results : dict[int , SectionContent] | None = None) -> list[SectionContent] :
    print(f"Invoking the Execution Plan Agent")
    results = results if results is not None else {} 

    for task in plan.tasks:
        if task.status != "pending" : # skip done and failed 
            continue 
        print(f"Into the TASK : {task.id} with title : {task.title}")  
        for attempt in range(2):
            try:
                executed_task = execute_task(plan,task)
                results[task.id] = executed_task 
                task.status = "done" 
                break 
            except Exception as e:
                print(f"Task {task.id} attempt {attempt + 1} failed: {e}") 
        else :
            task.status = "failed" 

    return results


