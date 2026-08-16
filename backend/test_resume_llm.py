import json

from app.services.resume_parser import extract_text_from_pdf
from app.services.llm.resume_llm import analyze_resume_with_llm


file_path = "uploads/resumes/siddesh_hiwale_resumePOD3.pdf.pdf"

text = extract_text_from_pdf(file_path)

analysis = analyze_resume_with_llm(text)

print("=" * 60)
print("LLM RESUME ANALYSIS")
print("=" * 60)

print(
    json.dumps(
        analysis.model_dump(),
        indent=4,
        ensure_ascii=False,
    )
)