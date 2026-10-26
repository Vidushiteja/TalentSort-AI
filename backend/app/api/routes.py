import hashlib, re
from fastapi import APIRouter, Depends, File, UploadFile, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database.session import get_db
from app.models import Job, Candidate, Resume, ScreeningResult, DecisionHistory, RecruiterNote
from app.schemas.api import JobCreate, JobOut, DecisionIn, NoteIn
from app.services.resume_parser import extract_text
from app.services.screening import score_resume, extract_skills, find_experience
from app.config import settings

router = APIRouter()

def result_dict(r, resume=None, db=None):
    resume = resume or r.resume
    return {"id": r.id, "resume_id": r.resume_id, "job_id": r.job_id, "candidate_id": resume.candidate_id,
        "candidate_name": resume.candidate.name, "filename": resume.filename, "score": r.score,
        "breakdown": r.breakdown, "matched_required": r.matched_required, "missing_required": r.missing_required,
        "matched_preferred": r.matched_preferred, "missing_preferred": r.missing_preferred,
        "evidence": r.evidence, "relevance_method": r.relevance_method, "created_at": r.created_at.isoformat(),
        "decision": latest_decision(resume.id)}

def latest_decision(resume_id, db=None):
    if db is None: return "Needs Review"
    row = db.query(DecisionHistory).filter_by(resume_id=resume_id).order_by(desc(DecisionHistory.id)).first()
    return row.decision if row else "Needs Review"

@router.get("/health")
def health():
    return {"status":"ok", "service":"TalentSort AI"}

@router.post("/jobs", response_model=JobOut, status_code=201)
def create_job(payload: JobCreate, db: Session = Depends(get_db)):
    job = Job(**payload.model_dump())
    db.add(job); db.commit(); db.refresh(job)
    return job

@router.get("/jobs", response_model=list[JobOut])
def list_jobs(include_archived: bool = False, db: Session = Depends(get_db)):
    q = db.query(Job)
    if not include_archived: q = q.filter_by(archived=False)
    return q.order_by(desc(Job.created_at)).all()

@router.get("/jobs/{job_id}", response_model=JobOut)
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job: raise HTTPException(404, "Job not found")
    return job

