import re

from app.schemas.resume_analysis import (
    ProjectAnalysis,
    ResumeAnalysis,
)


SECTION_HEADINGS = {
    "education",
    "academic background",

    "experience",
    "work experience",
    "professional experience",
    "employment history",
    "career history",

    "projects",
    "personal projects",
    "academic projects",
    "selected projects",
    "relevant projects",

    "skills",
    "technical skills",
    "key skills",
    "technical competencies",
    "core competencies",
    "areas of expertise",

    "certifications",
    "certificates",

    "achievements",
    "awards",

    "languages",

    "personal interests / hobbies",
    "interests",
    "hobbies",

    "personal details",
}

MAJOR_SECTION_HEADINGS = {
    "education",
    "academic background",

    "experience",
    "work experience",
    "professional experience",
    "employment history",
    "career history",

    "projects",
    "personal projects",
    "academic projects",
    "selected projects",
    "relevant projects",

    "certifications",
    "certificates",

    "achievements",
    "awards",

    "languages",

    "personal interests / hobbies",
    "interests",
    "hobbies",

    "personal details",
}

DATE_PATTERNS = [
    # 12 May, 2026
    r"\b\d{1,2}\s+[A-Za-z]+\s*,?\s*\d{4}\b",

    # May 2026
    r"\b[A-Za-z]+\s+\d{4}\b",

    # 2023 - 2027
    r"\b\d{4}\s*[-–]\s*\d{4}\b",

    # 2023 - Present
    r"\b\d{4}\s*[-–]\s*(?:Present|Current)\b",

    # 05/2024
    r"\b\d{1,2}/\d{1,2}/\d{4}\b",
]


KNOWN_SKILLS = [
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "C",
    "C++",
    "C#",
    "Go",
    "Rust",

    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "Generative AI",
    "GenAI",
    "NLP",
    "Computer Vision",
    "LLM",
    "RAG",

    "FastAPI",
    "Flask",
    "Django",
    "React",
    "Next.js",
    "Node.js",
    "Express",

    "PostgreSQL",
    "MySQL",
    "MongoDB",
    "Redis",

    "Docker",
    "Kubernetes",
    "AWS",
    "Azure",
    "GCP",

    "Ollama",
    "LangChain",
    "Hugging Face",
    "PyTorch",
    "TensorFlow",
    "Scikit-learn",

    "Vector Databases",
    "Qdrant",
    "FAISS",

    "Whisper",
    "Faster Whisper",
    "OpenCV",

    "Speech Recognition",
    "Text-to-Speech",
    "Voice Synthesis",
    "Voice Cloning",

    "Semantic Search",
    "Secure AI Deployment",
    "AI Automation",
    "Report Generation",
    "Resume Analysis",
]


def normalize_line(line: str) -> str:
    """Normalize text extracted from a PDF."""

    line = line.strip()

    # Normalize repeated spaces/tabs
    line = re.sub(r"\s+", " ", line)

    return line

def extract_email(text: str) -> str | None:
    """Extract the first email address from the resume."""

    match = re.search(
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b",
        text,
    )

    return match.group(0) if match else None


def extract_phone(text: str) -> str | None:
    """Extract the first likely phone number."""

    patterns = [
        r"\+\d{1,3}[\s-]?\d{10}",
        r"\b\d{10}\b",
        r"\b\d{3}[\s-]\d{3}[\s-]\d{4}\b",
    ]

    for pattern in patterns:
        match = re.search(pattern, text)

        if match:
            return match.group(0)

    return None


def extract_name(text: str) -> str | None:
    """
    Extract candidate name from the resume header.
    """

    lines = [
        normalize_line(line)
        for line in text.splitlines()
        if normalize_line(line)
    ]

    # Look near the beginning of the resume.
    for line in lines[:20]:

        # Ignore obvious contact/details lines
        if "@" in line:
            continue

        if re.search(
            r"(gender|marital|address|date of birth|known languages|"
            r"permanent address|phone|email|emails)\s*:",
            line,
            re.IGNORECASE,
        ):
            continue

        # Handle:
        # SIDDESH MANOJ HIWALEB.Tech. - CSE - Cloud Computing
        match = re.search(
            r"^([A-Za-z]+(?:\s+[A-Za-z]+){1,4})(?=B\.Tech|M\.Tech|B\.E|M\.E|BSc|MSc|Ph\.?|\s*$)",
            line,
            re.IGNORECASE,
        )

        if match:
            return re.sub(
                r"\s+",
                " ",
                match.group(1),
            ).strip().title()

    return None

