from llm_int import llm
from models.schema import Plan, SectionContent, Review


reviewer_llm = llm.with_structured_output(Review)


def build_outline(plan: Plan, results: dict[int, SectionContent]) -> str:
    lines = []
    for t in plan.tasks:
        s = results.get(t.id)
        if s is None:
            continue
        # text = " ".join(s.paragraphs + s.bullets)[:100]     # short preview only
        lines.append(f"{t.id}: {s.heading}")
    return "\n".join(lines)


def review_plan(request : str , plan : Plan , results: dict[int, SectionContent]) -> Review: 
    print(f"Invoking the Review Plan Agent")

    outline = build_outline(plan , results)
    print(f"outline : {outline}")
    prompt = f"""
            Review this drafted document against the user's request.
            Request : {request} 
            Assumptions : {plan.assumptions} 
            Section written : (id: section) :
            {outline} 
            # Rules 
            - List every requirement explicitly named in the request. 
            - For each one, check whether a section above covers it. 
            - Add a missing task ONLY for a requirement that is named in the request and has no matching section .
            - Add at most {3} missing tasks. If there are more gaps, keep the {3} most important ones, ordered from most to least important. 
            # Not To Do
            Do NOT add sections for anything the request did not ask for, even if it would be nice to have. Do NOT add sections that duplicate existing ones.
            If all requirements are covered, return missing_tasks as an empty list.
            For each missing task, set insert_after_id to the id of the section it should follow.
            """
    review = reviewer_llm.invoke(prompt)

    review.missing_tasks = review.missing_tasks[:3]
    review.ok = len(review.missing_tasks) == 0  
    return review
