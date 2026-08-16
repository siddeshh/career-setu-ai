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


def normalize_skill(
    skill: str,
) -> str | None:
    """
    Normalize one skill.
    """

    if not skill:
        return None

    value = skill.strip()

    if not value:
        return None

    lower_value = value.lower()

    # Explicit alias/removal
    if lower_value in SKILL_ALIASES:
        return SKILL_ALIASES[lower_value]

    # Known canonical skill
    if lower_value in CANONICAL_NAMES:
        return CANONICAL_NAMES[lower_value]

    # Unknown skill:
    # preserve it rather than inventing a replacement.
    return value


def normalize_skills(
    skills: list[str],
) -> list[str]:
    """
    Normalize and deduplicate skills.
    """

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
    """
    Keep only recognizable spoken languages.
    """

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

        result.append(
            value.title()
        )

    return result


def normalize_resume(
    resume: ResumeAnalysis,
) -> ResumeAnalysis:
    """
    Normalize Gemini's ResumeAnalysis output.
    """

    # Name
    if resume.full_name:
        resume.full_name = (
            resume.full_name
            .strip()
            .title()
        )

    # Email
    if resume.email:
        resume.email = (
            resume.email
            .strip()
            .lower()
        )

    # Phone
    if resume.phone:
        resume.phone = (
            resume.phone
            .strip()
        )

    # Global skills
    resume.skills = normalize_skills(
        resume.skills
    )

    # Spoken languages
    resume.languages = normalize_languages(
        resume.languages
    )

    # Project skills
    for project in resume.projects:

        project.skills = normalize_skills(
            project.skills
        )

    # Experience skills
    for experience in resume.experience:

        experience.skills = normalize_skills(
            experience.skills
        )

    return resume