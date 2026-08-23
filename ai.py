import os
from dotenv import load_dotenv
import google.generativeai as genai
import json

load_dotenv()
print(os.getenv("GEMINI_API_KEY"))

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-3.6-flash")


def analyze_resume(resume_text, user_goal):
    prompt = f"""
You are a senior software engineer and hiring manager.

Evaluate the resume based on the user's career goal.

User Goal:
{user_goal}

Resume:
{resume_text}

Instructions:
- Extract only skills relevant to the user's goal.
- Ignore unrelated technologies.
- Identify missing skills.
- Create a learning roadmap.
- Generate interview questions.
- Respond ONLY with valid JSON.

Required JSON format:

{{
    "skills": [],
    "missing_skills": [],
    "roadmap": [],
    "interview_questions": []
}}
"""

    try:
        response = model.generate_content(prompt)

        content = response.text.strip()

        # Remove markdown if Gemini wraps JSON in ```json
        content = content.replace("```json", "").replace("```", "").strip()

        return json.loads(content)

    except Exception as e:
        return {
            "skills": [],
            "missing_skills": [],
            "roadmap": [],
            "interview_questions": [],
            "error": str(e)
        }