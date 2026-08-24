from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User

from app.schemas.job_matching import JobMatchResponse

from app.services.job_matching_pipeline import (
    run_job_matching_pipeline,
)


router = APIRouter(
    prefix="/job-matching",
    tags=["Job Matching"],
)


# ------------------------------------------------------
# Analyze Job Description
# ------------------------------------------------------

@router.post(
    "/analyze",
    response_model=JobMatchResponse,
)
def analyze_job_match(
    resume_id: str,
    job_description: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Match a user's resume against a job description.
    """

    try:
        result = run_job_matching_pipeline(
            db=db,
            user_id=current_user.id,
            resume_id=resume_id,
            job_description=job_description,
        )

        return result

    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    except Exception as e:
        print("=" * 60)
        print("JOB MATCHING ERROR")
        print("=" * 60)
        print(type(e).__name__)
        print(str(e))

        raise HTTPException(
            status_code=500,
            detail=f"Job matching failed: {str(e)}",
        )