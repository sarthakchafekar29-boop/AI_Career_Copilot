
import os
import json
import time

from google import genai
from google.genai import types


# Get Gemini API key from environment variables
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise RuntimeError(
        "GEMINI_API_KEY is missing. Add it in Render Environment settings."
    )

# Initialize Gemini client
client = genai.Client(api_key=API_KEY)

# Model name
MODEL_NAME = "gemini-3.6-flash"


def analyze_resume(resume_text, user_goal):
    """
    Analyze a resume according to the user's career goal.

    Returns a dictionary containing:
    skills, missing_skills, roadmap, interview_questions.
    """

    prompt = f"""
You are a senior software engineer, career advisor,
and hiring manager.

Analyze the resume based on the user's career goal.

USER CAREER GOAL:
{user_goal}

RESUME:
{resume_text[:12000]}

INSTRUCTIONS:
1. Extract skills relevant to the career goal.
2. Identify important missing skills.
3. Create a practical learning roadmap in steps.
4. Generate useful interview questions.
5. Do not invent qualifications or experience.
6. Keep the answer clear and concise.
7. Return only valid JSON.

REQUIRED JSON FORMAT:
{{
    "skills": [],
    "missing_skills": [],
    "roadmap": [],
    "interview_questions": []
}}

All four fields must contain arrays of strings.
"""

    for attempt in range(3):
        try:
            response = client.models.generate_content(
                model=MODEL_NAME,
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    temperature=0.2,
                    max_output_tokens=1500,
                ),
            )

            if not response.text:
                raise ValueError("Gemini returned an empty response.")

            result = json.loads(response.text)

            # Validate the expected response fields
            required_fields = [
                "skills",
                "missing_skills",
                "roadmap",
                "interview_questions",
            ]

            for field in required_fields:
                if not isinstance(result.get(field), list):
                    result[field] = []

            # Ensure each field contains strings only
            for field in required_fields:
                result[field] = [
                    str(item) for item in result[field]
                ]

            return result

        except Exception as error:
            error_text = str(error)
            error_type = type(error).__name__

            # Retry temporary Gemini server errors
            is_temporary_error = (
                "503" in error_text
                or "UNAVAILABLE" in error_text.upper()
                or "429" in error_text
                or "RESOURCE_EXHAUSTED" in error_text.upper()
            )

            if is_temporary_error and attempt < 2:
                wait_seconds = 2 ** (attempt + 1)
                print(
                    f"Gemini temporarily unavailable. "
                    f"Retry {attempt + 1}/2 in {wait_seconds} seconds."
                )
                time.sleep(wait_seconds)
                continue

            # Log the error without exposing the API key
            print(
                f"Resume analysis failed: "
                f"{error_type}: {error_text}"
            )

            return {
                "skills": [],
                "missing_skills": [],
                "roadmap": [],
                "interview_questions": [],
                "error": (
                    "Resume analysis is temporarily unavailable. "
                    "Please try again later."
                ),
            }

    # Fallback if all retry attempts fail
    return {
        "skills": [],
        "missing_skills": [],
        "roadmap": [],
        "interview_questions": [],
        "error": "Unable to analyze the resume. Please try again.",
    }
