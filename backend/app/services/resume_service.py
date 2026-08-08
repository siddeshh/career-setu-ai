from sqlalchemy.orm import Session

from app.models.resume import Resume

def create_resume(
        db: Session,
        user_id,
        file_name: str,
        file_path: str
):
    resume = Resume(
        user_id=user_id,
        file_name=file_name,
        file_path=file_path
    )

    db.add(resume)
    db.commit()
    db.refresh(resume)

    return resume

def get_user_resumes(
        db: Session,
        user_id,
):
    return (
        db.query(Resume)
        .filter(Resume.user_id == user_id)
        .order_by(Resume.created_at.desc())
        .all()
    )

def get_resume_by_id(
    db: Session,
    resume_id,
    user_id,
):
    return (
        db.query(Resume)
        .filter(
            Resume.id == resume_id,
            Resume.user_id == user_id,
        )
        .first()
    )


def delete_resume(
    db: Session,
    resume: Resume,
):
    db.delete(resume)
    db.commit()