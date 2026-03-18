from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import httpx
import json
import os

app = FastAPI(title="HuyHaha DL Platform API", version="2.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
async def health():
    return {"status": "healthy"}

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
GRADE_MODEL = "google/gemini-2.0-flash-001"
CHAT_MODEL  = "google/gemini-2.0-flash-001"

class GradingRequest(BaseModel):
    question: str
    student_answer: str
    expected_concepts: List[str]
    max_score: int = 10
    subject: str = ""

class ChatRequest(BaseModel):
    message: str
    history: List[dict] = []
    context: str = ""

class SetKeyRequest(BaseModel):
    api_key: str

async def call_openrouter(messages: list, system: str = "", model: str = GRADE_MODEL) -> str:
    key = OPENROUTER_API_KEY
    if not key:
        raise HTTPException(status_code=400, detail="Chưa cấu hình OPENROUTER_API_KEY. Vào Cài đặt để nhập key.")
    
    all_messages = []
    if system:
        all_messages.append({"role": "system", "content": system})
    all_messages.extend(messages)
    
    payload = {
        "model": model,
        "messages": all_messages,
        "max_tokens": 2048,
        "temperature": 0.3,
    }
    
    async with httpx.AsyncClient(timeout=90.0) as client:
        resp = await client.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://huyhaha-dl-platform.edu.vn",
                "X-Title": "HuyHaha Deep Learning Platform"
            },
            json=payload
        )
        if resp.status_code != 200:
            detail = resp.text[:300]
            raise HTTPException(status_code=resp.status_code, detail=f"OpenRouter API lỗi: {detail}")
        data = resp.json()
        return data["choices"][0]["message"]["content"]

@app.get("/health")
async def health():
    return {"status": "ok", "platform": "HuyHaha DL Platform v2", "api_key_set": bool(OPENROUTER_API_KEY)}

@app.get("/api/config-status")
async def config_status():
    return {"api_key_configured": bool(OPENROUTER_API_KEY)}

@app.post("/api/set-api-key")
async def set_api_key(body: SetKeyRequest):
    global OPENROUTER_API_KEY
    key = body.api_key.strip()
    if not key or len(key) < 10:
        raise HTTPException(status_code=400, detail="API key không hợp lệ")
    OPENROUTER_API_KEY = key
    return {"status": "ok", "message": "Đã cập nhật API key thành công"}

@app.post("/api/grade")
async def grade_answer(req: GradingRequest):
    system_prompt = """Bạn là giáo viên chấm điểm chuyên sâu về Deep Learning, Machine Learning và NLP tại Việt Nam.
Chấm điểm câu trả lời học sinh một cách CÔNG BẰNG, CHI TIẾT và MANG TÍNH XÂY DỰNG.

Trả lời CHỈ bằng JSON hợp lệ, không thêm markdown, không thêm text nào khác:
{
  "score": <số nguyên 0 đến max_score>,
  "feedback": "<nhận xét tổng quan 2-3 câu, bằng tiếng Việt, cụ thể>",
  "strengths": ["<điểm mạnh cụ thể 1>", "<điểm mạnh cụ thể 2>"],
  "improvements": ["<gợi ý cải thiện cụ thể 1>", "<gợi ý cải thiện cụ thể 2>"],
  "detailed_breakdown": {
    "concept_understanding": <0-40>,
    "technical_accuracy": <0-40>,
    "completeness": <0-20>
  },
  "missing_concepts": ["<khái niệm còn thiếu>"],
  "encouragement": "<câu động viên ngắn bằng tiếng Việt>"
}"""

    user_msg = f"""Câu hỏi/Bài tập: {req.question}

Chủ đề: {req.subject}
Các khái niệm kỳ vọng: {', '.join(req.expected_concepts)}
Điểm tối đa: {req.max_score}

Câu trả lời học sinh:
---
{req.student_answer}
---

Chấm điểm chi tiết và công bằng."""

    raw = await call_openrouter([{"role": "user", "content": user_msg}], system=system_prompt)
    
    try:
        clean = raw.strip()
        if "```" in clean:
            parts = clean.split("```")
            for p in parts:
                p2 = p.strip()
                if p2.startswith("json"):
                    p2 = p2[4:].strip()
                if p2.startswith("{"):
                    clean = p2
                    break
        result = json.loads(clean)
        score = max(0, min(int(result.get("score", 0)), req.max_score))
        return {
            "score": score,
            "max_score": req.max_score,
            "feedback": result.get("feedback", ""),
            "strengths": result.get("strengths", []),
            "improvements": result.get("improvements", []),
            "detailed_breakdown": result.get("detailed_breakdown", {}),
            "missing_concepts": result.get("missing_concepts", []),
            "encouragement": result.get("encouragement", "Tiếp tục cố gắng nhé!")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Lỗi parse JSON từ AI: {str(e)}. Raw: {raw[:200]}")

@app.post("/api/chat")
async def chat(req: ChatRequest):
    system_prompt = """Bạn là trợ lý AI chuyên sâu của thầy HuyHaha, chuyên về Deep Learning, Machine Learning, NLP và Computer Vision.

Phong cách: thân thiện, rõ ràng, có ví dụ cụ thể, dùng tiếng Việt là chủ yếu.
Chuyên môn: CNN, RNN, LSTM, GRU, Transformer, BERT, GPT, T5, YOLO, RAG, LoRA, SFT, RLHF, PPO, GRPO, FastAPI, Docker, MLflow, W&B.

Khi giải thích: dùng bullet points, code examples nếu cần, luôn đưa ví dụ thực tế.
Khi học sinh hỏi code: cung cấp code hoàn chỉnh, có comment giải thích."""

    if req.context:
        system_prompt += f"\n\nHọc sinh đang học: {req.context}"

    messages = req.history[-12:] + [{"role": "user", "content": req.message}]
    response = await call_openrouter(messages, system=system_prompt, model=CHAT_MODEL)
    return {"response": response}
