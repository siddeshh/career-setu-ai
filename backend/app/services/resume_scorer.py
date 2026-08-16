from app.schemas.resume_analysis import (
    ResumeAnalysis,
    ResumeScore,
    ResumeQuality,
    ScoreBreakdown,
)

import re

def detect_candidate_type(
    resume: ResumeAnalysis,
) -> str:
    """
    Determine whether the candidate is a student,
    fresher, or experienced candidate.
    """

    if resume.experience:
        return "experienced"

    # Students usually have education + projects
    # but no professional experience.
    if resume.education and resume.projects:
        return "student"

    if resume.education:
        return "fresher"

    return "unknown"

def has_measurable_impact(
    text: str,
) -> bool:

    if not text:
        return False

    text_lower = text.lower()

    # Explicit numerical evidence
    numerical_patterns = [
        r"\b\d+(?:\.\d+)?%",
        r"\b\d+\+",
        r"\b\d+(?:,\d{3})*\s+(?:users|documents|requests|records|files|candidates|transactions)\b",
        r"\b(?:over|more than|approximately|around)\s+\d+\b",
    ]

    for pattern in numerical_patterns:
        if re.search(pattern, text_lower):
            return True

    # Explicit result-oriented language combined
    # with a measurable technical concept
    impact_verbs = (
        "improved",
        "increased",
        "reduced",
        "decreased",
        "achieved",
        "optimized",
    )

    measurable_terms = (
        "accuracy",
        "performance",
        "latency",
        "speed",
        "efficiency",
        "processing time",
        "response time",
        "throughput",
        "error rate",
        "success rate",
    )

    has_impact_verb = any(
        verb in text_lower
        for verb in impact_verbs
    )

    has_measurable_term = any(
        term in text_lower
        for term in measurable_terms
    )

    return (
        has_impact_verb
        and has_measurable_term
    )

def calculate_resume_quality(
    resume: ResumeAnalysis,
) -> ResumeQuality:

    issues = []
    recommendations = []

    # --------------------------------
    # Content quality
    # --------------------------------

    content_score = 0

    # Professional summary
    if resume.summary:
        content_score += 15

    # Skills
    if resume.skills:
        content_score += 15

    # Education
    if resume.education:
        content_score += 15

    # Experience
    if resume.experience:
        content_score += 15

    # Projects
    if resume.projects:
        project_points = 0

    for project in resume.projects:

        if project.title:
            project_points += 2

        if project.description:
            project_points += 2

        if project.skills:
            project_points += 1

        if project.start_date or project.end_date:
            project_points += 1

        if project.url:
            project_points += 1

        if has_measurable_impact(
            project.description
        ):
            project_points += 2

    # Maximum 25 points from projects
    content_score += min(
        25,
        project_points,
    )

    # Certifications
    if resume.certifications:
        content_score += 5

    # Maximum content score = 100
    content_score = min(
        100,
        content_score,
    )

    # --------------------------------
    # ATS readiness
    # --------------------------------

    ats_score = 0

    # Contact information
    if resume.full_name:
        ats_score += 15

    if resume.email:
        ats_score += 15

    if resume.phone:
        ats_score += 10

    # Resume structure
    if resume.summary:
        ats_score += 10

    if resume.skills:
        ats_score += 15

    if resume.education:
        ats_score += 10

    # Practical content
    if resume.experience:
        ats_score += 10

    elif resume.projects:
        # Students can demonstrate practical experience
        # through projects.
        ats_score += 7

    # Additional sections
    if resume.certifications:
        ats_score += 5

    if resume.languages:
        ats_score += 3

    # --------------------------------
    # Formatting / structure
    # --------------------------------

    formatting_score = 0

    sections_present = 0

    if resume.summary:
        sections_present += 1

    if resume.skills:
        sections_present += 1

    if resume.education:
        sections_present += 1

    if resume.experience:
        sections_present += 1

    if resume.projects:
        sections_present += 1

    if resume.certifications:
        sections_present += 1

    formatting_score = min(
        100,
        sections_present * 16,
    )

    # --------------------------------
    # Issues
    # --------------------------------

    if not resume.summary:
        issues.append(
            "Professional summary is missing"
        )

        recommendations.append(
            "Add a concise professional summary "
            "targeted toward the desired role"
        )

    if not resume.experience:
        issues.append(
            "No professional experience is listed"
        )

        recommendations.append(
            "Add internships, work experience, "
            "freelance work, or relevant practical experience"
        )

    if not resume.certifications:
        issues.append(
            "No certifications are listed"
        )

        recommendations.append(
            "Add relevant certifications when available"
        )

    if len(resume.skills) < 7:
        issues.append(
            "Technical skill coverage is limited"
        )

        recommendations.append(
            "Add relevant skills that are supported "
            "by your actual projects or experience"
        )

    if resume.projects:

        projects_without_impact = [
            project.title
            for project in resume.projects
            if not has_measurable_impact(
                project.description
            )
        ]
    

    if projects_without_impact:
        issues.append(
            "Project descriptions lack measurable impact"
        )

        recommendations.append(
            "Add measurable results such as accuracy, "
            "performance improvements, users, documents "
            "processed, or processing time reductions"
        )

    # --------------------------------
    # Overall quality
    # --------------------------------

    quality_score = round(
        (
            content_score
            + ats_score
            + formatting_score
        ) / 3
    )

    return ResumeQuality(
        quality_score=quality_score,
        ats_score=ats_score,
        content_score=content_score,
        formatting_score=formatting_score,
        issues=issues,
        recommendations=recommendations,
    )

