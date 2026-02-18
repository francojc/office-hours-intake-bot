from fastapi import APIRouter, HTTPException
from mlx_lm import generate, load
from pydantic import BaseModel

from app.config import settings

router = APIRouter()

_model = None
_tokenizer = None


def get_model():
    global _model, _tokenizer
    if _model is None:
        if not settings.model_path.exists():
            raise RuntimeError(
                f"Model not found at {settings.model_path}. "
                "Run: uv run mlx_lm.convert --hf-path "
                "Qwen/Qwen2.5-3B-Instruct "
                f"--mlx-path {settings.model_path}"
            )
        _model, _tokenizer = load(str(settings.model_path))
    return _model, _tokenizer


class ChatRequest(BaseModel):
    message: str


class ChatResponse(BaseModel):
    reply: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    try:
        model, tokenizer = get_model()
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))

    messages = [
        {"role": "system", "content": "You are a helpful assistant."},
        {"role": "user", "content": request.message},
    ]
    prompt = tokenizer.apply_chat_template(
        messages, tokenize=False, add_generation_prompt=True
    )
    reply = generate(
        model,
        tokenizer,
        prompt=prompt,
        max_tokens=256,
    )
    return ChatResponse(reply=reply)
