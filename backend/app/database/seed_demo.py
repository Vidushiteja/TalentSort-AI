from app.database.init_db import init_db
from app.database.session import SessionLocal
from app.models import Job

def seed():
    init_db()
    db = SessionLocal()
    try:
        if db.query(Job).count(): print("Jobs already exist; skipping seed."); return
        db.add(Job(title="Junior Python Backend Developer", department="Engineering",
            description="Build reliable APIs and data services using Python, SQL, and testing.",
            responsibilities="Develop REST APIs, work with databases, write tests, collaborate with a team.",
            required_skills=["python","fastapi","sql","git"], preferred_skills=["docker","pytest","aws"],
            min_experience=0, education="Computer Science or equivalent", certifications=[],
            weights={"required":45,"preferred":20,"relevance":25,"experience":10}))
        db.commit()
        print("Demo job created. Upload resumes through the UI.")
    finally: db.close()

if __name__ == "__main__": seed()
