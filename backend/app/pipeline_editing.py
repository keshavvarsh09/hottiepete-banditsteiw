"""Pipelines for AI Captions (caption an uploaded video) and Split Video."""
import os
import json
from sqlmodel import Session
from .config import settings
from .models import RenderJob, Project
from .providers import subtitles as sub_p
from .providers import editing as edit_p


def _update(session, job, status, progress):
    job.status = status
    job.progress = progress
    session.add(job)
    session.commit()
    session.refresh(job)


async def run_captions_job(session: Session, job_id: int):
    """data: {video_path, subtitle_style, subtitle_settings}"""
    job = session.get(RenderJob, job_id)
    project = session.get(Project, job.project_id)
    data = json.loads(project.data_json or "{}")
    work = os.path.join(settings.renders_dir, f"job_{job_id}")
    os.makedirs(work, exist_ok=True)
    try:
        video = data["video_path"]
        _update(session, job, "subtitles", 40)
        words = sub_p.transcribe_words(video)
        ass_path = os.path.join(work, "subs.ass")
        sub_p.write_ass(words, ass_path, style=data.get("subtitle_style", "Default"),
                        settings=data.get("subtitle_settings", {}))
        _update(session, job, "assembling", 85)
        out_path = os.path.join(settings.renders_dir, f"render_{job_id}.mp4")
        edit_p.burn_captions(video, ass_path, out_path)
        job.output_path = out_path
        _update(session, job, "ready", 100)
    except Exception as e:  # noqa: BLE001
        job.error = str(e)
        _update(session, job, "error", job.progress)


async def run_split_job(session: Session, job_id: int):
    """data: {main_path, bg_path, main_speed, bg_speed, captions, subtitle_style}"""
    job = session.get(RenderJob, job_id)
    project = session.get(Project, job.project_id)
    data = json.loads(project.data_json or "{}")
    work = os.path.join(settings.renders_dir, f"job_{job_id}")
    os.makedirs(work, exist_ok=True)
    try:
        ass_path = None
        if data.get("captions"):
            _update(session, job, "subtitles", 40)
            words = sub_p.transcribe_words(data["main_path"])
            ass_path = os.path.join(work, "subs.ass")
            sub_p.write_ass(words, ass_path, style=data.get("subtitle_style", "Default"),
                            settings=data.get("subtitle_settings", {}))
        _update(session, job, "assembling", 85)
        out_path = os.path.join(settings.renders_dir, f"render_{job_id}.mp4")
        edit_p.split_stack(data["main_path"], data["bg_path"], out_path, ass_path=ass_path,
                           main_speed=data.get("main_speed", 1.0), bg_speed=data.get("bg_speed", 1.0))
        job.output_path = out_path
        _update(session, job, "ready", 100)
    except Exception as e:  # noqa: BLE001
        job.error = str(e)
        _update(session, job, "error", job.progress)
