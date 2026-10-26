import re

SKILL_SYNONYMS = {
    "Python": ["python", "python3"],
    "SQL": ["sql", "mysql", "postgresql", "sqlite", "database queries"],
    "Git": ["git", "github", "version control"],
    "Communication": ["communication", "communicate", "presentation", "stakeholder"],
    "HTML": ["html", "html5"],
    "CSS": ["css", "css3", "responsive design"],
    "JavaScript": ["javascript", "js", "ecmascript"],
    "Django": ["django"],
    "FastAPI": ["fastapi", "fast api"],
    "Machine Learning": ["machine learning", "scikit-learn", "sklearn", "classification", "regression"],
    "Data Analysis": ["data analysis", "pandas", "data cleaning", "exploratory data analysis", "eda"],
    "UI/UX Design": ["ui/ux", "ui ux", "user experience", "user interface", "wireframe", "prototyping", "figma"],
    "REST APIs": ["rest api", "restful api", "api integration", "http api"],
    "Cloud Computing": ["cloud computing", "openstack", "aws", "azure", "google cloud"],
    "Problem Solving": ["problem solving", "troubleshooting", "debugging", "analytical skills"],
    "Project Management": ["project management", "planning", "milestones", "agile", "scrum"],
    "Excel": ["excel", "spreadsheets", "pivot table"],
    "C++": ["c++", "cpp"],
    "Java": ["java", "core java"],
    "Testing": ["software testing", "unit testing", "pytest", "test cases", "quality assurance"],
}
DEFAULT_SKILLS = list(SKILL_SYNONYMS.keys())

def _sentences(text):
    chunks = re.split(r'(?<=[.!?])\s+|\n+', text)
    return [re.sub(r'\s+', ' ', s).strip() for s in chunks if s.strip()]

def _variants(criterion):
    key = criterion.strip()
    if key in SKILL_SYNONYMS:
        return SKILL_SYNONYMS[key]
    return [key.lower()]

def _contains_term(text, term):
    # Use word boundaries for short/technical terms where possible.
    pattern = r'(?<!\w)' + re.escape(term.lower()) + r'(?!\w)'
    return re.search(pattern, text.lower()) is not None

def analyze_resume(text, criteria, weights=None):
    weights = weights or {}
    sentences = _sentences(text)
    rows = []
    total_weight = 0
    earned_weight = 0
    matched_count = 0
    for criterion in criteria:
        weight = int(weights.get(criterion, 3))
        weight = max(1, min(weight, 5))
        total_weight += weight
        variants = _variants(criterion)
        evidence = []
        matched_terms = []
        for sentence in sentences:
            found = [v for v in variants if _contains_term(sentence, v)]
            if found:
                evidence.append(sentence[:500])
                matched_terms.extend(found)
        matched = bool(evidence)
        if matched:
            matched_count += 1
            earned_weight += weight
        rows.append({
            "Criterion": criterion,
            "Weight (1–5)": weight,
            "Match status": "Evidence found" if matched else "No evidence found",
            "Matched terms": ", ".join(sorted(set(matched_terms))) if matched else "—",
            "Resume evidence": " | ".join(evidence[:3]) if evidence else "No supporting statement located. This does not prove the candidate lacks the skill.",
            "Evidence type": "Explicit text match" if matched else "Not found in extracted text",
        })
    score = round(100 * earned_weight / total_weight) if total_weight else 0
    return {"score": score, "matched_count": matched_count, "total_count": len(criteria), "criteria": rows}