def is_section_heading(line: str) -> bool:
    """Check whether a line looks like a major resume section."""

    normalized = (
        line.lower()
        .strip()
        .rstrip(":")
    )

    return normalized in SECTION_HEADINGS


def contains_date(line: str) -> bool:
    """Check whether a line contains a recognizable date."""

    return any(
        re.search(
            pattern,
            line,
            re.IGNORECASE,
        )
        for pattern in DATE_PATTERNS
    )


def is_project_start(line: str) -> bool:
    """
    Detect a possible dated project/experience entry.

    This is only a heuristic and is not tied to one
    specific resume format.
    """

    return bool(
        re.match(
            r"^\d{1,2}\s+"
            r"(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
            r"[a-z]*,\s*\d{4}",
            line,
            re.IGNORECASE,
        )
    )


def extract_major_section(
    text: str,
    section_name: str,
) -> list[str]:
    """Extract content from a named resume section."""

    lines = [
        normalize_line(line)
        for line in text.splitlines()
        if normalize_line(line)
    ]

    target = section_name.lower().strip()

    results = []
    inside_section = False

    for line in lines:
        normalized = (
            line.lower()
            .strip()
            .rstrip(":")
        )

        if normalized == target:
            inside_section = True
            continue

        if inside_section:
            normalized_heading = (
                line.lower()
                .strip()
                .rstrip(":")
            )

            if normalized_heading in MAJOR_SECTION_HEADINGS:
                break

        if inside_section:
            results.append(line)

    return results


def extract_education(text: str) -> list[str]:
    """Extract education information."""

    for heading in [
        "education",
        "academic background",
    ]:
        result = extract_major_section(
            text,
            heading,
        )

        if result:
            return result

    return []


def extract_projects(text: str) -> list[str]:
    """Extract project section."""

    for heading in [
        "projects",
        "personal projects",
        "academic projects",
        "selected projects",
        "relevant projects",
    ]:
        result = extract_major_section(
            text,
            heading,
        )

        if result:
            return result

    return []


def extract_experience(text: str) -> list[str]:
    """Extract professional experience."""

    for heading in [
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "career history",
    ]:
        result = extract_major_section(
            text,
            heading,
        )

        if result:
            return result

    return []


def extract_certifications(text: str) -> list[str]:
    """Extract certifications."""

    for heading in [
        "certifications",
        "certificates",
    ]:
        result = extract_major_section(
            text,
            heading,
        )

        if result:
            return result

    return []


def extract_project_skills(text: str) -> list[str]:
    """
    Extract skills from anywhere in the resume.

    Supports:
        Key Skills: Python FastAPI Docker

    and:

        Key Skills:
        Python FastAPI Docker
    """

    lines = [
        normalize_line(line)
        for line in text.splitlines()
        if normalize_line(line)
    ]

    skills = []
    collecting = False

    for line in lines:
        lower = line.lower().strip()

        # Found a Key Skills label anywhere in the resume
        if lower.startswith("key skills"):

            collecting = True

            # Same-line skills
            if ":" in line:
                value = line.split(":", 1)[1].strip()

                if value:
                    skills.append(value)

            continue

        if collecting:

            # Stop at another major section
            if is_section_heading(line):
                collecting = False
                continue

            # Stop at common project metadata
            if lower.startswith(
                (
                    "project link:",
                    "github:",
                    "url:",
                    "mentor:",
                    "team size:",
                    "role:",
                    "responsibilities:",
                    "i have ",
                    "developed ",
                    "built ",
                )
            ):
                collecting = False
                continue

            # Stop when another project/date entry begins
            if is_project_start(line):
                collecting = False
                continue

            skills.append(line)

    return skills

def split_skills(
    skill_lines: list[str],
) -> list[str]:
    """
    Convert skill lines into normalized individual skills.
    """

    found_skills = []

    for line in skill_lines:

        line_lower = line.lower()

        for skill in KNOWN_SKILLS:

            pattern = (
                rf"(?<![A-Za-z0-9+#])"
                rf"{re.escape(skill.lower())}"
                rf"(?![A-Za-z0-9+#])"
            )

            if re.search(pattern, line_lower):

                if skill not in found_skills:
                    found_skills.append(skill)

    return found_skills

