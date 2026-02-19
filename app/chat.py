import logging
import re
from pathlib import Path

from fastapi import APIRouter, HTTPException
from mlx_lm import generate, load
from pydantic import BaseModel

from app.config import settings
from app.rag import retrieve_context

logger = logging.getLogger(__name__)

router = APIRouter()

_model = None
_tokenizer = None
_system_prompt_template: str | None = None

SYSTEM_PROMPT_PATH = Path("docs/system-prompt.md")


def _load_system_prompt() -> str:
    """Load and cache the system prompt template from docs/."""
    global _system_prompt_template
    if _system_prompt_template is None:
        if not SYSTEM_PROMPT_PATH.exists():
            logger.warning(
                "System prompt file %s not found, using fallback",
                SYSTEM_PROMPT_PATH,
            )
            _system_prompt_template = (
                "You are a helpful assistant."
                "\n\n{{retrieved_context}}"
            )
        else:
            raw = SYSTEM_PROMPT_PATH.read_text()
            match = re.search(
                r"^## Prompt\s*\n+```\n(.*?)```",
                raw,
                re.DOTALL | re.MULTILINE,
            )
            if match:
                _system_prompt_template = match.group(1).rstrip("\n")
            else:
                _system_prompt_template = raw
    return _system_prompt_template


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

    context = retrieve_context(request.message)
    system_prompt = _load_system_prompt().replace(
        "{{retrieved_context}}", context
    )

    messages = [
        {"role": "system", "content": system_prompt},
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
