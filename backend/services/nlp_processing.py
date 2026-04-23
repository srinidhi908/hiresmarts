import spacy

# load model once (fast)
nlp = spacy.load("en_core_web_sm")


# simple skill list (you can expand later)
SKILLS_DB = [
    "python", "java", "c++", "sql", "mysql", "postgresql",
    "machine learning", "deep learning", "data science",
    "flask", "django", "fastapi", "react", "html", "css",
    "javascript", "aws", "docker", "git", "testing"
]


def preprocess_text(text: str):
    doc = nlp(text.lower())
    tokens = [token.text for token in doc if not token.is_stop and token.is_alpha]
    return " ".join(tokens)


def extract_skills(text: str):
    text_lower = text.lower()
    found_skills = []

    for skill in SKILLS_DB:
        if skill in text_lower:
            found_skills.append(skill)

    return list(set(found_skills))
