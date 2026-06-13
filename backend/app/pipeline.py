"""Job pipeline orchestrator for the Dialogue Video flow."""
import os
import json
from sqlmodel import Session
from .config import settings
from .models import RenderJob, Project, Character
from .providers import script as script_p
from .providers import tts as tts_p
from .providers import broll as broll_p
from .providers import subtitles as sub_p
from .providers import assemble as asm_p


def _update(session: Session, job: RenderJob, status: str, progress: int):
    job.status = status
    job.progress = progress
    session.add(job)
    session.commit()
    session.refresh(job)


async def run_dialogue_job(session: Session, job_id: int):
    job = session.get(RenderJob, job_id)
    project = session.get(Project, job.project_id)
    data = json.loads(project.data_json or "{}")
    work = os.path.join(settings.renders_dir, f"job_{job_id}")
    os.makedirs(work, exist_ok=True)

    try:
        # 1. Script (use saved script if present, else generate)
        _update(session, job, "scripting", 10)
        scr = data.get("script") or await script_p.generate_script(data.get("topic", ""))

        # Map speakers A/B to character voice IDs
        chars = {c.name: c for c in session.query(Character).all()} if hasattr(session, "query") else {}
        voice_a = data.get("voice_a") or settings.fish_voice_a
        voice_b = data.get("voice_b") or settings.fish_voice_b

        # 2. TTS per line
        _update(session, job, "tts", 35)
        audio_paths, line_durations = [], []
        for i, line in enumerate(scr["lines"]):
            vid = voice_a if line["speaker"] == "A" else voice_b
            ap = os.path.join(work, f"line_{i}.mp3")
            await tts_p.synthesize(line["text"], vid, ap)
            audio_paths.append(ap)
            line_durations.append(asm_p.get_duration(ap))

        voice_path = os.path.join(work, "voice.mp3")
        asm_p.concat_audio(audio_paths, voice_path)

        # 3. B-roll per line (top overlay), timed to each line
        _update(session, job, "broll", 55)
        broll_overlays, t = [], 0.0
        for i, line in enumerate(scr["lines"]):
            img = os.path.join(work, f"broll_{i}.jpg")
            await broll_p.generate_image(line.get("broll_prompt", line["text"]), img)
            broll_overlays.append({"path": img, "start": t, "end": t + line_durations[i]})
            t += line_durations[i]

        # 4. Subtitles (centered karaoke)
        _update(session, job, "subtitles", 75)
        words = sub_p.transcribe_words(voice_path)
        ass_path = os.path.join(work, "subs.ass")
        sub_p.write_ass(words, ass_path, style=data.get("subtitle_style", "Default"),
                        settings=data.get("subtitle_settings", {}))

        # 5. Assembly
        _update(session, job, "assembling", 90)
        bg = data.get("background_path")
        char_overlays = data.get("character_overlays", [])  # [{path,x,y,scale}]
        out_path = os.path.join(settings.renders_dir, f"render_{job_id}.mp4")
        asm_p.assemble(bg, voice_path, ass_path, out_path,
                       broll_overlays=broll_overlays,
                       character_overlays=char_overlays,
                       music_path=data.get("music_path"),
                       music_volume=data.get("music_volume", 0.2))

        job.output_path = out_path
        _update(session, job, "ready", 100)
    except Exception as e:  # noqa: BLE001
        job.error = str(e)
        _update(session, job, "error", job.progress)
