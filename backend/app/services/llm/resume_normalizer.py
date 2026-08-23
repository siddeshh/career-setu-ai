from app.schemas.resume_analysis import ResumeAnalysis


SKILL_ALIASES = {
    "sementic search": "Semantic Search",
    "semantic searching": "Semantic Search",
    "voice cloning": "Voice Cloning",
    "voice synthesis": "Voice Synthesis",
    "text to speech": "Text-to-Speech",
    "text-to-speech": "Text-to-Speech",
    "speech to text": "Speech Recognition",
    "speech-to-text": "Speech Recognition",
    "faster-whisper": "Faster Whisper",
    "generative ai": "Generative AI",
    "gen ai": "GenAI",
    "ai automation": "AI Automation",
    "data feeding": None,
    "pdfp": None,
}


CANONICAL_NAMES = {
    "python": "Python",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "artificial intelligence": "Artificial Intelligence",
    "generative ai": "Generative AI",
    "genai": "GenAI",
    "nlp": "NLP",
    "computer vision": "Computer Vision",
    "llm": "LLM",
    "rag": "RAG",
    "fastapi": "FastAPI",
    "flask": "Flask",
    "django": "Django",
    "react": "React",
    "next.js": "Next.js",
    "node.js": "Node.js",
    "express": "Express",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "redis": "Redis",
    "docker": "Docker",
    "kubernetes": "Kubernetes",
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "ollama": "Ollama",
    "langchain": "LangChain",
    "hugging face": "Hugging Face",
    "pytorch": "PyTorch",
    "tensorflow": "TensorFlow",
    "scikit-learn": "Scikit-learn",
    "vector databases": "Vector Databases",
    "qdrant": "Qdrant",
    "faiss": "FAISS",
    "whisper": "Whisper",
    "faster whisper": "Faster Whisper",
    "opencv": "OpenCV",
    "speech recognition": "Speech Recognition",
    "text-to-speech": "Text-to-Speech",
    "voice synthesis": "Voice Synthesis",
    "voice cloning": "Voice Cloning",
    "semantic search": "Semantic Search",
    "secure ai deployment": "Secure AI Deployment",
    "ai automation": "AI Automation",
    "report generation": "Report Generation",
    "resume analysis": "Resume Analysis",
}


VALID_SPOKEN_LANGUAGES = {
    "english",
    "hindi",
    "marathi",
    "tamil",
    "telugu",
    "kannada",
    "malayalam",
    "bengali",
    "gujarati",
    "french",
    "german",
    "spanish",
    "japanese",
    "korean",
    "chinese",
}


def normalize_skill(skill: str) -> str | None:
    """
    Normalize one skill.
    """

    if not skill:
        return None

    value = skill.strip()

    if not value:
        return None

    lower_value = value.lower()

    if lower_value in SKILL_ALIASES:
        return SKILL_ALIASES[lower_value]

    if lower_value in CANONICAL_NAMES:
        return CANONICAL_NAMES[lower_value]

    return value


def normalize_skills(
    skills: list[str],
) -> list[str]:

    result = []
    seen = set()

    for skill in skills:

        normalized = normalize_skill(skill)

        if normalized is None:
            continue

        key = normalized.lower()

        if key in seen:
            continue

        seen.add(key)
        result.append(normalized)

    return result


def normalize_languages(
    languages: list[str],
) -> list[str]:

    result = []
    seen = set()

    for language in languages:

        if not language:
            continue

        value = language.strip()

        if value.lower() not in VALID_SPOKEN_LANGUAGES:
            continue

        key = value.lower()

        if key in seen:
            continue

        seen.add(key)

        result.append(value.title())

    return result


def extract_languages_from_text(
    text: str,
) -> list[str]:
    """
    Recover explicitly listed spoken languages from text.

    This is intentionally conservative.
    It only extracts languages from common
    'Known Languages' style text.
    """

    if not text:
        return []

    text_lower = text.lower()

    markers = [
        "known languages",
        "languages known",
    ]

    found = []

    for marker in markers:

        if marker not in text_lower:
            continue

        start = text_lower.find(marker)

        section = text[
            start:start + 150
        ]

        for language in VALID_SPOKEN_LANGUAGES:

            if language in section.lower():

                found.append(language)

    return normalize_languages(found)


