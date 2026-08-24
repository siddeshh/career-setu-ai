from app.schemas.resume_analysis import ResumeAnalysis
from app.schemas.job_matching import (
    JobDescriptionAnalysis,
    JobMatchAnalysis,
    SkillMatch,
)


def _normalize(value: str) -> str:
    return value.strip().lower()


def _match_skills(
    resume_skills: list[str],
    job_skills: list[str],
) -> SkillMatch:

    resume_map = {
        _normalize(skill): skill
        for skill in resume_skills
        if skill
    }

    matched = []
    missing = []

    for skill in job_skills:

        if not skill:
            continue

        key = _normalize(skill)

        if key in resume_map:
            matched.append(skill)
        else:
            missing.append(skill)

    return SkillMatch(
        matched=matched,
        missing=missing,
    )


def _match_keywords(
    resume_skills: list[str],
    keywords: list[str],
):
    resume_set = {
        _normalize(skill)
        for skill in resume_skills
        if skill
    }

    matched = []
    missing = []

    for keyword in keywords:

        if not keyword:
            continue

        key = _normalize(keyword)

        if key in resume_set:
            matched.append(keyword)
        else:
            missing.append(keyword)

    return matched, missing


def calculate_match_score(
    skill_match: SkillMatch,
    total_required_skills: int,
) -> int:

    if total_required_skills == 0:
        return 0

    matched_count = len(skill_match.matched)

    score = (
        matched_count
        / total_required_skills
    ) * 100

    return round(score)


def match_resume_to_job(
    resume: ResumeAnalysis,
    job: JobDescriptionAnalysis,
) -> tuple[int, JobMatchAnalysis]:

    required_skills = (
        job.required_skills
    )

    skill_match = _match_skills(
        resume.skills,
        required_skills,
    )

    matched_keywords, missing_keywords = (
        _match_keywords(
            resume.skills,
            job.keywords,
        )
    )

    score = calculate_match_score(
        skill_match,
        len(required_skills),
    )

    strengths = []

    if skill_match.matched:
        strengths.append(
            "Matches required skills: "
            + ", ".join(
                skill_match.matched
            )
        )

    if matched_keywords:
        strengths.append(
            "Matches job keywords: "
            + ", ".join(
                matched_keywords
            )
        )

    skill_gaps = (
        skill_match.missing.copy()
    )

    recommendations = []

    if skill_gaps:
        recommendations.append(
            "Develop the missing skills: "
            + ", ".join(skill_gaps)
        )

    analysis = JobMatchAnalysis(
        skill_match=skill_match,
        matched_keywords=matched_keywords,
        missing_keywords=missing_keywords,
        experience_match=None,
        education_match=None,
        strengths=strengths,
        skill_gaps=skill_gaps,
        recommendations=recommendations,
    )

    return score, analysis