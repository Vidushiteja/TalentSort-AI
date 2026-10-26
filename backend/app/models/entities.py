from datetime import datetime, timezone
from sqlalchemy import String, Text, Integer, Float, DateTime, ForeignKey, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database.session import Base

def utcnow():
    return datetime.now(timezone.utc)

class Job(Base):
    __tablename__ = "jobs"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    title: Mapped[str] = mapped_column(String(200))
    department: Mapped[str] = mapped_column(String(120), default="")
    description: Mapped[str] = mapped_column(Text)
    responsibilities: Mapped[str] = mapped_column(Text, default="")
    required_skills: Mapped[list] = mapped_column(JSON, default=list)
    preferred_skills: Mapped[list] = mapped_column(JSON, default=list)
    min_experience: Mapped[float] = mapped_column(Float, default=0)
    education: Mapped[str] = mapped_column(String(200), default="")
    certifications: Mapped[list] = mapped_column(JSON, default=list)
    weights: Mapped[dict] = mapped_column(JSON, default=lambda: {"required":45,"preferred":20,"relevance":25,"experience":10})
    archived: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    resumes: Mapped[list["Resume"]] = relationship(back_populates="job", cascade="all, delete-orphan")

class Candidate(Base):
    __tablename__ = "candidates"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(200), default="Unknown candidate")
    email: Mapped[str] = mapped_column(String(320), default="")
    extracted_skills: Mapped[list] = mapped_column(JSON, default=list)
    education_evidence: Mapped[str] = mapped_column(Text, default="")
    experience_years: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    resumes: Mapped[list["Resume"]] = relationship(back_populates="candidate", cascade="all, delete-orphan")

class Resume(Base):
    __tablename__ = "resumes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    filename: Mapped[str] = mapped_column(String(255))
    sha256: Mapped[str] = mapped_column(String(64), index=True)
    extracted_text: Mapped[str] = mapped_column(Text)
    parse_status: Mapped[str] = mapped_column(String(40), default="processed")
    parse_message: Mapped[str] = mapped_column(Text, default="")
    candidate_id: Mapped[int] = mapped_column(ForeignKey("candidates.id"))
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    candidate: Mapped[Candidate] = relationship(back_populates="resumes")
    job: Mapped[Job] = relationship(back_populates="resumes")
    results: Mapped[list["ScreeningResult"]] = relationship(back_populates="resume", cascade="all, delete-orphan")

class ScreeningResult(Base):
    __tablename__ = "screening_results"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"))
    job_id: Mapped[int] = mapped_column(ForeignKey("jobs.id"))
    score: Mapped[float] = mapped_column(Float)
    breakdown: Mapped[dict] = mapped_column(JSON, default=dict)
    matched_required: Mapped[list] = mapped_column(JSON, default=list)
    missing_required: Mapped[list] = mapped_column(JSON, default=list)
    matched_preferred: Mapped[list] = mapped_column(JSON, default=list)
    missing_preferred: Mapped[list] = mapped_column(JSON, default=list)
    evidence: Mapped[dict] = mapped_column(JSON, default=dict)
    relevance_method: Mapped[str] = mapped_column(String(40), default="lexical")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    resume: Mapped[Resume] = relationship(back_populates="results")

class DecisionHistory(Base):
    __tablename__ = "decision_history"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"))
    decision: Mapped[str] = mapped_column(String(40))
    note: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

class RecruiterNote(Base):
    __tablename__ = "recruiter_notes"
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    resume_id: Mapped[int] = mapped_column(ForeignKey("resumes.id"))
    note: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
