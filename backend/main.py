from fastapi import FastAPI, UploadFile, File, HTTPException
from pypdf import PdfReader
import os
import json
from pydantic import BaseModel

from services.resume_parser import parse_resume
from services.jd_parser import parse_job_description
from services.matcher import match_resume_with_job
from services.ai_question_generator import generate_interview_questions
from services.answer_evaluator import evaluate_answer


app = FastAPI(
    title="AI Interview Coach",
    description="AI-powered interview preparation platform",
    version="1.0.0"
)


UPLOAD_DIR = "uploads"

if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)


# ==========================================
# HOME
# ==========================================

@app.get("/")
def home():
    return {
        "message": "AI Interview Coach API is running"
    }


# ==========================================
# UPLOAD RESUME
# ==========================================

@app.post("/upload-resume")
async def upload_resume(
    file: UploadFile = File(...)
):

    # Check file type
    if not file.filename.lower().endswith(".pdf"):
        raise HTTPException(
            status_code=400,
            detail="Only PDF files are allowed."
        )

    # Save uploaded resume
    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(file_path, "wb") as buffer:

        content = await file.read()

        buffer.write(content)

    # ======================================
    # Extract text from PDF
    # ======================================

    try:

        reader = PdfReader(file_path)

        text = ""

        for page in reader.pages:

            page_text = page.extract_text()

            if page_text:
                text += page_text + "\n"

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not read resume: {str(e)}"
        )

    # ======================================
    # Parse resume
    # ======================================

    parsed_resume = parse_resume(text)

    # ======================================
    # Save parsed resume
    # ======================================

    resume_data_path = os.path.join(
        UPLOAD_DIR,
        "resume_data.json"
    )

    with open(
        resume_data_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            parsed_resume,
            file,
            indent=4
        )

    return {
        "filename": file_path.split(os.sep)[-1],
        "message": "Resume uploaded successfully",
        "text": text,
        "parsed_resume": parsed_resume
    }


# ==========================================
# UPLOAD JOB DESCRIPTION
# ==========================================

@app.post("/upload-job-description")
async def upload_job_description(
    file: UploadFile = File(...)
):

    # Allowed file types
    allowed_extensions = [
        ".pdf",
        ".txt"
    ]

    extension = os.path.splitext(
        file.filename
    )[1].lower()

    if extension not in allowed_extensions:

        raise HTTPException(
            status_code=400,
            detail="Only PDF and TXT files are allowed."
        )

    # Save JD
    file_path = os.path.join(
        UPLOAD_DIR,
        file.filename
    )

    with open(
        file_path,
        "wb"
    ) as buffer:

        content = await file.read()

        buffer.write(content)

    # ======================================
    # Extract JD text
    # ======================================

    try:

        if extension == ".pdf":

            reader = PdfReader(file_path)

            jd_text = ""

            for page in reader.pages:

                page_text = page.extract_text()

                if page_text:
                    jd_text += page_text + "\n"

        else:

            with open(
                file_path,
                "r",
                encoding="utf-8"
            ) as jd_file:

                jd_text = jd_file.read()

    except Exception as e:

        raise HTTPException(
            status_code=500,
            detail=f"Could not read job description: {str(e)}"
        )

    # ======================================
    # Parse JD
    # ======================================

    parsed_jd = parse_job_description(
        jd_text
    )

    # ======================================
    # Save parsed JD
    # ======================================

    jd_data_path = os.path.join(
        UPLOAD_DIR,
        "jd_data.json"
    )

    with open(
        jd_data_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            parsed_jd,
            file,
            indent=4
        )

    return {
        "filename": file_path.split(os.sep)[-1],
        "message": "Job description uploaded successfully",
        "text": jd_text,
        "parsed_job_description": parsed_jd
    }


# ==========================================
# MATCH RESUME WITH JOB DESCRIPTION
# ==========================================

