"""Render static social cards (Reddit post, tweet) to PNG via Pillow.

These are generic, original card layouts (not a clone of any platform's exact assets).
"""
from PIL import Image, ImageDraw, ImageFont
import os

W = 900


def _font(size, bold=False):
    # fall back to default bitmap font if no TTF available
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
    return lines


def reddit_card(subreddit, username, title, body, upvotes, comments, out_path):
    title_f, meta_f, body_f = _font(40, True), _font(26), _font(30)
    pad = 40
    img = Image.new("RGBA", (W, 600), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    y = pad
    d.text((pad, y), f"r/{subreddit}  •  u/{username}", font=meta_f, fill=(120, 120, 120)); y += 50
    for ln in _wrap(d, title, title_f, W - 2 * pad):
        d.text((pad, y), ln, font=title_f, fill=(20, 20, 20)); y += 50
    y += 10
    for ln in _wrap(d, body, body_f, W - 2 * pad):
        d.text((pad, y), ln, font=body_f, fill=(40, 40, 40)); y += 40
    y += 20
    d.text((pad, y), f"▲ {upvotes}    💬 {comments}", font=meta_f, fill=(120, 120, 120))
    img = img.crop((0, 0, W, min(600, y + 80)))
    img.save(out_path)
    return out_path


def tweet_card(name, handle, text, out_path):
    name_f, handle_f, body_f = _font(36, True), _font(28), _font(34)
    pad = 40
    img = Image.new("RGBA", (W, 500), (255, 255, 255, 255))
    d = ImageDraw.Draw(img)
    y = pad
    d.text((pad, y), name, font=name_f, fill=(20, 20, 20))
    d.text((pad, y + 42), f"@{handle}", font=handle_f, fill=(120, 120, 120)); y += 100
    for ln in _wrap(d, text, body_f, W - 2 * pad):
        d.text((pad, y), ln, font=body_f, fill=(20, 20, 20)); y += 46
    img = img.crop((0, 0, W, min(500, y + 40)))
    img.save(out_path)
    return out_path
