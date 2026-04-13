import google as genai
from google.genai import Client, types
from app.core.config import settings
from app.schemas.candidate_schema import GeminiOutputModel
import json

client = Client(api_key=settings.GEMINI_API_KEY)

model_name = "gemini-2.0-flash"

prompt = """
    You are an expert technical interviewer conducting a live interview directly with the candidate.

    Task has two parts:
    1. Extract the candidate's full name and primary email address from the provided Resume
    2. Generate EXACTLY 10 interview questions addressed DIRECTLY TO THE CANDIDATE.

    CRITICAL RULE: You must speak exactly as if you are talking to the candidate face-to-face. Use "you" and "your". Do not ever use the candidate's name or refer to them in the third person.

    Structure the 10 questions logically in this exact chronological interview sequence:
    - Question 1 (Introductory): Must be asking the candidate to introduce themselves and walk through their professional background.
    - Question 2 and 3 (Introductory): Ask about their professional strengths, career goals, or general soft skills based on their resume.
    - Question 4 to 10 (Technical): Shift entirely to technical questions evaluating their specific skills, domain knowledge, architectural design capabilities, and problem-solving abilities directly related to the Job Description and their past experience.
"""

async def generate_interview_questions(resume_text: str, jd_text: str) -> GeminiOutputModel:
    """
        Calls Gemini to extract candidate info and generate 10 interview questions.
        Returns a GeminiOutputModel with candidate_name, candidate_email and questions.
    """

    prompt = f"Resume:\n{resume_text}\n\nJob Description:\n{jd_text}"

    response = client.models.generate_content(
        model = model_name, 
        contents = prompt, 
        config = types.GenerateContentConfig(
            system_instruction = prompt, 
            response_mime_type = "application/json", 
            response_schema = GeminiOutputModel
        )
    )

    try:
        # Some Gemini SDK versions pre-parse the response - use it directly

        if hasattr(response, "parsed") and response.parsed is not None:
            parsed = response.parsed
            if isinstance(parsed, GeminiOutputModel):
                return parsed
            if isinstance(parsed, list) and len(parsed) == 1:
                parsed = parsed[0]
            if isinstance(parsed, dict):
                return GeminiOutputModel(**parsed)

        # Fallback: manually parse the raw JSON text
        data = json.loads(response.text)
        print('Gemini raw response type:', type(data).__name__)

        # Gemini sometimes wraps the object in a list - unwrap it
        if isinstance(data, list):
            if len(data) == 0:
                raise ValueError("Gemini returned an empty list - no candidate data found.")
            data = data[0]

        if not isinstance(data, dict):
            raise ValueError(f"Unexpected Gemini response shape ({type(data).__name}): {data}")

        return GeminiOutputModel(**data)

    except (json.JSONDecodeError, ValueError, Exception) as e:
        print("Failed to parse Gemini output:", response.text)
        raise e





       