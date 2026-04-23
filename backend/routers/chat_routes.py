from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()

class ChatRequest(BaseModel):
    message: str
    results: dict  # resume analysis result

@router.post("/chat")
def chat_bot(data: ChatRequest):

    msg = data.message.lower()
    result = data.results

    matched = result.get("matched_skills", [])
    missing = result.get("missing_skills", [])
    score = result.get("match_score", 0)

    # 🔥 Simple smart responses
    if "improve" in msg:
        return {
            "reply": f"You can improve by learning: {', '.join(missing) or 'advanced topics'}."
        }

    elif "skills" in msg:
        return {
            "reply": f"You already have: {', '.join(matched)}. Missing: {', '.join(missing)}."
        }

    elif "score" in msg:
        return {
            "reply": f"Your score is {score}%. Add missing skills to increase it."
        }

    else:
        return {
            "reply": "Try asking about skills, score, or improvements 🚀"
        }