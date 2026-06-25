"""B-roll images via imglink.ai (free keyless mode). Rendered as a top overlay."""
import urllib.parse
import httpx


async def generate_image(prompt: str, out_path: str, width: int = 1920, height: int = 1080) -> str:
    """Generate one B-roll image from a prompt. Returns out_path."""
    # Truncate prompt to 70 words to prevent URI limit errors
    words = prompt.split()
    if len(words) > 70:
        prompt = " ".join(words[:70])

    encoded = urllib.parse.quote(prompt)
    url = f"https://imglink.ai/images?prompt={encoded}&width={width}&height={height}&key=anonymous"

    async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
        r = await client.get(url)
        r.raise_for_status()
        with open(out_path, "wb") as f:
            f.write(r.content)
    return out_path
