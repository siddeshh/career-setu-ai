from app.schemas.resume_analysis import (
    ResumeAnalysis,
    ResumeScore,
    ResumeImprovement,
    ResumeImprovementResponse,
)


def generate_resume_improvements(
    resume: ResumeAnalysis,
    score: ResumeScore,
) -> ResumeImprovementResponse:

    improvements = []

    quality = score.quality

    if not resume.summary:
        improvements.append(
            ResumeImprovement(
                section="Summary",
                priority="high",
                issue="Professional summary is missing",
                recommendation=(
                    "Add a concise 2-3 line professional summary "
                    "targeted toward the desired role."
                ),
            )
        )

    if not resume.experience:
        improvements.append(
            ResumeImprovement(
                section="Experience",
                priority="medium",
                issue="No professional experience is listed",
                recommendation=(
                    "Add internships, freelance work, hackathons, "
                    "or relevant practical experience when available."
                ),
            )
        )

    if not resume.certifications:
        improvements.append(
            ResumeImprovement(
                section="Certifications",
                priority="low",
                issue="No certifications are listed",
                recommendation=(
                    "Add relevant certifications or industry "
                    "credentials when available."
                ),
            )
        )

    if resume.projects:

        project_issues = any(
            "measurable impact" in issue.lower()
            for issue in quality.issues
        )

        if project_issues:
            improvements.append(
                ResumeImprovement(
                    section="Projects",
                    priority="high",
                    issue=(
                        "Project descriptions lack measurable impact"
                    ),
                    recommendation=(
                        "Add measurable results such as accuracy, "
                        "performance improvements, users, documents "
                        "processed, or processing-time reductions."
                    ),
                )
            )

    if quality.ats_score < 70:
        improvements.append(
            ResumeImprovement(
                section="ATS",
                priority="high",
                issue=(
                    "Resume has room for improvement in ATS readiness"
                ),
                recommendation=(
                    "Use clear section headings, relevant technical "
                    "keywords, consistent formatting, and role-specific "
                    "skills supported by your actual experience."
                ),
            )
        )

    return ResumeImprovementResponse(
        improvements=improvements
    )