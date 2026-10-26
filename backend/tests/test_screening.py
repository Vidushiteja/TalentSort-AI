from types import SimpleNamespace
from app.services.screening import extract_skills, score_resume, relevance_score
from app.services.resume_parser import extract_text
import pytest

def test_extract_skills_normalizes_aliases():
    assert "python" in extract_skills("Built APIs in Python and used sklearn.")
    assert "scikit-learn" in extract_skills("Built APIs in Python and used sklearn.")

def test_score_explains_missing_evidence():
    job = SimpleNamespace(title="Python Developer", description="Build APIs", responsibilities="",
        required_skills=["python","docker"], preferred_skills=["pytest"], min_experience=2,
        weights={"required":45,"preferred":20,"relevance":25,"experience":10})
    result = score_resume("Python developer with 3 years experience. Built REST APIs.", job, use_model=False)
    assert result["score"] >= 0
    assert "python" in result["matched_required"]
    assert "docker" in result["missing_required"]
    assert result["experience_years"] == 3.0

def test_invalid_file_type():
    with pytest.raises(ValueError):
        extract_text("resume.txt", b"not a resume")

def test_lexical_relevance_is_bounded():
    score, method = relevance_score("Python SQL API", "Python SQL API", use_model=False)
    assert 0 <= score <= 1
    assert method == "lexical"
