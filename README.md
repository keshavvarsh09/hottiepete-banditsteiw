<div align="center">

# 🎬 hottiepete banditsteiw

### Self-hosted AI short-video generator. 9:16 vertical, 1080×1920.

[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![FFmpeg](https://img.shields.io/badge/FFmpeg-007808?style=for-the-badge&logo=ffmpeg&logoColor=white)](https://ffmpeg.org)

**Script → Voice → Visuals → Subtitles → Export. Fully automated.**

---

*Type a topic. Get a publish-ready vertical video with AI voices, B-roll, and karaoke captions — in minutes.*

</div>

<br/>

## ✨ Features

| | Feature | What it does |
|---|---|---|
| 🎙️ | **Dialogue Video** | Topic → LLM script → dual-voice TTS → AI B-roll images → word-level karaoke subtitles → ffmpeg assembly with draggable character cutouts on a 9:16 canvas |
| 📰 | **Reddit Video** | Pillow-rendered Reddit post card narrated over a looping background with centered captions |
| 🐦 | **Twitter Video** | Sequence of tweet cards narrated in order with synced subtitles |
| 🎤 | **AI Voiceover** | Single-voice narration over background video with word-level captions |
| 🧠 | **Split Video** | Brain-rot stacked layout — main clip top, gameplay bottom (1080×960 each) — with optional auto-captions |
| 💬 | **Text Stories** | iMessage-style animated chat bubble conversations rendered frame-by-frame via Pillow |
| 📝 | **AI Captions** | Upload any video → auto-transcribe → burn centered karaoke captions (scaled to 9:16) |
| 🎵 | **Voice Isolation** | Upload audio/video → Demucs separates vocals from background music/noise → download clean `.wav` |

### 🎨 Subtitle Style Presets

`Default` · `TikTok` · `Cinema` · `Bold` · `Colorful` · `Cyberpunk` · `Soft` · `Cartoon` · `Haze`

---

## 🏗️ Architecture

```
┌─────────────────────────────────────┐
│           Frontend (SPA)            │
│    Vanilla HTML/CSS/JS · Liquid     │
│    Glass UI · Hosted on Vercel      │
└──────────────┬──────────────────────┘
               │  REST API
               ▼
┌─────────────────────────────────────┐
│         Backend (FastAPI)           │
│    Dockerized · Railway / VPS       │
│                                     │
│  ┌───────────────────────────────┐  │
│  │        Render Pipeline        │  │
│  │                               │  │
│  │  scripting ──► tts ──► broll  │  │
│  │       │                  │    │  │
│  │       ▼                  ▼    │  │
│  │  subtitles ◄──────── assembling │ │
│  │       │                       │  │
│  │       ▼                       │  │
│  │     ready                     │  │
│  └───────────────────────────────┘  │
│                                     │
│  ┌─────────┐ ┌──────────┐ ┌──────┐ │
│  │ SQLite  │ │ assets/  │ │render│ │
│  │ metadata│ │ uploads  │ │  s/  │ │
│  └─────────┘ └──────────┘ └──────┘ │
└─────────────────────────────────────┘
        │             │           │
        ▼             ▼           ▼
   ┌─────────┐  ┌──────────┐ ┌────────────┐
   │  Groq   │  │  Fish    │ │Pollinations│
   │  LLM    │  │  Audio   │ │  AI Images │
   │ (script)│  │  (TTS)   │ │  (B-roll)  │
   └─────────┘  └──────────┘ └────────────┘
```

### Dialogue Pipeline — Step by Step

```
 ┌───────┐    ┌─────────┐    ┌──────────┐    ┌───────────────┐    ┌──────────┐    ┌───────┐
 │ Topic │───▶│  Groq   │───▶│ Fish TTS │───▶│  Pollinations │───▶│ faster-  │───▶│ffmpeg │
 │ Input │    │ Script  │    │ 2 Voices │    │  B-Roll Imgs  │    │ whisper  │    │Compose│
 └───────┘    └─────────┘    └──────────┘    └───────────────┘    │ Karaoke  │    └───┬───┘
                                                                  └──────────┘        │
                                                                                      ▼
                                                                               ┌────────────┐
                                                                               │  1080×1920  │
                                                                               │  .mp4 ready │
                                                                               └────────────┘
```

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|:---|:---|:---|
| **Backend** | FastAPI | Async REST API + job pipeline |
| **Database** | SQLite via SQLModel | Project/character/voice/job metadata |
| **TTS** | Fish Audio API | High-quality multi-voice speech synthesis |
| **Script Gen** | Groq API (Llama 3.3 70B) | Ultra-fast LLM script generation |
| **B-Roll** | Pollinations AI | Free AI image generation (no API key) |
| **Transcription** | faster-whisper (local) | Word-level timestamps for karaoke subs |
| **Video** | FFmpeg | Composition, scaling, subtitle burn-in |
| **Voice Isolation** | Demucs (local) | Vocal / music separation |
| **Social Cards** | Pillow | Reddit post & tweet card rendering |
| **Frontend** | Vanilla HTML / CSS / JS | Zero-dependency SPA |
| **UI Theme** | Liquid Glass / Glassmorphism | iOS-inspired frosted glass aesthetic |
| **Container** | Docker + Docker Compose | One-command deployment |
| **Hosting** | Railway + Vercel | Backend (persistent disk) + Frontend (static) |

---

## 🚀 Quick Start

### 1 — Clone & Configure

```bash
git clone https://github.com/<your-username>/hottiepete-banditsteiw.git
cd hottiepete-banditsteiw
cp .env.example .env
```

Open `.env` and fill in your API keys:

```env
FISH_API_KEY=your_fish_audio_key
FISH_VOICE_A=voice_id_for_speaker_a
FISH_VOICE_B=voice_id_for_speaker_b
GROQ_API_KEY=your_groq_key          # Free at console.groq.com
```

### 2a — Run with Docker *(recommended)*

```bash
docker compose up --build
```

> Backend available at **http://localhost:8000**

### 2b — Run without Docker

```bash
# Backend
cd backend
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
# Install ffmpeg separately: apt / brew / choco install ffmpeg
uvicorn app.main:app --reload --port 8000
```

```bash
# Frontend (any static server)
cd frontend
python -m http.server 5173
```

> Open **http://localhost:5173**

---

## 🔑 Environment Variables

| Variable | Required | Description |
|:---|:---:|:---|
| `FISH_API_KEY` | ✅ | Fish Audio API key for TTS |
| `FISH_VOICE_A` | ✅ | Fish Audio voice ID — Speaker A |
| `FISH_VOICE_B` | ✅ | Fish Audio voice ID — Speaker B |
| `GROQ_API_KEY` | ⚠️ | Groq API key — falls back to placeholder if missing |
| `GROQ_MODEL` | — | Model name (default: `llama-3.3-70b-versatile`) |
| `BACKEND_BASE_URL` | — | Backend URL (default: `http://localhost:8000`) |
| `DATABASE_URL` | — | SQLite path (default: `sqlite:///./data/app.db`) |
| `ASSETS_DIR` | — | Upload directory (default: `./assets`) |
| `RENDERS_DIR` | — | Output directory (default: `./renders`) |

> [!NOTE]
> If `GROQ_API_KEY` is missing, script generation returns a fallback placeholder — it won't crash.
> If `FISH_API_KEY` is missing, TTS **will** fail with a `RuntimeError`.

---

## 📡 API Reference

### General

| Method | Endpoint | Description |
|:---:|:---|:---|
| `GET` | `/api/health` | Health check |

### Projects

| Method | Endpoint | Description |
|:---:|:---|:---|
| `GET` | `/api/projects` | List all projects |
| `POST` | `/api/projects` | Create a project |
| `PUT` | `/api/projects/{id}` | Update a project |
| `GET` | `/api/projects/{id}` | Get project details |

### Characters & Voices

| Method | Endpoint | Description |
|:---:|:---|:---|
| `GET` | `/api/characters` | List characters |
| `POST` | `/api/characters` | Create character *(multipart: name, voice_id, image)* |
| `GET` | `/api/voices` | List voices |
| `POST` | `/api/voices` | Add a voice |
| `POST` | `/api/voices/try` | Preview a voice *(returns mp3)* |

### Media & Backgrounds

| Method | Endpoint | Description |
|:---:|:---|:---|
| `GET` | `/api/backgrounds` | List background videos |
| `POST` | `/api/backgrounds` | Upload a background `.mp4` |
| `POST` | `/api/media` | Upload generic media *(for captions / split)* |

### Social Cards

| Method | Endpoint | Description |
|:---:|:---|:---|
| `POST` | `/api/cards/reddit` | Generate a Reddit post card PNG |
| `POST` | `/api/cards/tweet` | Generate a tweet card PNG |

### Rendering

| Method | Endpoint | Description |
|:---:|:---|:---|
| `POST` | `/api/projects/{id}/render` | Start a render job |
| `GET` | `/api/jobs/{id}` | Poll job status |
| `GET` | `/api/jobs/{id}/download` | Download finished render |
| `GET` | `/api/videos` | List all completed renders |

> [!TIP]
> Interactive API docs are available at **`/docs`** (Swagger UI) and **`/redoc`** when the backend is running.

---

## 📂 Project Structure

```
hottiepete-banditsteiw/
│
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py                # FastAPI routes
│       ├── config.py              # Pydantic settings
│       ├── db.py                  # SQLite engine
│       ├── models.py              # Project, Character, Voice, RenderJob
│       ├── pipeline.py            # Dialogue video orchestrator
│       ├── pipeline_narration.py  # Reddit / Twitter / Voiceover pipeline
│       ├── pipeline_editing.py    # Captions + Split video pipeline
│       ├── pipeline_textstory.py  # Chat story pipeline
│       ├── pipeline_isolation.py  # Demucs vocal isolation
│       └── providers/
│           ├── assemble.py        # ffmpeg composition
│           ├── broll.py           # Pollinations image generation
│           ├── cards.py           # Reddit / Tweet card renderer
│           ├── chatstory.py       # Chat bubble frame renderer
│           ├── editing.py         # ffmpeg scale / crop / stack
│           ├── isolation.py       # Demucs vocal separation
│           ├── script.py          # Groq script generation
│           ├── subtitles.py       # faster-whisper + ASS output
│           └── tts.py             # Fish Audio TTS
│
├── frontend/
│   ├── index.html                 # SPA shell
│   ├── styles.css                 # Liquid Glass theme
│   ├── app.js                     # Router + all views
│   ├── config.js                  # Backend URL config
│   └── vercel.json                # SPA routing
│
├── .env.example
├── .gitignore
├── docker-compose.yml
├── LICENSE                        # MIT
├── README.md
└── SETUP.md                       # Detailed setup guide
```

---

## 🌐 Deployment

### Backend → Railway / Render / Fly / VPS

The backend needs **persistent disk storage** for SQLite, uploaded assets, and rendered videos.

```bash
# Railway example
railway login
railway link
railway up
```

> [!WARNING]
> **Vercel is NOT suitable for the backend.** It has no persistent filesystem and a 10 s function timeout — both are incompatible with video rendering.

### Frontend → Vercel

1. Update `frontend/config.js` with your deployed backend URL.
2. Deploy the `frontend/` directory to Vercel.
3. The included `vercel.json` handles SPA routing automatically.

---

## 📌 Important Notes

- 🚫 **No deepfakes** — Lip-sync of real people is intentionally not implemented.
- 🎥 **Backgrounds not bundled** — Supply your own `.mp4` loop files via the upload endpoint.
- 📁 **Auto-created directories** — The backend creates `data/`, `assets/`, and `renders/` on startup.
- 🗄️ **Database models** — `Project`, `Character`, `Voice`, `RenderJob` (SQLModel / Pydantic).

---

## 🤝 Contributing

Contributions are welcome! Whether it's a bug fix, a new subtitle preset, or a whole new pipeline — open a PR.

1. **Fork** the repository
2. **Create** a feature branch — `git checkout -b feat/amazing-feature`
3. **Commit** your changes — `git commit -m "feat: add amazing feature"`
4. **Push** to your branch — `git push origin feat/amazing-feature`
5. **Open** a Pull Request

Please keep PRs focused and well-described. For large changes, open an issue first to discuss.

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<div align="center">

**Built with ☕ and too many ffmpeg flags.**

</div>
