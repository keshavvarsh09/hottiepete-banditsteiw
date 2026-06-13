"""Script generation via Groq (free LLM). Provider is pluggable.

Produces two-speaker dialogue: a caption hook, alternating lines, a closer CTA,
and a per-line B-roll image prompt derived from each line.
"""
import json
import httpx
from ..config import settings

SYSTEM_PROMPT = (
    "You write short viral two-character dialogue scripts for 9:16 videos. "
    "One character is an exasperated genius explaining a useful website/app hack; "
    "the other is a dim-witted partner who reacts and asks naive questions. "
    "Keep it crisp and punchy. Return STRICT JSON only with this shape: "
    '{"hook": str, "lines": [{"speaker": "A"|"B", "text": str, "broll_prompt": str}], "closer": str}. '
    "speaker A = the smart one, speaker B = the dim one. "
    "broll_prompt is a short, concrete image description matching that line's content."
)


async def generate_script(topic: str) -> dict:
    if not settings.groq_api_key:
        # offline fallback so the pipeline runs without a key
        return {
            "hook": f"Here is a website that changes how you do {topic}.",
            "lines": [
                {"speaker": "B", "text": f"Ugh, doing {topic} is such a pain!",
                 "broll_prompt": f"frustrated person struggling with {topic}, screen glow"},
                {"speaker": "A", "text": "You absolute caveman. There is a free site for that.",
                 "broll_prompt": "clean modern website interface on a laptop"},
            ],
            "closer": "Save this so you never forget it.",
        }

    payload = {
        "model": settings.groq_model,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Topic: {topic}"},
        ],
        "response_format": {"type": "json_object"},
        "temperature": 0.8,
    }
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {settings.groq_api_key}"},
            json=payload,
        )
        r.raise_for_status()
        content = r.json()["choices"][0]["message"]["content"]
    return json.loads(content)
