import json

from app.services.resume_parser import extract_text_from_pdf
from app.services.resume_pipeline import analyze_resume
from app.services.resume_scorer import calculate_resume_score


file_path = (
    "uploads/resumes/"
    "siddesh_hiwale_resumePOD3.pdf.pdf"
)


text = extract_text_from_pdf(file_path)

resume_analysis = analyze_resume(text)

score = calculate_resume_score(
    resume_analysis
)


print("=" * 60)
print("RESUME SCORE")
print("=" * 60)

print(
    json.dumps(
        score.model_dump(),
        indent=4,
        ensure_ascii=False,
    )
)