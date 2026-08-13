import re

from app.schemas.resume_analysis import (
    ExperienceAnalysis,
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
    # Programming
    "Python",
    "Java",
    "JavaScript",
    "TypeScript",
    "C",
    "C++",
    "C#",
    "Go",
    "Rust",

    # Data Science / AI
    "Pandas",
    "NumPy",
    "Matplotlib",
    "Seaborn",
    "Machine Learning",
    "Deep Learning",
    "Artificial Intelligence",
    "Generative AI",
    "GenAI",
    "NLP",
    "Computer Vision",
    "LLM",
    "RAG",

    # Backend / Web
    "FastAPI",
    "Flask",
    "Django",
    "React",
    "Next.js",
    "Node.js",
    "Express",
    "HTML",
    "CSS",
    "Tailwind CSS",

    # Databases
    "PostgreSQL",
    "MySQL",
    "MongoDB",
    "Redis",
    "SQL",
    "Supabase",
    "Firebase",

    # Cloud / DevOps
    "Docker",
    "Kubernetes",
    "AWS",
    "Azure",
    "GCP",
    "Terraform",
    "Jenkins",
    "GitHub Actions",
    "Git",
    "GitHub",
    "Linux",

    # GenAI / LLM
    "Ollama",
    "LangChain",
    "LangGraph",
    "CrewAI",
    "Hugging Face",
    "OpenAI",
    "Gemini",
    "Claude",

    # ML Frameworks
    "PyTorch",
    "TensorFlow",
    "Scikit-learn",
    "XGBoost",
    "LightGBM",

    # Vector / Search
    "Vector Databases",
    "Qdrant",
    "FAISS",
    "Semantic Search",

    # AI / Speech / Vision
    "Whisper",
    "Faster Whisper",
    "OpenCV",
    "Speech Recognition",
    "Text-to-Speech",
    "Voice Synthesis",
    "Voice Cloning",

    # Messaging
    "Apache Kafka",
    "RabbitMQ",

    # ORM / Backend Tools
    "Prisma",
    "SQLAlchemy",

    # Career-Setu specific
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

def normalize_skill_name(skill: str) -> str:
    """
    Normalize common skill naming variations.
    """

    aliases = {
        "sementic search": "Semantic Search",
        "semantic searching": "Semantic Search",
        "faster-whisper": "Faster Whisper",
        "generative ai": "Generative AI",
        "text to speech": "Text-to-Speech",
        "speech to text": "Speech Recognition",
        "voice synthesis": "Voice Synthesis",
        "voice cloning": "Voice Cloning",
    }

    normalized = skill.strip()

    return aliases.get(
        normalized.lower(),
        normalized,
    )

def normalize_project_skills(
    skill_lines: list[str],
) -> list[str]:
    """
    Convert raw project skill lines into clean individual skills.
    """

    skills = []

    for line in skill_lines:

        known = split_skills([line])

        for skill in known:
            normalized = normalize_skill_name(skill)

            if normalized not in skills:
                skills.append(normalized)

    return unique_skills(skills)

def extract_unknown_skills(text: str) -> list[str]:
    """
    Detect potential skills that are not present in KNOWN_SKILLS.

    This is a heuristic fallback. The LLM layer will later
    perform more reliable semantic skill extraction.
    """

    if not text:
        return []

    # Normalize common separators
    cleaned = re.sub(
        r"[|,/;•·]+",
        ",",
        text,
    )

    # Split comma-separated values
    candidates = []

    for part in cleaned.split(","):
        part = part.strip()

        if not part:
            continue

        # Split long whitespace-separated skill sequences
        words = part.split()

        if len(words) <= 4:
            candidates.append(part)

    return candidates



def unique_skills(skills: list[str]) -> list[str]:
    """
    Remove duplicate skills while preserving order.
    """

    result = []
    seen = set()

    for skill in skills:

        key = skill.lower().strip()

        if key not in seen:
            seen.add(key)
            result.append(skill)

    return result

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

        current["skills"] = unique_skills(
            current["skills"]
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
                    current["skills"].extend(
                        normalize_project_skills([value])
                )

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

                current["skills"].extend(
                    normalize_project_skills([line])
                )

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

def extract_experience_candidates(text: str) -> list[str]:
    """
    Extract lines belonging to the experience section.
    Supports common resume section names.
    """

    lines = [
        normalize_line(line)
        for line in text.splitlines()
        if normalize_line(line)
    ]

    experience_headings = {
        "experience",
        "work experience",
        "professional experience",
        "employment history",
        "work history",
        "career history",
        "internships",
        "internship experience",
    }

    candidates = []
    inside_experience = False

    for line in lines:

        normalized = (
            line.lower()
            .strip()
            .rstrip(":")
        )

        if normalized in experience_headings:
            inside_experience = True
            continue

        if not inside_experience:
            continue

        if normalized in MAJOR_SECTION_HEADINGS:
            break

        candidates.append(line)

    return candidates

def structure_experience_candidates(
    candidates: list[str],
) -> list[ExperienceAnalysis]:
    """
    Convert experience candidate lines into structured
    experience records.
    """

    experiences = []

    current = None
    description_lines = []

    date_range_pattern = re.compile(
        r"^"
        r"(?P<start>"
        r"(?:\d{1,2}\s+)?"
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"[a-z]*"
        r"(?:,\s*)?\s*\d{4}"
        r"|"
        r"\d{1,2}/\d{4}"
        r"|"
        r"\d{4}"
        r")"
        r"\s*[-–]\s*"
        r"(?P<end>"
        r"(?:\d{1,2}\s+)?"
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)"
        r"[a-z]*"
        r"(?:,\s*)?\s*\d{4}"
        r"|"
        r"\d{1,2}/\d{4}"
        r"|"
        r"\d{4}"
        r"|"
        r"Present|Current"
        r")"
        r"(?P<rest>.*)$",
        re.IGNORECASE,
    )

    def save_current_experience():
        nonlocal current
        nonlocal description_lines

        if current is None:
            return

        current["description"] = (
            " ".join(description_lines).strip()
            or None
        )

        current["skills"] = unique_skills(
            current["skills"]
        )

        experiences.append(
            ExperienceAnalysis(**current)
        )

        current = None
        description_lines = []

    for line in candidates:

        lower = line.lower().strip()

        # --------------------------------------------
        # New experience detected by date range
        # --------------------------------------------

        match = date_range_pattern.match(line)

        if match:

            save_current_experience()

            current = {
                "company": None,
                "role": None,
                "start_date": match.group("start").strip(),
                "end_date": match.group("end").strip(),
                "description": None,
                "skills": [],
            }

            rest = match.group("rest").strip()

            if rest:
                current["role"] = rest

            continue

        if current is None:
            continue

        # --------------------------------------------
        # Skills
        # --------------------------------------------

        if lower.startswith("key skills:"):

            value = line.split(
                ":",
                1,
            )[1].strip()

            if value:
                current["skills"].extend(
                    normalize_project_skills(
                        [value]
                    )
                )

            continue

        # --------------------------------------------
        # Company
        # --------------------------------------------

        if lower.startswith("company:"):

            current["company"] = line.split(
                ":",
                1,
            )[1].strip()

            continue

        # --------------------------------------------
        # Role
        # --------------------------------------------

        if lower.startswith("role:"):

            current["role"] = line.split(
                ":",
                1,
            )[1].strip()

            continue

        # --------------------------------------------
        # Description
        # --------------------------------------------

        if (
            lower.startswith("developed ")
            or lower.startswith("worked ")
            or lower.startswith("built ")
            or lower.startswith("responsible ")
            or lower.startswith("created ")
            or lower.startswith("implemented ")
            or lower.startswith("managed ")
        ):

            description_lines.append(line)
            continue

        # Continue description
        if description_lines:
            description_lines.append(line)

    save_current_experience()

    return experiences

def extract_simple_section(
    text: str,
    headings: set[str],
) -> list[str]:
    """
    Extract a simple resume section such as
    certifications, achievements, or languages.
    """

    lines = [
        normalize_line(line)
        for line in text.splitlines()
        if normalize_line(line)
    ]

    results = []
    inside_section = False

    for line in lines:

        normalized = (
            line.lower()
            .strip()
            .rstrip(":")
        )

        if normalized in headings:
            inside_section = True
            continue

        if inside_section and normalized in MAJOR_SECTION_HEADINGS:
            break

        if inside_section:
            results.append(line)

    return results

def extract_certifications_data(
    text: str,
) -> list[str]:

    return extract_simple_section(
        text,
        {
            "certifications",
            "certificates",
            "professional certifications",
        },
    )

def extract_achievements_data(
    text: str,
) -> list[str]:

    return extract_simple_section(
        text,
        {
            "achievements",
            "awards",
            "honors",
            "honours",
        },
    )

def extract_languages_data(
    text: str,
) -> list[str]:

    return extract_simple_section(
        text,
        {
            "languages",
            "language proficiency",
        },
    )

def extract_summary(text: str) -> str | None:
    """
    Extract a resume summary/profile section.
    """

    summary_headings = {
        "summary",
        "professional summary",
        "profile",
        "professional profile",
        "career objective",
        "objective",
        "about me",
    }

    lines = [
        normalize_line(line)
        for line in text.splitlines()
        if normalize_line(line)
    ]

    results = []
    inside_summary = False

    for line in lines:
        normalized = (
            line.lower()
            .strip()
            .rstrip(":")
        )

        if normalized in summary_headings:
            inside_summary = True
            continue

        if inside_summary and normalized in MAJOR_SECTION_HEADINGS:
            break

        if inside_summary:
            results.append(line)

    if not results:
        return None

    return " ".join(results).strip()

def analyze_resume_text(
    text: str,
) -> ResumeAnalysis:
    """
    Convert extracted resume text into structured resume data.
    """
    summary = extract_summary(text)

    skill_lines = extract_project_skills(text)

    project_candidates = extract_project_candidates(text)

    projects = structure_project_candidates(
        project_candidates
    )

    experience_candidates = extract_experience_candidates(
        text
    )

    experiences = structure_experience_candidates(
        experience_candidates
    )   

    return ResumeAnalysis(
    full_name=extract_name(text),
    email=extract_email(text),
    phone=extract_phone(text),
    summary=summary,

    skills=normalize_project_skills(
        skill_lines
    ),

    education=extract_education(text),

    experience=experiences,

    projects=projects,

    certifications=extract_certifications_data(text),

    achievements=extract_achievements_data(text),

    languages=extract_languages_data(text),

    
)