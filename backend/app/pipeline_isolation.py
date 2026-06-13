"""Voice Isolation pipeline: extract clean vocals from an uploaded audio/video file."""
import os
import json
import shutil
from sqlmodel import Session
from .config import settings
from .models import RenderJob, Project
from .providers import isolation as iso_p


def _update(session, job, status, progress):
    job.status = status
    job.progress = progress
    session.add(job)
    session.commit()
    session.refresh(job)


async def run_isolation_job(session: Session, job_id: int):
    """data: {input_path}"""
    job = session.get(RenderJob, job_id)
    project = session.get(Project, job.project_id)
    data = json.loads(project.data_json or "{}")
    work = os.path.join(settings.renders_dir, f"job_{job_id}")
    os.makedirs(work, exist_ok=True)
    try:
        _update(session, job, "assembling", 30)
        vocals = iso_p.isolate_vocals(data["input_path"], work)
        out_path = os.path.join(settings.renders_dir, f"vocals_{job_id}.wav")
        shutil.copy(vocals, out_path)
        job.output_path = out_path
        _update(session, job, "ready", 100)
    except Exception as e:  # noqa: BLE001
        job.error = str(e)
        _update(session, job, "error", job.progress)
