import os
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.services.resume_parser import extract_text_from_pdf
from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.resume import ResumeResponse
from app.services.resume_service import (
    create_resume,
    get_user_resumes,
    get_resume_by_id,
    delete_resume as delete_resume_service,
)


router = APIRouter(
    prefix="/resume",
    tags=["Resume"],
)


UPLOAD_DIR = Path("uploads/resumes")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload")
def upload_resume(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed",
        )

    file_path = UPLOAD_DIR / file.filename

    with open(file_path, "wb") as buffer:
        buffer.write(file.file.read())

    extracted_text = extract_text_from_pdf(str(file_path))

    resume = create_resume(
        db=db,
        user_id=current_user.id,
        file_name=file.filename,
        file_path=str(file_path),
        extracted_text=extracted_text,
    )

    return {
        "message": "Resume uploaded successfully",
        "resume_id": str(resume.id),
        "file_name": resume.file_name,
    }

@router.get(
    "/",
    response_model=list[ResumeResponse],
)
def get_my_resumes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return get_user_resumes(
        db=db,
        user_id=current_user.id,
    )

@router.delete("/{resume_id}")
def delete_resume(
    resume_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    resume = get_resume_by_id(
        db=db,
        resume_id=resume_id,
        user_id=current_user.id,
    )

    if resume is None:
        raise HTTPException(
            status_code=404,
            detail="Resume not found",
        )

    if os.path.exists(resume.file_path):
        os.remove(resume.file_path)

    delete_resume_service(
        db=db,
        resume=resume,
    )
    
    return {
        "message": "Resume deleted successfully"
    }