from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException
from sqlalchemy.orm import Session
import shutil
import os
import uuid

from typing import List
from pydantic import BaseModel

from services.text_extraction import extract_text_from_pdf, extract_text_from_docx
from services.nlp_processing import preprocess_text, extract_skills
from services.report_generator import generate_pdf

from fastapi.responses import FileResponse

from database import get_db
from models import MatchHistory

router = APIRouter()

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


# ================================
# ✅ Pydantic Model
# ================================
class ReportItem(BaseModel):
    name: str
    match_score: float
    classification: str
    matched_skills: List[str]
    missing_skills: List[str]


# ================================
# Save File
# ================================
def save_file(upload_file: UploadFile):
    unique_name = f"{uuid.uuid4()}_{upload_file.filename}"
    file_path = os.path.join(UPLOAD_FOLDER, unique_name)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(upload_file.file, buffer)

    return file_path


# ================================
# Extract Text
# ================================
def extract_text(file_path: str):
    if file_path.endswith(".pdf"):
        return extract_text_from_pdf(file_path)
    elif file_path.endswith(".docx"):
        return extract_text_from_docx(file_path)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type")


# ================================
# 🔥 GENERATE SUGGESTIONS (NEW)
# ================================
def generate_suggestions(score, missing_skills):
    suggestions = []

    if missing_skills:
        suggestions.append(f"Learn these skills: {', '.join(missing_skills)}")

    if score < 40:
        suggestions.append("Your resume is weak. Add strong projects and core skills.")
    elif score < 70:
        suggestions.append("Improve by adding more job-relevant keywords and experience.")
    else:
        suggestions.append("Great match! Add achievements to stand out further.")

    return suggestions


# ================================
# MATCH SINGLE RESUME
# ================================
@router.post("/match-resume")
async def match_resume(
    resume_file: UploadFile = File(...),
    job_description: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        file_path = save_file(resume_file)
        resume_text = extract_text(file_path)

        resume_clean = preprocess_text(resume_text)
        jd_clean = preprocess_text(job_description)

        resume_skills = list(set([s.lower() for s in extract_skills(resume_clean)]))
        jd_skills = list(set([s.lower() for s in extract_skills(jd_clean)]))

        matched_skills = list(set(resume_skills) & set(jd_skills))
        missing_skills = list(set(jd_skills) - set(resume_skills))

        score = round((len(matched_skills) / len(jd_skills)) * 100, 2) if jd_skills else 0

        if score >= 70:
            label = "Suitable"
        elif score >= 40:
            label = "Moderate"
        else:
            label = "Not Suitable"

        # 🔥 Suggestions
        suggestions = generate_suggestions(score, missing_skills)

        # Save to DB
        new_record = MatchHistory(
            resume_filename=resume_file.filename,
            resume_skills=", ".join(resume_skills),
            jd_skills=", ".join(jd_skills),
            match_score=score,
            classification=label
        )

        db.add(new_record)
        db.commit()

        return {
            "resume_skills": resume_skills,
            "jd_skills": jd_skills,
            "matched_skills": matched_skills,
            "missing_skills": missing_skills,
            "match_score_percent": score,
            "classification": label,
            "suggestions": suggestions  # ✅ FIXED
        }

    except Exception as e:
        print("❌ MATCH ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))


# ================================
# 🔥 MATCH MULTIPLE RESUMES (UPDATED)
# ================================
@router.post("/match-multiple")
async def match_multiple_resumes(
    files: List[UploadFile] = File(...),
    job_description: str = Form(...)
):
    try:
        results = []

        jd_clean = preprocess_text(job_description)
        jd_skills = list(set([s.lower() for s in extract_skills(jd_clean)]))

        for file in files:
            file_path = save_file(file)
            resume_text = extract_text(file_path)

            resume_clean = preprocess_text(resume_text)
            resume_skills = list(set([s.lower() for s in extract_skills(resume_clean)]))

            matched_skills = list(set(resume_skills) & set(jd_skills))
            missing_skills = list(set(jd_skills) - set(resume_skills))

            score = round((len(matched_skills) / len(jd_skills)) * 100, 2) if jd_skills else 0

            if score >= 70:
                label = "Suitable"
            elif score >= 40:
                label = "Moderate"
            else:
                label = "Not Suitable"

            # 🔥 ADD THIS (IMPORTANT FIX)
            suggestions = generate_suggestions(score, missing_skills)

            results.append({
                "name": file.filename,
                "match_score": score,
                "classification": label,
                "matched_skills": matched_skills,
                "missing_skills": missing_skills,
                "suggestions": suggestions  # ✅ FIXED
            })

        results = sorted(results, key=lambda x: x["match_score"], reverse=True)

        return results

    except Exception as e:
        print("❌ MULTI MATCH ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))


# ================================
# 🔥 DOWNLOAD PDF REPORT
# ================================
@router.post("/download-report")
async def download_report(data: dict):
    try:
        company_name = data.get("company_name", "HireSmart AI")
        results = data.get("results", [])

        if not results:
            raise HTTPException(status_code=400, detail="No data provided")

        clean_data = []
        for item in results:
            clean_data.append({
                "name": item.get("name"),
                "match_score": item.get("match_score"),
                "classification": item.get("classification"),
                "matched_skills": item.get("matched_skills", []),
                "missing_skills": item.get("missing_skills", [])
            })

        file_path = generate_pdf(clean_data, company_name)

        if not file_path or not os.path.exists(file_path):
            raise HTTPException(status_code=500, detail="PDF generation failed")

        return FileResponse(
            path=file_path,
            filename="HireSmart_Report.pdf",
            media_type="application/pdf"
        )

    except Exception as e:
        print("❌ PDF ERROR:", e)
        raise HTTPException(status_code=500, detail=str(e))