import uuid 
from pathlib import Path 
from docx import Document 
from models.schema import Plan, SectionContent 
from datetime import datetime 
from slugify import slugify 

OUTPUT_DIR = Path("output") 
OUTPUT_DIR.mkdir(exist_ok=True) 

def build_docx(plan : Plan , results : dict[int, SectionContent] ) -> str :
    doc = Document() 
    doc.add_heading(plan.title , level = 0) 
    doc.add_paragraph(plan.document_type) 

    if plan.assumptions:
        doc.add_heading("Assumptions" , level = 1) 
        for a in plan.assumptions:
            doc.add_paragraph(a, style="List Bullet")  

    for task in plan.tasks :
        s = results.get(task.id) 
        if s is None:                       # failed task, nothing to write
            continue
        doc.add_heading(s.heading, level = 1) 
        for p in s.paragraphs:
            doc.add_paragraph(p) 
        for b in s.bullets:
            doc.add_paragraph(b, style="List Bullet") 

    filename = f"{datetime.now():%Y%m%d_%H%M%S}_{slugify(plan.title)}.docx"
    # 20261122_143210_rag-for-customer-support.docx
    path = OUTPUT_DIR / filename
    doc.save(path)
    return str(path)
