"""Fish Audio TTS. Each character maps to a Fish Audio voice ID."""
import httpx
from ..config import settings

FISH_TTS_URL = "https://api.fish.audio/v1/tts"


async def synthesize(text: str, voice_id: str, out_path: str) -> str:
    """Synthesize one line to an mp3 at out_path. Returns out_path.

    Requires FISH_API_KEY. voice_id is the Fish Audio model/reference id.
    """
    if not settings.fish_api_key:
        raise RuntimeError("FISH_API_KEY is not set")

    payload = {"text": text, "reference_id": voice_id, "format": "mp3"}
    async with httpx.AsyncClient(timeout=120) as client:
        r = await client.post(
            FISH_TTS_URL,
            headers={"Authorization": f"Bearer {settings.fish_api_key}"},
            json=payload,
        )
        r.raise_for_status()
        with open(out_path, "wb") as f:
            f.write(r.content)
    return out_path
