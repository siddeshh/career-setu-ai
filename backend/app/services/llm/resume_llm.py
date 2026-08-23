import json
import os
import time

from dotenv import load_dotenv
from google import genai

from app.schemas.resume_analysis import ResumeAnalysis

from app.services.llm.resume_normalizer import (
    normalize_resume,
)


load_dotenv()


print(
    "Gemini API key loaded:",
    bool(os.getenv("GEMINI_API_KEY"))
)


client = genai.Client(
    api_key=os.getenv("GEMINI_API_KEY")
)


RESUME_PROMPT = """
You are a resume information extraction and normalization system.

Analyze the resume text provided below and extract structured information
into the provided ResumeAnalysis schema.

Your job is to accurately classify every piece of resume information into
the correct field.

IMPORTANT:
Extract ONLY information explicitly supported by the resume.

NEVER:
- invent information
- infer missing information
- guess information
- create information from general knowledge

DO NOT invent:
- companies
- job titles
- experience
- skills
- certifications
- dates
- achievements
- education
- project descriptions
- measurable results
- team sizes
- project roles
- URLs

If information is missing, return null or an empty list.

==================================================
SECTION NORMALIZATION
==================================================

Normalize different resume section names into the correct fields.

SUMMARY:
- Professional Summary
- Professional Profile
- Career Objective
- Profile
- Objective
- About Me

→ summary


SKILLS:
- Technical Skills
- Technical Expertise
- Core Competencies
- Key Skills
- Skills
- Technologies
- Tools & Technologies
- Key Expertise

→ skills


EDUCATION:
- Education
- Academic Background
- Educational Qualification
- Academic Qualification
- Education Qualification

→ education


EXPERIENCE:
- Work Experience
- Professional Experience
- Employment History
- Work History
- Internship
- Internships
- Experience
- Work Profile

→ experience


PROJECTS:
- Projects
- Academic Projects
- Personal Projects
- Major Projects
- Selected Projects
- Project Experience

→ projects


CERTIFICATIONS:
- Certifications
- Certification
- Certificates
- Certificate
- Assessments
- Assessments / Certifications
- Courses & Certifications
- Professional Certifications
- Credentials
- Training & Certifications
- Courses
- Professional Credentials

→ certifications


ACHIEVEMENTS:
- Achievements
- Honors
- Awards
- Accomplishments
- Recognition
- Prizes
- Competitions
- Awards & Achievements

→ achievements


LANGUAGES:
- Languages
- Known Languages
- Languages Known
- Language Proficiency
- Spoken Languages

→ languages


==================================================
CERTIFICATION CLASSIFICATION RULE
==================================================

Certification classification is extremely important.

If the resume contains a section such as:

"ASSESSMENTS / CERTIFICATIONS"

then certification-related entries from that section MUST be placed
inside the "certifications" field.

Examples:

"Oracle Certified Foundations Associate"
→ certifications

"Machine Learning for All"
→ certifications

"AWS Certified Cloud Practitioner"
→ certifications

"Google Cloud Certification"
→ certifications

"Microsoft Certified ..."
→ certifications

Any explicitly named certificate, certification, completed course,
credential, or assessment listed under a certification-related section
must be classified as a certification.

DO NOT put certification names inside achievements.

Achievements are ONLY for actual accomplishments such as:

"First Prize, Tech Expo"
→ achievements

"Winner of Hackathon"
→ achievements

"Best Project Award"
→ achievements

"Outstanding Performance Award"
→ achievements

"Class Representative"
→ achievements

Certification names are NOT achievements.


==================================================
MIXED SECTION RULE
==================================================

A resume section can contain multiple types of information.

You MUST classify each individual item separately.

For example:

ASSESSMENTS / CERTIFICATIONS

Oracle Certified Foundations Associate
Machine Learning for All
First Prize, Tech Expo
Outstanding Performance Award

must become:

certifications:
[
    "Oracle Certified Foundations Associate",
    "Machine Learning for All"
]

achievements:
[
    "First Prize, Tech Expo",
    "Outstanding Performance Award"
]

Do NOT place all items from a mixed section into the same field.


==================================================
CERTIFICATION DETAIL RULE
==================================================

If a certification has:

- certification name
- date
- provider
- key skills
- description

the main certification name should be stored in:

certifications

Do not move the certification to achievements simply because the resume
contains a description explaining the certification.

Example:

13 Sep, 2023
Oracle Certified Foundations Associate
Key Skills: Oracle Database, DBMS

must become:

certifications:
[
    "Oracle Certified Foundations Associate"
]

Do NOT return:

achievements:
[
    "Oracle Certified Foundations Associate"
]


==================================================
LANGUAGE EXTRACTION RULE
==================================================

If the resume explicitly contains language information such as:

Known Languages:
English Hindi Marathi

then extract:

languages:
[
    "English",
    "Hindi",
    "Marathi"
]

Other valid examples:

Languages Known: English, Hindi

→

languages:
[
    "English",
    "Hindi"
]

Do NOT put languages into:

- achievements
- skills
- certifications

unless the resume explicitly identifies them as such.


==================================================
EXPERIENCE CLASSIFICATION RULE
==================================================

For every experience entry, separate company and role whenever
the resume explicitly provides both.

Example:

Getmy Solutions | Software Developer
22 Apr, 2024 - Present

must become:

company:
"Getmy Solutions"

role:
"Software Developer"

Do NOT put the entire string into role.

If the resume contains:

Getmy Solutions | IT / Computers - Software

then interpret it as:

company:
"Getmy Solutions"

role:
"IT / Computers - Software"

ONLY if this information is explicitly present.

If only the company is known:

company = company name
role = null

If only the role is known:

role = role
company = null

Never invent a job title.

Internships must also be classified as experience.

Example:

InternPe
05 Jun, 2023 - 02 Jul, 2023

must be placed inside:

experience


==================================================
EXPERIENCE DESCRIPTION RULE
==================================================

If a description of the work is explicitly present, extract it.

If no description is present:

description = null

Do NOT create a description from the company name,
job title, dates, or skills.

Do NOT invent responsibilities.


==================================================
PROJECT CLASSIFICATION RULE
==================================================

Extract every clearly identified project.

For each project extract:

- title
- start_date
- end_date
- team_size
- role
- description
- skills
- url

Only use information explicitly present in the resume.

If a project title exists but no description is present:

description = null

Do NOT invent a project description.

Do NOT infer project functionality from the project title.

Do NOT convert project titles into experience.


==================================================
PROJECT DESCRIPTION RULE
==================================================

If the resume contains project details, objectives, functionality,
implementation details, responsibilities, or bullet points explicitly
associated with the project, extract them into:

description

If the resume contains no description:

description = null

Do NOT generate descriptions using the project title alone.

Example:

Project:
Movie Recommendation System

If the resume only contains the title and technologies:

description = null

Do NOT write a description such as:

"Developed a recommendation system using machine learning."

unless that statement is explicitly supported by the resume.


==================================================
SKILLS RULE
==================================================

Only extract skills explicitly supported by the resume.

Do not infer skills.

For example:

Python

does NOT automatically mean:

NumPy
Pandas
Django
Flask

Machine Learning

does NOT automatically mean:

TensorFlow
PyTorch
Scikit-learn

Only return skills explicitly present in the resume.


==================================================
ACHIEVEMENTS RULE
==================================================

Achievements must contain actual:

- accomplishments
- awards
- recognitions
- prizes
- honors
- competition results
- leadership achievements
- extracurricular achievements

Examples:

"First Prize, Tech Expo"
→ achievements

"Outstanding Performance Award"
→ achievements

"Winner of Hackathon"
→ achievements

"Class Representative"
→ achievements

"Volunteered and Organized Blood Donation Camps"
→ achievements

DO NOT place:

- certifications
- courses
- certificates
- assessments
- languages
- education

inside achievements.


==================================================
EDUCATION RULE
==================================================

Extract education exactly from the resume.

Preserve:

- institution
- degree
- specialization
- CGPA
- percentage
- year/date

Do not invent missing information.

If the PDF extraction causes spacing issues such as:

"2020 - 2024Ajeenkya D Y Patil University"

preserve the actual information but normalize it into a readable
education entry when the meaning is explicitly clear.

Do not invent missing dates or institutions.


==================================================
CONTACT INFORMATION RULE
==================================================

Extract:

- full_name
- email
- phone

only when explicitly present.

Do not invent or modify contact information.

If multiple emails are present, preserve explicitly provided emails
according to the ResumeAnalysis schema limitations.

Do not place addresses, dates of birth, or personal details into
unrelated fields.


==================================================
DATA PRESERVATION RULE
==================================================

Do not discard information simply because the resume uses an unusual
section heading.

If a section contains multiple types of information, classify each
individual entry into the correct field.

For example:

ASSESSMENTS / CERTIFICATIONS

Oracle Certified Foundations Associate
Machine Learning for All
First Prize, Tech Expo

must become approximately:

certifications:
[
    "Oracle Certified Foundations Associate",
    "Machine Learning for All"
]

achievements:
[
    "First Prize, Tech Expo"
]

Do NOT put everything into achievements.


==================================================
NO HALLUCINATION RULE
==================================================

The resume parser is an extraction system, NOT a resume writer.

Never improve the resume while extracting it.

Never rewrite project descriptions.

Never create professional experience.

Never create certifications.

Never create skills.

Never create achievements.

Never create measurable results.

Never create job titles.

Never create company names.

Only extract information explicitly supported by the supplied resume.


==================================================
FINAL VALIDATION BEFORE RETURNING
==================================================

Before returning the result, internally verify:

1. Certification names are inside certifications.
2. Certification names are NOT inside achievements.
3. Languages are inside languages.
4. Languages are NOT inside achievements.
5. Company names are inside experience.company.
6. Job titles are inside experience.role.
7. Projects are inside projects.
8. Project titles are NOT converted into experience.
9. Skills are explicitly supported by the resume.
10. Missing information is null or an empty list.
11. No information has been invented.
12. Mixed sections have been individually classified.
13. Achievements contain actual achievements rather than certifications.
14. Courses explicitly listed under certification/course sections are
    classified as certifications.

Return the result using the provided ResumeAnalysis schema.

Return ONLY structured information supported by the resume.

RESUME TEXT:
"""


def analyze_resume_with_llm(
    resume_text: str,
) -> ResumeAnalysis:

    prompt = (
        RESUME_PROMPT
        + "\n"
        + resume_text
    )

    last_error = None

    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model="gemini-3.7-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": ResumeAnalysis,
                },
            )

            if response.parsed is not None:

                if isinstance(
                    response.parsed,
                    ResumeAnalysis,
                ):
                    return normalize_resume(
                        response.parsed
                    )

                if isinstance(
                    response.parsed,
                    dict,
                ):
                    return normalize_resume(
                        ResumeAnalysis.model_validate(
                            response.parsed
                        )
                    )

            if response.text:

                data = json.loads(
                    response.text
                )

                return normalize_resume(
                    ResumeAnalysis.model_validate(
                        data
                    )
                )

            raise ValueError(
                "Gemini returned an empty response"
            )

        except Exception as exc:

            last_error = exc

            print(
                f"Gemini attempt {attempt + 1} failed: "
                f"{type(exc).__name__}: {exc}"
            )

            if attempt < 2:
                time.sleep(2 ** attempt)

            else:
                raise last_error