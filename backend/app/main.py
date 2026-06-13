import os
import json
import shutil
from fastapi import FastAPI, Depends, UploadFile, File, Form, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlmodel import Session, select

from .config import settings
from .db import init_db, get_session, engine
from .models import Project, Character, Voice, RenderJob
from .pipeline import run_dialogue_job
from .pipeline_narration import run_narration_job
from .pipeline_editing import run_captions_job, run_split_job
from .pipeline_textstory import run_textstory_job
from .pipeline_isolation import run_isolation_job
from .providers import tts as tts_p
from .providers import cards as cards_p

app = FastAPI(title="hottiepete banditsteiw")
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"],
)

os.makedirs(os.path.join(settings.assets_dir, "backgrounds"), exist_ok=True)
os.makedirs(os.path.join(settings.assets_dir, "characters"), exist_ok=True)
os.makedirs(settings.renders_dir, exist_ok=True)
app.mount("/assets", StaticFiles(directory=settings.assets_dir), name="assets")


@app.on_event("startup")
def _startup():
    init_db()


@app.get("/api/health")
def health():
    return {"ok": True}


# ---- Projects ----
@app.get("/api/projects")
def list_projects(session: Session = Depends(get_session)):
    return session.exec(select(Project)).all()


@app.post("/api/projects")
def create_project(payload: dict, session: Session = Depends(get_session)):
    p = Project(name=payload.get("name", "Untitled"), type=payload.get("type", "dialogue"),
                data_json=json.dumps(payload.get("data", {})))
    session.add(p); session.commit(); session.refresh(p)
    return p


@app.put("/api/projects/{pid}")
def update_project(pid: int, payload: dict, session: Session = Depends(get_session)):
    p = session.get(Project, pid)
    if not p:
        raise HTTPException(404)
    if "name" in payload:
        p.name = payload["name"]
    if "data" in payload:
        p.data_json = json.dumps(payload["data"])
    session.add(p); session.commit(); session.refresh(p)
    return p


@app.get("/api/projects/{pid}")
def get_project(pid: int, session: Session = Depends(get_session)):
    p = session.get(Project, pid)
    if not p:
        raise HTTPException(404)
    return p


# ---- Characters ----
@app.get("/api/characters")
def list_characters(session: Session = Depends(get_session)):
    return session.exec(select(Character)).all()


@app.post("/api/characters")
async def create_character(name: str = Form(...), voice_id: str = Form(...),
                           image: UploadFile = File(None), session: Session = Depends(get_session)):
    image_path = ""
    if image:
        image_path = os.path.join(settings.assets_dir, "characters", image.filename)
        with open(image_path, "wb") as f:
            shutil.copyfileobj(image.file, f)
    c = Character(name=name, voice_id=voice_id, image_path=image_path)
    session.add(c); session.commit(); session.refresh(c)
    return c


# ---- Voices ----
@app.get("/api/voices")
def list_voices(session: Session = Depends(get_session)):
    return session.exec(select(Voice)).all()


@app.post("/api/voices")
def create_voice(payload: dict, session: Session = Depends(get_session)):
    v = Voice(name=payload["name"], voice_id=payload["voice_id"])
    session.add(v); session.commit(); session.refresh(v)
    return v


@app.post("/api/voices/try")
async def try_voice(payload: dict):
    """Preview a Fish Audio voice: synthesize a short sample, return the mp3."""
    out = os.path.join(settings.renders_dir, "preview.mp3")
    await tts_p.synthesize(payload.get("text", "This is a voice preview."), payload["voice_id"], out)
    return FileResponse(out, media_type="audio/mpeg")


# ---- Backgrounds ----
@app.get("/api/backgrounds")
def list_backgrounds():
    base = os.path.join(settings.assets_dir, "backgrounds")
    items = []
    for root, _, files in os.walk(base):
        for fn in files:
            if fn.lower().endswith(".mp4"):
                rel = os.path.relpath(os.path.join(root, fn), settings.assets_dir)
                cat = os.path.basename(root) if root != base else "Uncategorized"
                items.append({"name": fn, "category": cat, "path": os.path.join(root, fn),
                              "url": f"/assets/{rel}"})
    return items


