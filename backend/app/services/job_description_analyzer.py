import re

from app.schemas.job_matching import JobDescriptionAnalysis


SKILL_KEYWORDS = {
    "python": "Python",
    "java": "Java",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
    "c++": "C++",
    "machine learning": "Machine Learning",
    "deep learning": "Deep Learning",
    "artificial intelligence": "Artificial Intelligence",
    "ai": "AI",
    "generative ai": "Generative AI",
    "genai": "GenAI",
    "nlp": "NLP",
    "natural language processing": "NLP",
    "computer vision": "Computer Vision",
    "opencv": "OpenCV",
    "llm": "LLM",
    "large language model": "LLM",
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
    "git": "Git",
    "github": "GitHub",
    "linux": "Linux",
    "sql": "SQL",
    "tensorflow": "TensorFlow",
    "pytorch": "PyTorch",
    "scikit-learn": "Scikit-learn",
    "langchain": "LangChain",
    "vector database": "Vector Databases",
    "vector databases": "Vector Databases",
}


def _extract_skills(text: str) -> list[str]:
    """
    Extract known technical skills from job description.
    """

    text_lower = text.lower()

    found = []
    seen = set()

    for keyword, canonical_name in SKILL_KEYWORDS.items():

        pattern = rf"(?<!\w){re.escape(keyword)}(?!\w)"

        if re.search(pattern, text_lower):

            key = canonical_name.lower()

            if key not in seen:
                seen.add(key)
                found.append(canonical_name)

    return found


def _extract_section(
    text: str,
    section_names: list[str],
) -> str:
    """
    Extract text belonging to a recognizable section.
    """

    lines = text.splitlines()

    start_index = None

    for index, line in enumerate(lines):

        normalized = line.strip().lower()

        for section_name in section_names:

            if normalized.startswith(
                section_name.lower()
            ):

                start_index = index + 1
                break

        if start_index is not None:
            break

    if start_index is None:
        return ""

    collected = []

    known_sections = {
        "requirements",
        "qualifications",
        "responsibilities",
        "skills",
        "experience",
        "education",
        "preferred qualifications",
        "preferred skills",
        "about the role",
        "about us",
        "job description",
    }

    for line in lines[start_index:]:

        normalized = line.strip().lower()

        if normalized in known_sections:
            break

        if line.strip():
            collected.append(line.strip())

    return "\n".join(collected)


def _extract_job_title(text: str) -> str | None:
    """
    Extract job title from common job description formats.
    """


    match = re.search(
        r"job\s*title\s*:\s*(.*?)(?=\s+company\s*:|\s+location\s*:|\s+requirements?\s*:|\s+responsibilities\s*:|$)",
        text,
        re.IGNORECASE,
    )

    if match:
        return match.group(1).strip()

    return None


def _extract_company(text: str) -> str | None:
    """
    Extract company name from common job description formats.
    """



    match = re.search(
        r"company\s*:\s*(.*?)(?=\s+location\s*:|\s+we\s+are\s+looking|\s+requirements?\s*:|\s+responsibilities\s*:|$)",
        text,
        re.IGNORECASE,
    )

    if match:
        return match.group(1).strip()

    return None


def _extract_bullets(text: str) -> list[str]:
    """
    Extract bullet-point lines.
    """

    results = []

    for line in text.splitlines():

        value = line.strip()

        if not value:
            continue

        if value.startswith(
            ("-", "•", "*")
        ):
            cleaned = value.lstrip(
                "-•* "
            ).strip()

            if cleaned:
                results.append(cleaned)

    return results


def analyze_job_description(
    job_description: str,
) -> JobDescriptionAnalysis:
    """
    Analyze a raw job description using
    deterministic rule-based extraction.
    """

    if not job_description:
        raise ValueError(
            "Job description cannot be empty"
        )

    text = job_description.strip()

    if not text:
        raise ValueError(
            "Job description cannot be empty"
        )

    skills = _extract_skills(text)

    required_section = _extract_section(
        text,
        [
            "requirements",
            "required qualifications",
            "required skills",
            "qualifications",
        ],
    )

    preferred_section = _extract_section(
        text,
        [
            "preferred qualifications",
            "preferred skills",
            "nice to have",
        ],
    )

    responsibilities_section = _extract_section(
        text,
        [
            "responsibilities",
            "what you'll do",
            "what you will do",
            "key responsibilities",
        ],
    )

    education_section = _extract_section(
        text,
        [
            "education",
            "educational requirements",
        ],
    )

    required_skills = _extract_skills(
        required_section
    )

    preferred_skills = _extract_skills(
        preferred_section
    )

    responsibilities = _extract_bullets(
        responsibilities_section
    )

    education_requirements = _extract_bullets(
        education_section
    )

    # If no explicit required-skills section
    # exists, use all detected skills.
    if not required_skills:
        required_skills = skills.copy()

    keywords = skills.copy()

    return JobDescriptionAnalysis(
        job_title=_extract_job_title(text),
        company=_extract_company(text),
        required_skills=required_skills,
        preferred_skills=preferred_skills,
        experience_requirements=[],
        education_requirements=education_requirements,
        responsibilities=responsibilities,
        keywords=keywords,
    )