@app.post("/match-resume")
async def match_resume():

    # ======================================
    # Check resume
    # ======================================

    resume_path = os.path.join(
        UPLOAD_DIR,
        "resume_data.json"
    )

    if not os.path.exists(resume_path):

        raise HTTPException(
            status_code=400,
            detail="Please upload a resume first."
        )

    # ======================================
    # Check JD
    # ======================================

    jd_path = os.path.join(
        UPLOAD_DIR,
        "jd_data.json"
    )

    if not os.path.exists(jd_path):

        raise HTTPException(
            status_code=400,
            detail="Please upload a job description first."
        )

    # ======================================
    # Read resume
    # ======================================

    with open(
        resume_path,
        "r",
        encoding="utf-8"
    ) as file:

        resume = json.load(file)

    # ======================================
    # Read JD
    # ======================================

    with open(
        jd_path,
        "r",
        encoding="utf-8"
    ) as file:

        job_description = json.load(file)

    # ======================================
    # Match
    # ======================================

    result = match_resume_with_job(
        resume,
        job_description
    )

    return {
        "message": "Resume matched with job description",
        "result": result
    }
@app.post("/generate-interview")
async def generate_interview():

    resume_path = os.path.join(
        UPLOAD_DIR,
        "resume_data.json"
    )

    jd_path = os.path.join(
        UPLOAD_DIR,
        "jd_data.json"
    )

    if not os.path.exists(resume_path):
        raise HTTPException(
            status_code=400,
            detail="Please upload a resume first."
        )

    if not os.path.exists(jd_path):
        raise HTTPException(
            status_code=400,
            detail="Please upload a job description first."
        )

    # Read resume
    with open(
        resume_path,
        "r",
        encoding="utf-8"
    ) as file:

        resume = json.load(file)

    # Read job description
    with open(
        jd_path,
        "r",
        encoding="utf-8"
    ) as file:

        job_description = json.load(file)

    # Match resume with JD
    match_result = match_resume_with_job(
        resume,
        job_description
    )

    # Build context for Gemini
    context = {
        "candidate": resume,
        "job": job_description,
        "matching": match_result
    }

    # Generate interview
    questions = generate_interview_questions(
        context
    )

    return {
        "message": "Interview generated successfully",
        "match_result": match_result,
        "interview": questions
    }
# ==========================================
# ANSWER EVALUATION REQUEST
# ==========================================

class AnswerRequest(BaseModel):

    question: str
    answer: str


# ==========================================
# EVALUATE INTERVIEW ANSWER
# ==========================================

@app.post("/evaluate-answer")
async def evaluate_interview_answer(
    request: AnswerRequest
):

    resume_path = os.path.join(
        UPLOAD_DIR,
        "resume_data.json"
    )

    jd_path = os.path.join(
        UPLOAD_DIR,
        "jd_data.json"
    )

    # ======================================
    # Check resume
    # ======================================

    if not os.path.exists(resume_path):

        raise HTTPException(
            status_code=400,
            detail="Please upload a resume first."
        )

    # ======================================
    # Check JD
    # ======================================

    if not os.path.exists(jd_path):

        raise HTTPException(
            status_code=400,
            detail="Please upload a job description first."
        )

    # ======================================
    # Read resume
    # ======================================

    with open(
        resume_path,
        "r",
        encoding="utf-8"
    ) as file:

        resume = json.load(file)

    # ======================================
    # Read JD
    # ======================================

    with open(
        jd_path,
        "r",
        encoding="utf-8"
    ) as file:

        job_description = json.load(file)

    # ======================================
    # Match resume with JD
    # ======================================

    match_result = match_resume_with_job(
        resume,
        job_description
    )

    # ======================================
    # Build context
    # ======================================

    context = {
        "candidate": resume,
        "job": job_description,
        "matching": match_result
    }

    # ======================================
    # Validate answer
    # ======================================

    if not request.answer.strip():

        raise HTTPException(
            status_code=400,
            detail="Answer cannot be empty."
        )

    # ======================================
    # Evaluate answer using Gemini
    # ======================================

    try:

        evaluation = evaluate_answer(
            request.question,
            request.answer,
            context
        )

    except RuntimeError as e:

        raise HTTPException(
            status_code=500,
            detail=str(e)
        )

    # ======================================
    # Return evaluation
    # ======================================

    return {
        "message": "Answer evaluated successfully",
        "evaluation": evaluation
    }