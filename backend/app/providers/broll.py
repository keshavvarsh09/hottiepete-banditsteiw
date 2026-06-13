"""B-roll images via Pollinations (free, no key). Rendered as a top overlay."""
import urllib.parse
import httpx


async def generate_image(prompt: str, out_path: str, width: int = 1024, height: int = 768) -> str:
    """Generate one B-roll image from a prompt. Returns out_path."""
    encoded = urllib.parse.quote(prompt)
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true"
    async with httpx.AsyncClient(timeout=120, follow_redirects=True) as client:
        r = await client.get(url)
        r.raise_for_status()
        with open(out_path, "wb") as f:
            f.write(r.content)
    return out_path
