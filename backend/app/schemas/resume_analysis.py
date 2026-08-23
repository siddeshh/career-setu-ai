from pydantic import BaseModel, Field


class ProjectAnalysis(BaseModel):
    title: str
    start_date: str | None = None
    end_date: str | None = None
    team_size: int | None = None
    role: str | None = None
    description: str | None = None
    skills: list[str] = Field(default_factory=list)
    url: str | None = None


class ExperienceAnalysis(BaseModel):
    company: str | None = None
    role: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    skills: list[str] = Field(default_factory=list)


class ResumeAnalysis(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    summary: str | None = None

    skills: list[str] = Field(default_factory=list)
    education: list[str] = Field(default_factory=list)
    experience: list[ExperienceAnalysis] = Field(default_factory=list)
    projects: list[ProjectAnalysis] = Field(default_factory=list)
    certifications: list[str] = Field(default_factory=list)
    achievements: list[str] = Field(default_factory=list)
    languages: list[str] = Field(default_factory=list)


class ScoreBreakdown(BaseModel):
    contact_information: int = 0
    summary: int = 0
    skills: int = 0
    education: int = 0
    experience: int = 0
    projects: int = 0
    certifications: int = 0
    completeness: int = 0


class ResumeQuality(BaseModel):
    quality_score: int = 0
    ats_score: int = 0
    content_score: int = 0
    formatting_score: int = 0
    issues: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class ResumeScore(BaseModel):
    candidate_type: str = "unknown"
    overall_score: int = 0
    breakdown: ScoreBreakdown
    quality: ResumeQuality
    strengths: list[str] = Field(default_factory=list)
    weaknesses: list[str] = Field(default_factory=list)
    recommendations: list[str] = Field(default_factory=list)


class ResumeImprovement(BaseModel):
    section: str
    priority: str
    issue: str
    recommendation: str


class ResumeImprovementResponse(BaseModel):
    improvements: list[ResumeImprovement] = Field(default_factory=list)