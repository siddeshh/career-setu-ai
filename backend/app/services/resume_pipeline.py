from app.schemas.resume_analysis import ResumeAnalysis

from app.services.resume_analyzer import (
    analyze_resume_text,
)

from app.services.llm.resume_llm import (
    analyze_resume_with_llm,
)


def analyze_resume(
    resume_text: str,
) -> ResumeAnalysis:
    """
    Main resume analysis pipeline.

    Gemini is preferred when available.
    Rule-based analysis is used as fallback.
    """

    try:
        print(
            "Starting LLM resume analysis..."
        )

        return analyze_resume_with_llm(
            resume_text
        )

    except Exception as llm_error:

        print(
            "LLM analysis failed:"
        )

        print(llm_error)

        print(
            "Using rule-based "
            "resume analyzer..."
        )

        return analyze_resume_text(
            resume_text
        )