import os
import json
from google import genai
from google.genai import types

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is missing")

client = genai.Client(api_key=api_key)


def analyze_resume(resume_text, user_goal):
    prompt = f"""
Analyze this resume for the career goal below.

Career goal: {user_goal}

Resume:
{resume_text[:12000]}

Return JSON with exactly these fields:
{{
  "skills": [],
  "missing_skills": [],
  "roadmap": [],
  "interview_questions": []
}}

All values must be arrays of strings.
Keep the response concise and practical.
"""

    try:
        response = client.models.generate_content(
            model="gemini-3.6-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                temperature=0.2,
                max_output_tokens=1500,
            ),
        )

        if not response.text:
            raise ValueError("Gemini returned an empty response")

        result = json.loads(response.text)

        for field in (
            "skills",
            "missing_skills",
            "roadmap",
            "interview_questions",
        ):
            if not isinstance(result.get(field), list):
                result[field] = []

        return result

    except Exception as e:
        print(f"Resume analysis failed: {type(e).__name__}: {e}")
        return {
            "skills": [],
            "missing_skills": [],
            "roadmap": [],
            "interview_questions": [],
            "error": "Resume analysis failed. Please try again.",
        }