@router.put("/jobs/{job_id}", response_model=JobOut)
def update_job(job_id: int, payload: JobCreate, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job: raise HTTPException(404, "Job not found")
    for key, value in payload.model_dump().items(): setattr(job, key, value)
    db.commit(); db.refresh(job); return job

@router.patch("/jobs/{job_id}/archive")
def archive_job(job_id: int, archived: bool = True, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job: raise HTTPException(404, "Job not found")
    job.archived = archived; db.commit()
    return {"id":job_id,"archived":archived}

@router.delete("/jobs/{job_id}")
def delete_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job: raise HTTPException(404, "Job not found")
    db.delete(job); db.commit(); return {"deleted":True}

@router.post("/jobs/{job_id}/resumes", status_code=201)
async def upload_resumes(job_id: int, files: list[UploadFile] = File(...), db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job: raise HTTPException(404, "Job not found")
    output = []
    for file in files:
        filename = (file.filename or "resume").replace("\\", "/").split("/")[-1]
        if not filename.lower().endswith((".pdf", ".docx")):
            output.append({"filename":filename,"status":"failed","error":"Only PDF and DOCX files are supported."}); continue
        data = await file.read()
        if len(data) > settings.max_upload_mb * 1024 * 1024:
            output.append({"filename":filename,"status":"failed","error":f"File exceeds {settings.max_upload_mb} MB limit."}); continue
        digest = hashlib.sha256(data).hexdigest()
        duplicate = db.query(Resume).filter_by(sha256=digest, job_id=job_id).first()
        if duplicate:
            output.append({"filename":filename,"status":"duplicate","resume_id":duplicate.id}); continue
        try:
            text = extract_text(filename, data)
        except ValueError as exc:
            output.append({"filename":filename,"status":"failed","error":str(exc)}); continue
        email_match = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.I)
        name = next((line.strip() for line in text.splitlines() if len(line.strip()) > 2 and "@" not in line and len(line.strip()) < 80), "Unknown candidate")
        candidate = Candidate(name=name, email=email_match.group(0) if email_match else "", extracted_skills=extract_skills(text),
                               education_evidence="\n".join(line for line in text.splitlines() if any(w in line.lower() for w in ["bachelor","master","b.tech","btech","degree","university","college","education"]))[:2000],
                               experience_years=find_experience(text))
        db.add(candidate); db.flush()
        resume = Resume(filename=filename, sha256=digest, extracted_text=text, candidate_id=candidate.id, job_id=job_id)
        db.add(resume); db.flush()
        scored = score_resume(text, job, settings.use_semantic_model)
        result = ScreeningResult(resume_id=resume.id, job_id=job_id, score=scored["score"], breakdown=scored["breakdown"],
            matched_required=scored["matched_required"], missing_required=scored["missing_required"],
            matched_preferred=scored["matched_preferred"], missing_preferred=scored["missing_preferred"],
            evidence=scored["evidence"], relevance_method=scored["relevance_method"])
        db.add(result); db.commit()
        output.append({"filename":filename,"status":"processed","resume_id":resume.id,"candidate_id":candidate.id,"score":scored["score"],"relevance_method":scored["relevance_method"]})
    return {"results":output}

@router.get("/jobs/{job_id}/results")
def job_results(job_id: int, search: str = "", decision: str = "", sort: str = "score", order: str = "desc",
                page: int = Query(1, ge=1), page_size: int = Query(20, ge=1, le=100), db: Session = Depends(get_db)):
    if not db.get(Job, job_id): raise HTTPException(404, "Job not found")
    rows = db.query(ScreeningResult).filter_by(job_id=job_id).all()
    results = [result_dict(r, db=db) for r in rows]
    if search:
        needle = search.lower()
        results = [r for r in results if needle in r["candidate_name"].lower() or needle in r["filename"].lower()]
    if decision: results = [r for r in results if r["decision"] == decision]
    sort_key = sort if sort in {"score","candidate_name","created_at"} else "score"
    results.sort(key=lambda r: (r.get(sort_key) or ""), reverse=(order.lower() != "asc"))
    total = len(results); start = (page-1)*page_size
    return {"items":results[start:start+page_size],"total":total,"page":page,"page_size":page_size}

@router.get("/results/{result_id}")
def get_result(result_id: int, db: Session = Depends(get_db)):
    r = db.get(ScreeningResult, result_id)
    if not r: raise HTTPException(404, "Screening result not found")
    return result_dict(r, db=db)

@router.post("/results/{result_id}/rescreen")
def rescreen(result_id: int, db: Session = Depends(get_db)):
    r = db.get(ScreeningResult, result_id)
    if not r: raise HTTPException(404, "Screening result not found")
    scored = score_resume(r.resume.extracted_text, r.resume.job, settings.use_semantic_model)
    for key, attr in [("score","score"),("breakdown","breakdown"),("matched_required","matched_required"),("missing_required","missing_required"),("matched_preferred","matched_preferred"),("missing_preferred","missing_preferred"),("evidence","evidence"),("relevance_method","relevance_method")]:
        setattr(r, attr, scored[key])
    db.commit(); db.refresh(r); return result_dict(r, db=db)

@router.patch("/resumes/{resume_id}/decision")
def set_decision(resume_id: int, payload: DecisionIn, db: Session = Depends(get_db)):
    if payload.decision not in {"Shortlisted","Needs Review","Not Selected"}:
        raise HTTPException(422, "Decision must be Shortlisted, Needs Review, or Not Selected")
    if not db.get(Resume, resume_id): raise HTTPException(404, "Resume not found")
    row = DecisionHistory(resume_id=resume_id, decision=payload.decision, note=payload.note)
    db.add(row); db.commit()
    return {"resume_id":resume_id,"decision":payload.decision,"saved":True}

@router.post("/resumes/{resume_id}/notes", status_code=201)
def add_note(resume_id: int, payload: NoteIn, db: Session = Depends(get_db)):
    if not db.get(Resume, resume_id): raise HTTPException(404, "Resume not found")
    note = RecruiterNote(resume_id=resume_id, note=payload.note)
    db.add(note); db.commit(); db.refresh(note)
    return {"id":note.id,"resume_id":resume_id,"note":note.note,"created_at":note.created_at.isoformat()}

@router.get("/resumes/{resume_id}/notes")
def get_notes(resume_id: int, db: Session = Depends(get_db)):
    if not db.get(Resume, resume_id): raise HTTPException(404, "Resume not found")
    return [{"id":n.id,"note":n.note,"created_at":n.created_at.isoformat()} for n in db.query(RecruiterNote).filter_by(resume_id=resume_id).order_by(desc(RecruiterNote.id)).all()]

@router.get("/resumes/{resume_id}/history")
def resume_history(resume_id: int, db: Session = Depends(get_db)):
    if not db.get(Resume, resume_id): raise HTTPException(404, "Resume not found")
    return [{"id":d.id,"decision":d.decision,"note":d.note,"created_at":d.created_at.isoformat()} for d in db.query(DecisionHistory).filter_by(resume_id=resume_id).order_by(desc(DecisionHistory.id)).all()]

@router.get("/jobs/{job_id}/compare")
def compare_candidates(job_id: int, ids: str, db: Session = Depends(get_db)):
    if not db.get(Job, job_id): raise HTTPException(404, "Job not found")
    try: selected = [int(x) for x in ids.split(",") if x.strip()][:4]
    except ValueError: raise HTTPException(422, "ids must be comma-separated result IDs")
    rows = db.query(ScreeningResult).filter(ScreeningResult.job_id == job_id, ScreeningResult.id.in_(selected)).all()
    return [result_dict(r, db=db) for r in rows]

@router.get("/dashboard")
def dashboard(db: Session = Depends(get_db)):
    jobs = db.query(Job).filter_by(archived=False).count()
    candidates = db.query(Candidate).count()
    results = db.query(ScreeningResult).all()
    decisions = [latest_decision(r.resume_id, db) for r in results]
    return {"active_jobs":jobs,"total_candidates":candidates,"analyzed":len(results),
            "awaiting_review":decisions.count("Needs Review"),"shortlisted":decisions.count("Shortlisted"),
            "recent_activity":[{"candidate":r.resume.candidate.name,"job":r.resume.job.title,"score":r.score,"created_at":r.created_at.isoformat()} for r in sorted(results,key=lambda x:x.id,reverse=True)[:6]]}

@router.delete("/resumes/{resume_id}")
def delete_resume(resume_id: int, db: Session = Depends(get_db)):
    resume = db.get(Resume, resume_id)
    if not resume: raise HTTPException(404, "Resume not found")
    candidate_id = resume.candidate_id
    db.delete(resume); db.commit()
    candidate = db.get(Candidate, candidate_id)
    if candidate and not candidate.resumes:
        db.delete(candidate); db.commit()
    return {"deleted":True}