def extract_project_candidates(text: str) -> list[str]:
    """
    Extract possible project-related lines without assuming
    one specific resume layout.
    """

    lines = [
        normalize_line(line)
        for line in text.splitlines()
        if normalize_line(line)
    ]

    project_candidates = []

    project_headings = {
        "projects",
        "personal projects",
        "academic projects",
        "selected projects",
        "relevant projects",
        "project",
    }

    inside_projects = False

    for line in lines:
        normalized = line.lower().strip().rstrip(":")

        # Start project section
        if normalized in project_headings:
            inside_projects = True
            continue

        if not inside_projects:
            continue

        # Stop at another major section
        normalized_heading = (
            line.lower()
            .strip()
            .rstrip(":")
        )

        if normalized_heading in MAJOR_SECTION_HEADINGS:
            break

        project_candidates.append(line)

    return project_candidates

def structure_project_candidates(
    candidates: list[str],
) -> list[ProjectAnalysis]:
    """
    Convert project candidate lines into structured projects.

    Handles project entries where the PDF extraction combines
    dates and the project title into one line.
    """

    projects = []

    current = None
    description_lines = []
    collecting_skills = False

    # Supports:
    # 12 May, 2026 - 31 May, 2026Offline Private ChatGPT
    #
    # 04 May, 2026 - 09 May, 2026Offline speech chatbot

    date_range_pattern = re.compile(
        r"^"
        r"(?P<start>\d{1,2}\s+"
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"[a-z]*,\s*\d{4})"
        r"\s*-\s*"
        r"(?P<end>\d{1,2}\s+"
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"[a-z]*,\s*\d{4})"
        r"(?P<title>.*)$",
        re.IGNORECASE,
    )

    def save_current_project():
        nonlocal current
        nonlocal description_lines

        if current is None:
            return

        current["description"] = (
            " ".join(description_lines).strip()
            or None
        )

        projects.append(
            ProjectAnalysis(**current)
        )

        current = None
        description_lines = []

    for line in candidates:

        # ==================================================
        # NEW PROJECT
        # ==================================================

        match = date_range_pattern.match(line)

        if match:

            save_current_project()

            current = {
                "title": match.group("title").strip(),
                "start_date": match.group("start").strip(),
                "end_date": match.group("end").strip(),
                "team_size": None,
                "role": None,
                "description": None,
                "skills": [],
                "url": None,
            }

            collecting_skills = False

            continue

        # ==================================================
        # Ignore lines before first project
        # ==================================================

        if current is None:
            continue

        lower = line.lower().strip()

        # ==================================================
        # TEAM SIZE
        # ==================================================

        if lower.startswith("team size:"):

            value = line.split(
                ":",
                1,
            )[1].strip()

            try:
                current["team_size"] = int(value)
            except ValueError:
                current["team_size"] = None

            continue

        # ==================================================
        # MENTOR
        # ==================================================

        if lower.startswith("mentor:"):
            continue

        # ==================================================
        # PROJECT LINK
        # ==================================================

        if (
            lower.startswith("project link:")
            or lower.startswith("github:")
            or lower.startswith("url:")
        ):

            current["url"] = line.split(
                ":",
                1,
            )[1].strip()

            continue

        # ==================================================
        # KEY SKILLS
        # ==================================================

        if lower.startswith("key skills"):

            collecting_skills = True

            if ":" in line:

                value = line.split(
                    ":",
                    1,
                )[1].strip()

                if value:
                    current["skills"].append(value)

            continue

        # ==================================================
        # SKILL LINES
        # ==================================================

        if collecting_skills:

            if (
                lower.startswith("i have ")
                or lower.startswith("developed ")
                or lower.startswith("built ")
                or lower.startswith("project link:")
            ):

                collecting_skills = False

            else:

                current["skills"].append(line)

                continue

        # ==================================================
        # DESCRIPTION
        # ==================================================

        if (
            lower.startswith("i have ")
            or lower.startswith("developed ")
            or lower.startswith("built ")
        ):

            description_lines.append(line)

            continue

        if description_lines:
            description_lines.append(line)

    # ======================================================
    # SAVE FINAL PROJECT
    # ======================================================

    save_current_project()

    return projects

def analyze_resume_text(
    text: str,
) -> ResumeAnalysis:
    """
    Convert extracted resume text into structured resume data.
    """

    skill_lines = extract_project_skills(text)

    project_candidates = extract_project_candidates(text)

    projects = structure_project_candidates(
        project_candidates
    )

    return ResumeAnalysis(
        full_name=extract_name(text),
        email=extract_email(text),
        phone=extract_phone(text),

        skills=split_skills(skill_lines),

        education=extract_education(text),

        experience=extract_experience(text),

        projects=projects,

        certifications=extract_certifications(text),
    )