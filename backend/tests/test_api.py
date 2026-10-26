import os, tempfile
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
from app.main import app
from app.database.session import Base, get_db

engine = create_engine("sqlite://", connect_args={"check_same_thread":False}, poolclass=StaticPool)
TestingSession = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base.metadata.create_all(engine)
def override_db():
    db = TestingSession()
    try: yield db
    finally: db.close()
app.dependency_overrides[get_db] = override_db
client = TestClient(app)

def test_health_and_job_crud():
    assert client.get("/api/health").json()["status"] == "ok"
    response = client.post("/api/jobs", json={"title":"QA Engineer","description":"Test web applications and APIs","required_skills":["python"],"preferred_skills":["pytest"]})
    assert response.status_code == 201
    job = response.json()
    assert job["title"] == "QA Engineer"
    assert client.get(f"/api/jobs/{job['id']}").status_code == 200
