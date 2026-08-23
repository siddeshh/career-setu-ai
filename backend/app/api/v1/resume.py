import os
from pathlib import Path

from app.services.resume_scorer import calculate_resume_score
from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.services.resume_parser import extract_text_from_pdf
from app.services.resume_pipeline import analyze_resume
from app.services.resume_improver import generate_resume_improvements

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
    # --------------------------------------------------
    # Step 0: Validate PDF
    # --------------------------------------------------
    if file.content_type != "application/pdf":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only PDF files are allowed",
        )

    file_path = UPLOAD_DIR / file.filename

    try:
        # --------------------------------------------------
        # Step 1: Save and extract PDF text
        # --------------------------------------------------
        with open(file_path, "wb") as buffer:
            buffer.write(file.file.read())

        extracted_text = extract_text_from_pdf(
            str(file_path)
        )

        if not extracted_text or not extracted_text.strip():
            raise HTTPException(
                status_code=400,
                detail="Could not extract text from the PDF",
            )

        # --------------------------------------------------
        # Step 2: Analyze extracted resume
        # --------------------------------------------------
        resume_analysis = analyze_resume(
            extracted_text
        )

        # --------------------------------------------------
        # Step 3: Calculate resume score
        # --------------------------------------------------
        resume_score = calculate_resume_score(
            resume_analysis
        )

        # --------------------------------------------------
        # Step 4: Generate resume improvements
        # --------------------------------------------------
        resume_improvements = generate_resume_improvements(
            resume_analysis,
            resume_score,
        )

        # --------------------------------------------------
        # Step 5: Store resume
        # --------------------------------------------------
        resume = create_resume(
            db=db,
            user_id=current_user.id,
            file_name=file.filename,
            file_path=str(file_path),
            extracted_text=extracted_text,
            analysis=resume_analysis.model_dump(),
        )

        # --------------------------------------------------
        # Step 6: Return complete result
        # --------------------------------------------------
        return {
            "message": "Resume uploaded successfully",
            "resume_id": str(resume.id),
            "file_name": resume.file_name,
            "analysis": resume_analysis.model_dump(),
            "score": resume_score.model_dump(),
            "improvements": resume_improvements.model_dump(),
        }

    except HTTPException:
        raise

    except Exception as e:
        print("=" * 60)
        print("RESUME UPLOAD ERROR")
        print("=" * 60)
        print(type(e).__name__)
        print(str(e))

        raise HTTPException(
            status_code=500,
            detail=f"Resume processing failed: {str(e)}",
        )

# ------------------------------------------------------
# Get all resumes
# ------------------------------------------------------

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


# ------------------------------------------------------
# Get resume analysis
# ------------------------------------------------------

@router.get("/{resume_id}/analysis")
def get_resume_analysis(
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

    if resume.analysis is None:
        raise HTTPException(
            status_code=404,
            detail="Resume analysis not available",
        )

    return {
        "resume_id": str(resume.id),
        "file_name": resume.file_name,
        "analysis": resume.analysis,
    }


# ------------------------------------------------------
# Delete resume
# ------------------------------------------------------

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