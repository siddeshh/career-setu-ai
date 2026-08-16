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

Analyze the resume text provided below.

Extract ONLY information explicitly supported by the resume.

DO NOT:
- invent information
- invent companies
- invent job titles
- invent experience
- invent skills
- invent certifications
- invent dates
- invent achievements
- invent education

If information is missing, return null or an empty list.

Normalize different resume section names.

Examples:
- Technical Expertise -> skills
- Core Competencies -> skills
- Professional Profile -> summary
- Career Objective -> summary
- Work History -> experience
- Professional Experience -> experience
- Selected Projects -> projects
- Academic Projects -> projects
- Certificates -> certifications
- Honors -> achievements

Return the result using the provided ResumeAnalysis schema.

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