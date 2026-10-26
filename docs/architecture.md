# Architecture and data flow

1. Recruiter creates a job with required/preferred skills and a job description.
2. Browser sends PDF/DOCX files to FastAPI.
3. Backend validates extension and size, hashes bytes for duplicate detection, and extracts text.
4. Skill extraction normalizes known aliases; optional Sentence Transformers embedding similarity compares resume and job text. If model loading fails or is disabled, lexical overlap is used.
5. Weighted components are persisted in SQLite with matched/missing skill evidence and excerpts.
6. Recruiter filters results, inspects evidence, adds notes, and saves a decision. No automated hiring decision is made.

## Core entities
- Job has many Resumes and screening results.
- Candidate has resume metadata and extracted qualification evidence.
- Resume is scoped to a job and has one or more screening results over time.
- DecisionHistory records each recruiter decision.
- RecruiterNote stores review notes.

## Security before production
Add real user authentication and tenant isolation, authorization on every object, CSRF protections if cookie auth is used, request rate limits, antivirus/malware scanning, secure file storage, deletion/retention policies, database migrations, monitoring, and a legal/privacy review.
