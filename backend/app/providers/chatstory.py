"""Animated chat-story renderer (original iMessage-style UI, not a clone of Apple assets).

Draws chat bubbles that appear in sequence, exports a sequence of PNG frames that
ffmpeg turns into a 9:16 clip. Sender on the right, others on the left.
"""
import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1080, 1920
PAD = 48
BUBBLE_MAX = 720
LINE_H = 46
GAP = 22


def _font(size, bold=False):
    try:
        path = "/usr/share/fonts/truetype/dejavu/DejaVuSans%s.ttf" % ("-Bold" if bold else "")
        return ImageFont.truetype(path, size)
    except Exception:
        return ImageFont.load_default()


def _wrap(draw, text, font, max_w):
    words, lines, cur = text.split(), [], ""
    for w in words:
        test = (cur + " " + w).strip()
        if draw.textlength(test, font=font) <= max_w:
            cur = test
        else:
            lines.append(cur); cur = w
    if cur:
        lines.append(cur)
    return lines or [""]


def _rounded(draw, box, radius, fill):
    draw.rounded_rectangle(box, radius=radius, fill=fill)


def _draw_state(messages, n_visible, scheme, title, show_header):
    """Render the chat with the first n_visible messages shown."""
    dark = scheme == "dark"
    bg = (0, 0, 0) if dark else (255, 255, 255)
    text_other = (235, 235, 235) if dark else (20, 20, 20)
    other_bubble = (58, 58, 60) if dark else (233, 233, 235)
    sender_bubble = (10, 132, 255)
    sender_text = (255, 255, 255)

    img = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(img)
    font = _font(34)
    head_f = _font(38, True)

    y = PAD
    if show_header:
        d.text((W // 2, y + 20), title or "Messages", font=head_f, fill=text_other, anchor="mt")
        y += 110
        d.line((0, y, W, y), fill=(80, 80, 80) if dark else (220, 220, 220), width=2)
        y += 30

    for msg in messages[:n_visible]:
        is_sender = msg.get("sender", False)
        lines = _wrap(d, msg["text"], font, BUBBLE_MAX - 48)
        bubble_w = min(BUBBLE_MAX, max(d.textlength(ln, font=font) for ln in lines) + 48)
        bubble_h = len(lines) * LINE_H + 28
        if is_sender:
            x1 = W - PAD - bubble_w
            fill, tcol = sender_bubble, sender_text
        else:
            x1 = PAD
            fill, tcol = other_bubble, text_other
        _rounded(d, (x1, y, x1 + bubble_w, y + bubble_h), 28, fill)
        ty = y + 14
        for ln in lines:
            d.text((x1 + 24, ty), ln, font=font, fill=tcol)
            ty += LINE_H
        y += bubble_h + GAP
    return img


def render_frames(messages, out_dir, scheme="dark", title="Messages", show_header=True,
                  fps=30, hold_seconds=1.2):
    """Render a frame sequence; each message holds for `hold_seconds`.

    Returns (frame_pattern, fps, total_frames).
    """
    os.makedirs(out_dir, exist_ok=True)
    frames_per_step = int(fps * hold_seconds)
    idx = 0
    for n in range(1, len(messages) + 1):
        frame = _draw_state(messages, n, scheme, title, show_header)
        for _ in range(frames_per_step):
            frame.save(os.path.join(out_dir, f"f_{idx:05d}.png"))
            idx += 1
    return os.path.join(out_dir, "f_%05d.png"), fps, idx
