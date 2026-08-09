from app.services.resume_parser import extract_text_from_pdf


file_path = "uploads/resumes/siddeshhiwale_resume.pdf.pdf"

text = extract_text_from_pdf(file_path)

print("=" * 60)
print("EXTRACTED RESUME TEXT")
print("=" * 60)

print(text)

print("=" * 60)
print("CHARACTER COUNT:", len(text))
print("=" * 60)