@app.post("/api/backgrounds")
async def upload_background(category: str = Form("Other Games"), file: UploadFile = File(...)):
    cat_dir = os.path.join(settings.assets_dir, "backgrounds", category)
    os.makedirs(cat_dir, exist_ok=True)
    dest = os.path.join(cat_dir, file.filename)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    return {"path": dest}


# ---- Social cards (Reddit / Twitter) ----
@app.post("/api/cards/reddit")
def make_reddit_card(payload: dict):
    out = os.path.join(settings.assets_dir, "characters", f"reddit_{abs(hash(str(payload)))}.png")
    cards_p.reddit_card(
        payload.get("subreddit", "AskReddit"), payload.get("username", "user"),
        payload.get("title", ""), payload.get("body", ""),
        payload.get("upvotes", "1.2k"), payload.get("comments", "340"), out)
    rel = os.path.relpath(out, settings.assets_dir)
    return {"path": out, "url": f"/assets/{rel}"}


@app.post("/api/cards/tweet")
def make_tweet_card(payload: dict):
    out = os.path.join(settings.assets_dir, "characters", f"tweet_{abs(hash(str(payload)))}.png")
    cards_p.tweet_card(payload.get("name", "User"), payload.get("handle", "user"),
                       payload.get("text", ""), out)
    rel = os.path.relpath(out, settings.assets_dir)
    return {"path": out, "url": f"/assets/{rel}"}


# ---- Generic media upload (for AI Captions / Split Video clips) ----
@app.post("/api/media")
async def upload_media(file: UploadFile = File(...)):
    media_dir = os.path.join(settings.assets_dir, "media")
    os.makedirs(media_dir, exist_ok=True)
    dest = os.path.join(media_dir, file.filename)
    with open(dest, "wb") as f:
        shutil.copyfileobj(file.file, f)
    rel = os.path.relpath(dest, settings.assets_dir)
    return {"path": dest, "url": f"/assets/{rel}"}


# ---- Render (dispatch by project type) ----
_NARRATION_TYPES = {"voiceover", "reddit", "twitter"}


@app.post("/api/projects/{pid}/render")
async def render(pid: int, background: BackgroundTasks, session: Session = Depends(get_session)):
    project = session.get(Project, pid)
    if not project:
        raise HTTPException(404)
    job = RenderJob(project_id=pid)
    session.add(job); session.commit(); session.refresh(job)
    ptype = project.type

    async def _run(job_id: int):
        with Session(engine) as s:
            if ptype in _NARRATION_TYPES:
                await run_narration_job(s, job_id)
            elif ptype == "captions":
                await run_captions_job(s, job_id)
            elif ptype == "split":
                await run_split_job(s, job_id)
            elif ptype == "textstories":
                await run_textstory_job(s, job_id)
            elif ptype == "isolation":
                await run_isolation_job(s, job_id)
            else:
                await run_dialogue_job(s, job_id)

    background.add_task(_run, job.id)
    return {"job_id": job.id}


@app.get("/api/jobs/{jid}")
def job_status(jid: int, session: Session = Depends(get_session)):
    job = session.get(RenderJob, jid)
    if not job:
        raise HTTPException(404)
    return job


@app.get("/api/jobs/{jid}/download")
def download(jid: int, session: Session = Depends(get_session)):
    job = session.get(RenderJob, jid)
    if not job or not job.output_path or not os.path.exists(job.output_path):
        raise HTTPException(404)
    ext = os.path.splitext(job.output_path)[1].lower()
    media = {".mp4": "video/mp4", ".wav": "audio/wav", ".mp3": "audio/mpeg"}.get(ext, "application/octet-stream")
    return FileResponse(job.output_path, media_type=media, filename=f"output_{jid}{ext}")


@app.get("/api/videos")
def list_videos(session: Session = Depends(get_session)):
    return session.exec(select(RenderJob).where(RenderJob.status == "ready")).all()
