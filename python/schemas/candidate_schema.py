from pydantic import BaseModel, Field, EmailStr
from typing import List, Optional
from enum import Enum

class QuestionType(str, Enum):
    introductory = "Introductory"
    basic = "Basic"
    technical = "Technical"

class QuestionModel(BaseModel):
    text: str = Field(description = "The exact interview question to ask the candidate directly. Must be an interrogative sentence ending in a question mark. Do NOT output a summary statement.")
    type: QuestionType

class GeminiOutputModel(BaseModel):
    candidate_name: str = Field(description = "The full name of the candidate extracted from the resume")
    candidate_email: EmailStr = Field(description = "The primary email address of the candidate extracted from the resume")
    questions: List[QuestionModel] = Field(
        min_length = 10, 
        max_length = 10, 
        description = "A list of exactly 10 generated interview questions."
    )

class CandidatePrepareRequest(BaseModel):
    resume_text: str
    job_description_text: str

class InterviewResponseModel(BaseModel):
    candidate_name: str
    candidate_email: str
    resume_text: str
    job_description_text: str
    questions: List[QuestionModel]
    meeting_link: str
    event_id: str
    start_time: str
    end_time: str