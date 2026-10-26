import re
from functools import lru_cache

SKILL_ALIASES = {
    "c++": ["c++", "cpp"], "javascript": ["javascript", "js"],
    "typescript": ["typescript", "ts"], "machine learning": ["machine learning", "ml"],
    "natural language processing": ["natural language processing", "nlp"],
    "scikit-learn": ["scikit-learn", "sklearn"], "node.js": ["node.js", "nodejs", "node js"],
    "postgresql": ["postgresql", "postgres"], "amazon web services": ["amazon web services", "aws"],
    "rest api": ["rest api", "restful api", "rest apis"],
}
SKILLS = sorted(set(SKILL_ALIASES) | {
    "python","java","c","c++","sql","fastapi","flask","django","react","html","css",
    "typescript","javascript","node.js","express","git","docker","kubernetes","aws",
    "azure","gcp","postgresql","mysql","mongodb","sqlite","redis","linux","pandas",
    "numpy","scikit-learn","tensorflow","pytorch","machine learning","deep learning",
    "natural language processing","data analysis","power bi","tableau","communication",
    "agile","spring boot","rest api","graphql","testing","pytest","data structures",
    "algorithms","computer vision"
}, key=str.lower)

def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", text.lower()).strip()

def extract_skills(text: str) -> list[str]:
    low = normalize(text)
    found = []
    for canonical in SKILLS:
        aliases = SKILL_ALIASES.get(canonical, [canonical])
        if any(re.search(r"(?<![a-z0-9+#.])" + re.escape(alias) + r"(?![a-z0-9+#.])", low) for alias in aliases):
            found.append(canonical)
    return sorted(set(found))

@lru_cache(maxsize=1)
def _model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def relevance_score(resume_text: str, job_text: str, use_model: bool = True) -> tuple[float, str]:
    if use_model:
        try:
            import numpy as np
            model = _model()
            vecs = model.encode([resume_text[:12000], job_text[:6000]], normalize_embeddings=True)
            score = float(np.dot(vecs[0], vecs[1]))
            return max(0.0, min(1.0, score)), "sentence-transformers"
        except Exception:
            pass
    # Explainable fallback: overlap of meaningful job terms in resume.
    stop = {"the","and","for","with","that","this","you","are","our","will","from","have","has","job","role","work","years","experience","required"}
    terms = set(re.findall(r"[a-z][a-z0-9+#.-]{2,}", normalize(job_text))) - stop
    if not terms:
        return 0.0, "lexical"
    resume_terms = set(re.findall(r"[a-z][a-z0-9+#.-]{2,}", normalize(resume_text)))
    return len(terms & resume_terms) / len(terms), "lexical"

def find_experience(text: str):
    patterns = [r"(\d+(?:\.\d+)?)\s*\+?\s*years?\s+(?:of\s+)?(?:professional\s+)?experience",
                r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*years?"]
    for pattern in patterns:
        m = re.search(pattern, text.lower())
        if m:
            try: return float(m.group(1))
            except ValueError: pass
    return None

def excerpt_for(text: str, term: str) -> str:
    low, target = text.lower(), term.lower()
    idx = low.find(target)
    if idx < 0: return ""
    return text[max(0, idx-100):min(len(text), idx+len(term)+140)].replace("\n", " ").strip()

def score_resume(resume_text: str, job, use_model: bool = True) -> dict:
    skills = extract_skills(resume_text)
    low = normalize(resume_text)
    required = [s.strip().lower() for s in (job.required_skills or []) if s.strip()]
    preferred = [s.strip().lower() for s in (job.preferred_skills or []) if s.strip()]
    matched_req = [s for s in required if s in skills or (s in SKILL_ALIASES and any(a in low for a in SKILL_ALIASES[s]))]
    matched_pref = [s for s in preferred if s in skills or (s in SKILL_ALIASES and any(a in low for a in SKILL_ALIASES[s]))]
    req_cov = len(matched_req)/len(required) if required else 1.0
    pref_cov = len(matched_pref)/len(preferred) if preferred else 1.0
    job_text = " ".join([job.title, job.description, job.responsibilities or "", " ".join(required), " ".join(preferred)])
    relevance, method = relevance_score(resume_text, job_text, use_model)
    exp = find_experience(resume_text)
    if job.min_experience <= 0:
        exp_score = 1.0
    elif exp is None:
        exp_score = 0.0
    else:
        exp_score = min(1.0, exp / job.min_experience)
    weights = job.weights or {"required":45,"preferred":20,"relevance":25,"experience":10}
    total_weight = sum(max(0, float(weights.get(k, 0))) for k in ("required","preferred","relevance","experience")) or 100
    score = 100 * sum(max(0, float(weights.get(k, 0))) * v for k,v in [
        ("required",req_cov),("preferred",pref_cov),("relevance",relevance),("experience",exp_score)
    ]) / total_weight
    terms = list(dict.fromkeys(required + preferred))
    evidence = {term: excerpt_for(resume_text, term) for term in terms}
    return {"score": round(score, 2), "breakdown": {"required":round(req_cov*100,2),"preferred":round(pref_cov*100,2),"relevance":round(relevance*100,2),"experience":round(exp_score*100,2)},
            "matched_required":matched_req,"missing_required":[s for s in required if s not in matched_req],
            "matched_preferred":matched_pref,"missing_preferred":[s for s in preferred if s not in matched_pref],
            "evidence":evidence,"skills":skills,"experience_years":exp,"relevance_method":method}
