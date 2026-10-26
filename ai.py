
import os
import json
import google.generativeai as genai

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise RuntimeError("GEMINI_API_KEY is not set in Render")

genai.configure(api_key=api_key)

model = genai.GenerativeModel(
    model_name="gemini-3.6-flash",
    generation_config={
        "response_mime_type": "application/json",
        "temperature": 0.2,
    },
)


def analyze_resume(resume_text, user_goal):
    prompt = f"""
You are a career advisor and hiring manager.

Analyze the resume for the user's career goal.

Career goal: {user_goal}

Resume:
{resume_text[:12000]}

Return only valid JSON in this format:
{{
    "skills": [],
    "missing_skills": [],
    "roadmap": [],
    "interview_questions": []
}}

Keep the analysis concise and practical.
Use arrays of strings for all four fields.
"""

    try:
        response = model.generate_content(
            prompt,
            request_options={"timeout": 35}
        )

        content = response.text.strip()
        result = json.loads(content)

        # Ensure all expected fields exist
        for field in [
            "skills",
            "missing_skills",
            "roadmap",
            "interview_questions",
        ]:
            if field not in result:
                result[field] = []

        return result

    except Exception as e:
        # Keep the full error in Render logs, not the user's page
        print(f"Resume analysis failed: {type(e).__name__}: {e}")

        return {
            "skills": [],
            "missing_skills": [],
            "roadmap": [],
            "interview_questions": [],
            "error": "Resume analysis failed. Please try again."
        }
