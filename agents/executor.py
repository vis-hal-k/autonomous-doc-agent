from llm_int import llm 
from models.schema import Plan , SectionContent 
import threading       # to see which worker thread runs each task
import time
from concurrent.futures import ThreadPoolExecutor, as_completed  # thread pool + "finished" iterator


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


def run_one_body(plan, task):
    """Worker function : write ONE task with retries. Return (task_id, content or None).""" 
    worker = threading.current_thread().name #  e.g. "ThreadPoolExecutor-0_2
    start = time.time() 
    print(f"[START ] task {task.id} '{task.title}' on {worker}") 
    for attempt in range(2):                  # try up to MAX_ATTEMPTS times
        try:
            content = execute_task(plan, task)           # call the LLM
            took = time.time() - start                   # seconds this task needed
            print(f"[DONE  ] task {task.id} on {worker} in {took:.1f}s")
            return task.id, content                      # success: hand result back to main thread
        except Exception as e:
            print(f"[RETRY ] task {task.id} attempt {attempt + 1} failed: {e}")
    
    return task.id, None    # None = failed (main thread marks status)


def execute_plan(plan:Plan, results : dict[int , SectionContent] | None = None) -> list[SectionContent] :
    print(f"Invoking the Execution Plan Agent (parallel)")
    results = results if results is not None else {} 

    pending = [task for task in plan.tasks if task.status == "pending"] 
    print(f"Pending tasks: {[t.id for t in pending]} | workers: {5}")
    

    if not pending:                                      # nothing to do, avoid creating a pool
        return results
    task_by_id = {t.id: t for t in plan.tasks}
    batch_start = time.time() 

    with ThreadPoolExecutor(max_workers = 5) as pool : 
        # submit start the work and immediately returns a Future (a promise of the result) 
        futures = [pool.submit(run_one_body,plan,t) for t in pending] 
        print(f"Submitted {len(futures)} tasks to the pool")

        # as_completed() yields each future the moment it finishes (NOT in submit order)
        for finished , f in enumerate(as_completed(futures) , start = 1 ):
            task_id , content = f.result()   # get (task_id, content) from the worker 
            task = task_by_id[task_id]    # find the matching task object 

            if content is None:
                task.status = "failed"
            else:
                results[task_id] = content               # keyed by id, so order doesn't matter
                task.status = "done"

            print(f"[MAIN  ] {finished}/{len(futures)} finished -> task {task_id} = {task.status}")
    total = time.time() - batch_start
    print(f"All tasks finished in {total:.1f}s")
    print(f"Finish order was random; results keys: {list(results.keys())}")

    # Assembly check: build the list in PLAN order, not finish order
    ordered_ids = [t.id for t in plan.tasks if t.id in results]
    print(f"Assembly order (plan order): {ordered_ids}")

    return results                            # doc builder should loop plan.tasks and use results[t.id]            




