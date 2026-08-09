import json

from app.services.resume_parser import extract_text_from_pdf
from app.services.resume_analyzer import (
    analyze_resume_text,
    extract_project_candidates,
)


file_path = "uploads/resumes/siddesh_hiwale_resumePOD3.pdf.pdf"


# ============================================================
# EXTRACT TEXT
# ============================================================

text = extract_text_from_pdf(file_path)


print("=" * 60)
print("RAW EXTRACTED TEXT")
print("=" * 60)

print(repr(text[:3000]))


# ============================================================
# PROJECT CANDIDATES
# ============================================================

project_candidates = extract_project_candidates(text)


print("=" * 60)
print("PROJECT CANDIDATES")
print("=" * 60)


for item in project_candidates:
    print("-", item)


# ============================================================
# STRUCTURED RESUME
# ============================================================

analysis = analyze_resume_text(text)


print("=" * 60)
print("STRUCTURED RESUME DATA")
print("=" * 60)


print(
    json.dumps(
        analysis.model_dump(),
        indent=4,
        ensure_ascii=False,
    )
)