def split_company_and_role(
    company: str | None,
    role: str | None,
):
    """
    Split values such as:

        Getmy Solutions | IT / Computers - Software

    into:

        company = Getmy Solutions
        role = IT / Computers - Software
    """

    if role and "|" in role:

        parts = [
            part.strip()
            for part in role.split("|")
            if part.strip()
        ]

        if len(parts) >= 2:

            if not company:
                company = parts[0]

            role = " | ".join(parts[1:])

    return company, role


def extract_certifications_from_achievements(
    achievements: list[str],
    certifications: list[str],
):
    """
    Recover certification entries when Gemini
    incorrectly places them inside achievements.

    Only explicit certification names are recovered.
    """

    cleaned_achievements = []

    certification_markers = [
        "certified",
        "certification",
        "certificate",
        "course",
        "assessment",
        "oracle certified",
    ]

    for item in achievements:

        if not item:
            continue

        value = item.strip()
        lower_value = value.lower()

        is_certification = any(
            marker in lower_value
            for marker in certification_markers
        )

        if is_certification:

            # Do not move section headings alone.
            if lower_value in {
                "certifications",
                "certification",
                "assessments",
                "assessments / certifications",
                "courses & certifications",
                "training & certifications",
            }:
                continue

            certifications.append(value)

        else:

            cleaned_achievements.append(value)

    return (
        cleaned_achievements,
        certifications,
    )


def deduplicate_strings(
    values: list[str],
) -> list[str]:

    result = []
    seen = set()

    for value in values:

        if not value:
            continue

        value = value.strip()

        if not value:
            continue

        key = value.lower()

        if key in seen:
            continue

        seen.add(key)
        result.append(value)

    return result


def normalize_certifications(
    certifications: list[str],
) -> list[str]:

    result = []

    for certification in certifications:

        if not certification:
            continue

        value = certification.strip()

        if not value:
            continue

        # Remove common section-heading noise.
        if value.lower() in {
            "certifications",
            "certification",
            "certificates",
            "assessments",
            "assessments / certifications",
            "courses & certifications",
            "training & certifications",
        }:
            continue

        result.append(value)

    return deduplicate_strings(result)


def normalize_resume(
    resume: ResumeAnalysis,
) -> ResumeAnalysis:
    """
    Normalize Gemini's ResumeAnalysis output.

    This function does NOT invent resume information.
    It only cleans, separates, and reclassifies
    information already present in Gemini's output.
    """

    # --------------------------------------------------
    # Name
    # --------------------------------------------------

    if resume.full_name:

        resume.full_name = (
            resume.full_name
            .strip()
            .title()
        )

    # --------------------------------------------------
    # Email
    # --------------------------------------------------

    if resume.email:

        resume.email = (
            resume.email
            .strip()
            .lower()
        )

    # --------------------------------------------------
    # Phone
    # --------------------------------------------------

    if resume.phone:

        resume.phone = (
            resume.phone
            .strip()
        )

    # --------------------------------------------------
    # Global skills
    # --------------------------------------------------

    resume.skills = normalize_skills(
        resume.skills
    )

    # --------------------------------------------------
    # Project skills
    # --------------------------------------------------

    for project in resume.projects:

        project.skills = normalize_skills(
            project.skills
        )

    # --------------------------------------------------
    # Experience
    # --------------------------------------------------

    for experience in resume.experience:

        (
            experience.company,
            experience.role,
        ) = split_company_and_role(
            experience.company,
            experience.role,
        )

        experience.skills = normalize_skills(
            experience.skills
        )

    # --------------------------------------------------
    # Certifications
    # --------------------------------------------------

    (
        resume.achievements,
        resume.certifications,
    ) = extract_certifications_from_achievements(
        resume.achievements,
        resume.certifications,
    )

    resume.certifications = normalize_certifications(
        resume.certifications
    )

    # --------------------------------------------------
    # Languages
    # --------------------------------------------------

    resume.languages = normalize_languages(
        resume.languages
    )

    # Recover languages if Gemini accidentally
    # placed them inside achievements.
    achievement_text = " ".join(
        resume.achievements
    )

    recovered_languages = extract_languages_from_text(
        achievement_text
    )

    resume.languages = normalize_languages(
        resume.languages
        + recovered_languages
    )

    # --------------------------------------------------
    # Deduplicate achievements
    # --------------------------------------------------

    resume.achievements = deduplicate_strings(
        resume.achievements
    )

    return resume