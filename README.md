# TalentSort AI
An educational, locally runnable resume-screening and candidate-review system. It uses evidence-based skill matching, optional Sentence Transformers semantic similarity, and SQLite persistence. It is a decision-support tool only: recruiters must review candidates and make all hiring decisions.

## Features
- React + TypeScript + Vite frontend
- FastAPI REST backend with Swagger docs
- SQLite + SQLAlchemy persistence
- PDF/DOCX text extraction, duplicate detection, file-size/type validation
- Skill normalization, configurable weighted scoring, evidence excerpts
- Candidate ranking, decisions, notes, screening history
- pytest backend tests and synthetic demo data

## Requirements
- Python 3.10+
- Node.js 20+ and npm
- Windows 10/11, macOS, or Linux

## Windows PowerShell: run locally
Extract the ZIP, then open the `TalentSort-AI` folder in VS Code.

### Backend
```powershell
cd backend
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item ..\.env.example .env
python -m app.database.init_db
uvicorn app.main:app --reload
```
Backend: http://127.0.0.1:8000  
API docs: http://127.0.0.1:8000/docs

The first semantic screening run may download the public `all-MiniLM-L6-v2` model. If it is unavailable, the engine automatically uses a transparent lexical fallback. No paid API key is required.

### Frontend (open a second terminal)
```powershell
cd frontend
npm install
Copy-Item .env.example .env
npm run dev
```
Open the Vite URL shown in the terminal (normally http://localhost:5173).

### Tests and production build
```powershell
cd backend
.\.venv\Scripts\Activate.ps1
pytest
```
In another terminal:
```powershell
cd frontend
npm run build
```

## Demo data
After starting the backend, create a job in the UI and upload one or more PDF/DOCX resumes. Synthetic examples are in `backend/sample_data/`. You can also load demo data:
```powershell
cd backend
python -m app.database.seed_demo
```

## Environment
See `.env.example`. Defaults are designed for local use. Set a strong `SECRET_KEY` and restrict `CORS_ORIGINS` before exposing the app publicly.

## GitHub
From the project root:
```powershell
git init
git add .
git commit -m "Initial TalentSort AI project"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/TalentSort-AI.git
git push -u origin main
```

## Deployment notes
The frontend can be deployed to Vercel or Netlify after setting `VITE_API_BASE_URL` to the deployed API URL. Deploy the FastAPI backend to a Python-capable host (for example Render or Railway) and configure environment variables. For durable production storage, use PostgreSQL via `DATABASE_URL`; local SQLite files are not suitable for many ephemeral hosting environments. Configure CORS to the exact frontend origin.

## Scoring formula
Default score = 45% required-skill coverage + 20% preferred-skill coverage + 25% semantic/lexical relevance + 10% experience evidence. The score is a match indicator for the provided job description, not a probability of job success. A missing skill means the resume did not provide evidence; it does not prove the candidate lacks that skill.

## Important limitations
- Scanned/image-only PDFs are reported as unreadable if no text can be extracted; OCR is not bundled.
- Experience extraction is heuristic and should be verified by a recruiter.
- Authentication UI is a local demo boundary, not production-grade identity management. Do not expose publicly without adding real authentication, authorization, rate limiting, malware scanning, retention controls, and privacy/legal review.
- Hiring decisions can have significant consequences. Use job-relevant evidence only, provide human review and accommodations, and audit the system for disparate impact before real use.
