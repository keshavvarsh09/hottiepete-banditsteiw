# Step-by-step setup

## 0. Prerequisites
- Docker + Docker Compose (easiest), OR Python 3.11 + ffmpeg installed locally.
- A free Groq API key (https://console.groq.com) for script generation.
- A Fish Audio API key + your voice IDs.

## 1. Get the code
```
cd "hottiepete banditsteiw"
cp .env.example .env
```
Edit `.env` and fill in:
- `FISH_API_KEY`, `FISH_VOICE_A`, `FISH_VOICE_B`
- `GROQ_API_KEY`
- Leave `BACKEND_BASE_URL=http://localhost:8000` for local.

## 2. Run the backend (Docker, recommended)
```
docker compose up --build
```
Backend at http://localhost:8000, frontend at http://localhost:5173 (ffmpeg + whisper baked in).

### Or run the backend without Docker
```
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
# install ffmpeg separately (apt install ffmpeg / brew install ffmpeg)
uvicorn app.main:app --reload --port 8000
```

## 3. Run the frontend
It is static. Any static server works:
```
cd frontend
python -m http.server 5173
```
Open http://localhost:5173. (`config.js` already points to localhost:8000.)

## 4. Add your assets
- **Backgrounds**: open the Backgrounds page → pick a category (Minecraft, Satisfying, ...) → upload your `.mp4`. Files land in `backend/assets/backgrounds/<category>/`. No clips are bundled, supply your own.
- **Characters**: Characters page → Create Character → name + Fish Audio voice ID + upload a cutout PNG.
- **Voices**: Voices page → add a name + voice ID → "Try Out" to preview.

## 5. Make a video
1. Go to **Dialogue Video**.
2. Enter a topic, pick a background and subtitle style.
3. Drag your character cutouts on the 9:16 canvas to position them (saved as x/y/scale).
4. Click **Render Video** and watch the step progress (scripting → tts → broll → subtitles → assembling → ready).
5. Download from the link, or from **Rendered Videos**.

## 6. Deploy (when ready)
### Backend → Railway (needs persistent disk; NOT Vercel)
1. Create a Railway project from this repo, root = `hottiepete banditsteiw/backend` (it has the Dockerfile).
2. Add a **Volume** mounted at `/app` (or at `/app/data`, `/app/assets`, `/app/renders`).
3. Set env vars: `FISH_API_KEY`, `FISH_VOICE_A`, `FISH_VOICE_B`, `GROQ_API_KEY`.
4. Deploy. Note the public URL (e.g. https://your-app.up.railway.app).

### Frontend → Vercel
1. Import the repo into Vercel, set root to `hottiepete banditsteiw/frontend`.
2. Edit `config.js` (or set it at build) so `window.BACKEND_BASE_URL` = your Railway URL.
3. Deploy. `vercel.json` handles SPA routing.

### CORS
The backend already allows all origins. Tighten `allow_origins` in `app/main.py` to your Vercel domain for production.

## Notes / limits
- Vercel cannot run the backend (no persistent disk, function timeouts, no ffmpeg/whisper). Keep backend on Railway/Render/Fly/VPS.
- Deepfake / lip-sync of real people is intentionally not implemented.
- Playground is a scaffolded UI stub. All other pipelines (Dialogue, Reddit, Twitter, AI Voiceover, Split Video, Text Stories, AI Captions, and Voice Isolation) are fully implemented and functional.
