from sqlalchemy.orm import Session

from app.models.resume import Resume
from app.models.job_match import JobMatch

from app.services.job_description_analyzer import (
    analyze_job_description,
)

from app.services.job_matcher import (
    match_resume_to_job,
)


def run_job_matching_pipeline(
    db: Session,
    user_id,
    resume_id: str,
    job_description: str,
):
    """
    Run the complete resume-to-job matching pipeline.

    Steps:
    1. Validate resume ownership
    2. Analyze job description
    3. Match resume against job
    4. Store result
    5. Return response
    """

    # --------------------------------------------------
    # Step 1: Get user's resume
    # --------------------------------------------------

    resume = (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == user_id,
        )
        .first()
    )

    if resume is None:
        raise ValueError("Resume not found")

    if not resume.analysis:
        raise ValueError(
            "Resume analysis is not available"
        )

    # --------------------------------------------------
    # Step 2: Analyze job description
    # --------------------------------------------------

    job_analysis = analyze_job_description(
        job_description
    )

    # --------------------------------------------------
    # Step 3: Convert stored resume analysis
    # back into ResumeAnalysis schema
    # --------------------------------------------------

    from app.schemas.resume_analysis import ResumeAnalysis

    resume_analysis = ResumeAnalysis.model_validate(
        resume.analysis
    )

    # --------------------------------------------------
    # Step 4: Match resume against job
    # --------------------------------------------------

    match_score, match_analysis = (
        match_resume_to_job(
            resume=resume_analysis,
            job=job_analysis,
        )
    )

    # --------------------------------------------------
    # Step 5: Store job match
    # --------------------------------------------------

    job_match = JobMatch(
        user_id=user_id,
        resume_id=resume.id,
        job_title=job_analysis.job_title,
        company=job_analysis.company,
        job_description=job_description,
        match_score=match_score,
        analysis=match_analysis.model_dump(),
    )

    db.add(job_match)
    db.commit()
    db.refresh(job_match)

    # --------------------------------------------------
    # Step 6: Return API response
    # --------------------------------------------------

    return {
        "id": str(job_match.id),
        "resume_id": str(resume.id),
        "job_title": job_analysis.job_title,
        "company": job_analysis.company,
        "match_score": match_score,
        "analysis": match_analysis,
    }