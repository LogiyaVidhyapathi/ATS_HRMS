from fastapi import APIRouter, UploadFile, File, HTTPException, status
from fastapi.responses import RedirectResponse
from datetime import datetime, timedelta
from app.services.interviewer_scheduler import schedule_interview
from app.services.gemini_service import generate_interview_questions
from app.utils.file_parser import extract_text_from_file
from app.schemas.candidate_schema import InterviewResponseModel
 
router = APIRouter()
 
@router.post("/start-interview", response_model = InterviewResponseModel)
 
async def start_interview(
    resume_file: UploadFile = File(...),
    jd_file: UploadFile = File(...)
):
   
    """
    Full AI Interview Pipeline:
    1. Parses uploaded Resume and Job Description files.
    2. Gemini extracts candidate name, email and generates 10 interview questions.
    3. Schedules a Microsoft Teams meeting for the extracted candidate email.
    4. Returns the complete response including meeting link and questions.
    """
 
    try:
        # Step 1: Extract raw text from Uploaded Files
        resume_text = await extract_text_from_file(resume_file)
        jd_text = await extract_text_from_file(jd_file)
 
        # Step 2: Gemini extracts candidate name, email, and generate questions
        gemini_output = await generate_interview_questions(
            resume_text = resume_text,
            jd_text = jd_text
        )
 
        print(f"Gemini extracted - Name: {gemini_output.candidate_name}, Email: {gemini_output.candidate_email}")
 
        # Step 3: Use the dynamically extracted email to schedule the Teams meeting
        start_time = datetime.utcnow() + timedelta(minutes = 2)
        end_time = start_time + timedelta(minutes = 60)
 
        meeting = schedule_interview(
            candidate_email = str(gemini_output.candidate_email),
            start_time = start_time,
            end_time = end_time
        )
 
        return InterviewResponseModel(
            candidate_name = gemini_output.candidate_name,
            candidate_email = str(gemini_output.candidate_email),
            resume_text = resume_text,
            job_description_text = jd_text,
            questions = gemini_output.questions,
            meeting_link = meeting["meeting_link"],
            event_id = meeting["event_id"],
            start_time = meeting["start_time"],
            end_time = meeting["end_time"]
        )
   
    except Exception as e:
        print(f"Error in start_interview pipeline: {e}")
        raise HTTPException(
            status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail = str(e)
        )
 