def calculate_resume_score(
    resume: ResumeAnalysis,
) -> ResumeScore:

    candidate_type = detect_candidate_type(resume)

    quality = calculate_resume_quality(resume)

    # ==================================================
    # 1. CONTACT INFORMATION — 10
    # ==================================================

    contact_score = 0

    if resume.full_name:
        contact_score += 4

    if resume.email:
        contact_score += 3

    if resume.phone:
        contact_score += 3

    # ==================================================
    # 2. PROFESSIONAL SUMMARY — 10
    # ==================================================

    summary_score = 10 if resume.summary else 0

    # ==================================================
    # 3. SKILLS — 15
    # ==================================================

    skill_count = len(resume.skills)

    if skill_count >= 10:
        skills_score = 15
    elif skill_count >= 7:
        skills_score = 12
    elif skill_count >= 4:
        skills_score = 8
    elif skill_count > 0:
        skills_score = 4
    else:
        skills_score = 0

    # ==================================================
    # 4. EDUCATION — 15
    # ==================================================

    education_score = 15 if resume.education else 0

    # ==================================================
    # 5. EXPERIENCE / PRACTICAL EXPERIENCE — 20
    # ==================================================

    experience_score = 0

    if resume.experience:
        experience_count = len(resume.experience)

        if experience_count >= 2:
            experience_score = 20
        else:
            experience_score = 15

    # Students can receive partial credit through
    # substantial project work.
    elif candidate_type == "student":
        project_count = len(resume.projects)

        if project_count >= 3:
            experience_score = 10
        elif project_count >= 2:
            experience_score = 7
        elif project_count == 1:
            experience_score = 4

    # ==================================================
    # 6. PROJECTS — 15
    # ==================================================

    project_count = len(resume.projects)

    if project_count >= 3:
        projects_score = 15
    elif project_count == 2:
        projects_score = 12
    elif project_count == 1:
        projects_score = 8
    else:
        projects_score = 0

    # ==================================================
    # 7. CERTIFICATIONS — 5
    # ==================================================

    certifications_score = (
        5 if resume.certifications else 0
    )

    # ==================================================
    # 8. RESUME COMPLETENESS — 10
    # ==================================================

    completeness_score = 0

    if resume.full_name:
        completeness_score += 2

    if resume.email:
        completeness_score += 2

    if resume.phone:
        completeness_score += 1

    if resume.education:
        completeness_score += 2

    if resume.projects:
        completeness_score += 2

    if resume.skills:
        completeness_score += 1

    # ==================================================
    # TOTAL
    # ==================================================

    overall_score = (
        contact_score
        + summary_score
        + skills_score
        + education_score
        + experience_score
        + projects_score
        + certifications_score
        + completeness_score
    )

    # ==================================================
    # STRENGTHS
    # ==================================================

    strengths = []

    if contact_score == 10:
        strengths.append(
            "Complete contact information"
        )

    if skills_score >= 12:
        strengths.append(
            "Strong technical skills"
        )

    if education_score >= 10:
        strengths.append(
            "Education information is clearly provided"
        )

    if projects_score >= 12:
        strengths.append(
            "Strong project portfolio"
        )

    if experience_score >= 15:
        strengths.append(
            "Relevant professional experience"
        )

    if candidate_type == "student" and project_count >= 2:
        strengths.append(
            "Strong practical experience through projects"
        )

    if certifications_score > 0:
        strengths.append(
            "Relevant certifications included"
        )

    # ==================================================
    # WEAKNESSES
    # ==================================================

    weaknesses = []

    if not resume.summary:
        weaknesses.append(
            "Professional summary is missing"
        )

    if not resume.experience:
        if candidate_type == "student":
            weaknesses.append(
                "No professional experience or internship is listed"
            )
        else:
            weaknesses.append(
                "Professional experience is missing"
            )

    if not resume.certifications:
        weaknesses.append(
            "Certifications are missing"
        )

    if skill_count < 7:
        weaknesses.append(
            "Resume contains a limited number of listed skills"
        )

    if project_count == 0:
        weaknesses.append(
            "No projects are listed"
        )

    # ==================================================
    # RECOMMENDATIONS
    # ==================================================

    recommendations = []

    if not resume.summary:
        recommendations.append(
            "Add a concise 2-3 line professional summary"
        )

    if candidate_type == "student":
        if not resume.experience:
            recommendations.append(
                "Add internships, hackathons, freelance work, "
                "or other practical experience when available"
            )

    elif candidate_type in {
        "fresher",
        "experienced",
    }:
        if not resume.experience:
            recommendations.append(
                "Add relevant professional or internship experience"
            )

    if not resume.certifications:
        recommendations.append(
            "Add relevant certifications or industry credentials"
        )

    if project_count < 2:
        recommendations.append(
            "Add more relevant projects with measurable outcomes"
        )

    if skill_count < 7:
        recommendations.append(
            "Add relevant technical skills supported by your projects"
        )

    # ==================================================
    # RETURN
    # ==================================================

    return ResumeScore(
        candidate_type=candidate_type,
        overall_score=overall_score,
        breakdown=ScoreBreakdown(
            contact_information=contact_score,
            summary=summary_score,
            skills=skills_score,
            education=education_score,
            experience=experience_score,
            projects=projects_score,
            certifications=certifications_score,
            completeness=completeness_score,
        ),
        quality=quality,
        strengths=strengths,
        weaknesses=weaknesses,
        recommendations=recommendations,
        
    )