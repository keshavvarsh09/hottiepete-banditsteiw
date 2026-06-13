"""Text Stories pipeline: animated chat bubbles + optional per-message TTS narration."""
import os
import json
import subprocess
from sqlmodel import Session
from .config import settings
from .models import RenderJob, Project
from .providers import chatstory as cs_p
from .providers import tts as tts_p
from .providers import assemble as asm_p


def _update(session, job, status, progress):
    job.status = status
    job.progress = progress
    session.add(job)
    session.commit()
    session.refresh(job)


async def run_textstory_job(session: Session, job_id: int):
    """data: {
        messages: [{text, sender(bool), voice_id?}],
        scheme('light'|'dark'), title, show_header(bool), narrate(bool)
    }"""
    job = session.get(RenderJob, job_id)
    project = session.get(Project, job.project_id)
    data = json.loads(project.data_json or "{}")
    work = os.path.join(settings.renders_dir, f"job_{job_id}")
    os.makedirs(work, exist_ok=True)
    try:
        messages = data.get("messages", [])
        narrate = data.get("narrate", False)

        # Optional per-message TTS to size each hold to the spoken duration
        holds = []
        voice_path = None
        if narrate:
            _update(session, job, "tts", 35)
            audio_paths = []
            for i, m in enumerate(messages):
                vid = m.get("voice_id") or settings.fish_voice_a
                ap = os.path.join(work, f"m_{i}.mp3")
                await tts_p.synthesize(m["text"], vid, ap)
                audio_paths.append(ap)
                holds.append(asm_p.get_duration(ap) + 0.3)
            voice_path = os.path.join(work, "voice.mp3")
            asm_p.concat_audio(audio_paths, voice_path)

        _update(session, job, "assembling", 70)
        frames_dir = os.path.join(work, "frames")
        # variable holds not yet per-frame; use average when narrating
        hold = (sum(holds) / len(holds)) if holds else 1.4
        pattern, fps, total = cs_p.render_frames(
            messages, frames_dir, scheme=data.get("scheme", "dark"),
            title=data.get("title", "Messages"), show_header=data.get("show_header", True),
            hold_seconds=hold)

        out_path = os.path.join(settings.renders_dir, f"render_{job_id}.mp4")
        cmd = ["ffmpeg", "-y", "-framerate", str(fps), "-i", pattern]
        if voice_path:
            cmd += ["-i", voice_path]
        cmd += ["-c:v", "libx264", "-pix_fmt", "yuv420p"]
        if voice_path:
            cmd += ["-c:a", "aac", "-shortest"]
        cmd += [out_path]
        subprocess.run(cmd, check=True, capture_output=True)

        job.output_path = out_path
        _update(session, job, "ready", 100)
    except Exception as e:  # noqa: BLE001
        job.error = str(e)
        _update(session, job, "error", job.progress)
