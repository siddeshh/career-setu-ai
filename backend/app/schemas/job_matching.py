from pydantic import BaseModel, Field


class JobDescriptionAnalysis(BaseModel):
    job_title: str | None = None
    company: str | None = None

    required_skills: list[str] = Field(default_factory=list)
    preferred_skills: list[str] = Field(default_factory=list)

    experience_requirements: list[str] = Field(
        default_factory=list
    )

    education_requirements: list[str] = Field(
        default_factory=list
    )

    responsibilities: list[str] = Field(
        default_factory=list
    )

    keywords: list[str] = Field(
        default_factory=list
    )


class SkillMatch(BaseModel):
    matched: list[str] = Field(
        default_factory=list
    )

    missing: list[str] = Field(
        default_factory=list
    )


class JobMatchAnalysis(BaseModel):
    skill_match: SkillMatch

    matched_keywords: list[str] = Field(
        default_factory=list
    )

    missing_keywords: list[str] = Field(
        default_factory=list
    )

    experience_match: bool | None = None

    education_match: bool | None = None

    strengths: list[str] = Field(
        default_factory=list
    )

    skill_gaps: list[str] = Field(
        default_factory=list
    )

    recommendations: list[str] = Field(
        default_factory=list
    )


class JobMatchResponse(BaseModel):
    id: str
    resume_id: str

    job_title: str | None = None
    company: str | None = None

    match_score: int

    analysis: JobMatchAnalysis