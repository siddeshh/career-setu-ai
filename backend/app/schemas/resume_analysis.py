from pydantic import BaseModel


class ProjectAnalysis(BaseModel):
    title: str
    start_date: str | None = None
    end_date: str | None = None
    team_size: int | None = None
    role: str | None = None
    description: str | None = None
    skills: list[str] = []
    url: str | None = None


class ExperienceAnalysis(BaseModel):
    company: str | None = None
    role: str | None = None
    start_date: str | None = None
    end_date: str | None = None
    description: str | None = None
    skills: list[str] = []


class ResumeAnalysis(BaseModel):
    full_name: str | None = None
    email: str | None = None
    phone: str | None = None
    summary: str | None = None

    skills: list[str] = []
    education: list[str] = []
    experience: list[ExperienceAnalysis] = []
    projects: list[ProjectAnalysis] = []
    certifications: list[str] = []
    achievements: list[str] = []
    languages: list[str] = []