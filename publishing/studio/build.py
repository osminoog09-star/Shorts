#!/usr/bin/env python3
"""Собирает страницу «Студия M1lash» из publishing/queue.json и PUBLISH.md роликов.

Запуск из корня репо:  python3 publishing/studio/build.py
Результат: publishing/studio/dist/studio.html (публикует Claude как артефакт).
"""
import base64
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
HERE = Path(__file__).resolve().parent
RAW = "https://raw.githubusercontent.com/osminoog09-star/Shorts/main/"

SECTION_KEYS = {
    "название": "title",
    "описание": "description",
    "теги": "tags",
    "закреп": "pinned",
    "первый комментарий": "pinned",
    "настройки": "settings",
}


def parse_publish(md_path: Path) -> dict:
    out = {}
    if not md_path.is_file():
        return out
    cur = None
    buf = []

    def flush():
        if cur:
            out[cur] = "\n".join(buf).strip()

    for line in md_path.read_text(encoding="utf-8").splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            flush()
            cur = SECTION_KEYS.get(m.group(1).strip().lower())
            buf = []
        elif cur:
            buf.append(line)
    flush()
    settings = out.get("settings", "")
    if "pinned" not in out:
        m = re.search(r"закреп[^:]*:\s*«(.+?)»", settings, re.I)
        if m:
            out["pinned"] = m.group(1)
    if "tags" not in out:
        tags = re.findall(r"#[\wА-Яа-яЁё]+", out.get("description", ""))
        if tags:
            out["tags"] = " ".join(dict.fromkeys(t for t in tags if t.lower() != "#shorts"))
    return out


def thumb_data_uri(item: dict) -> str | None:
    src = item.get("thumb")
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "t.jpg"
        if src and (ROOT / src).is_file():
            cmd = ["ffmpeg", "-v", "error", "-y", "-i", str(ROOT / src), "-vf", "scale=480:-2", "-q:v", "5", str(out)]
        else:
            mp4 = item.get("mp4") or ""
            if mp4.startswith("http") or not (ROOT / mp4).is_file():
                return None
            cmd = ["ffmpeg", "-v", "error", "-y", "-ss", "1.5", "-i", str(ROOT / mp4), "-frames:v", "1",
                   "-vf", "scale=-2:420", "-q:v", "5", str(out)]
        try:
            subprocess.run(cmd, check=True, timeout=60)
        except Exception as exc:  # нет ffmpeg или битый файл — страница без превью
            print(f"warn: thumb {item['id']}: {exc}", file=sys.stderr)
            return None
        return "data:image/jpeg;base64," + base64.b64encode(out.read_bytes()).decode()


def main() -> None:
    queue = json.loads((ROOT / "publishing/queue.json").read_text(encoding="utf-8"))
    items = []
    for it in queue["items"]:
        meta = parse_publish(ROOT / it["publish_md"]) if it.get("publish_md") else {}
        mp4 = it.get("mp4") or ""
        items.append({
            "id": it["id"],
            "kind": it.get("kind", "short"),
            "author": it.get("author", ""),
            "status": it.get("status", "draft"),
            "slot": it.get("slot"),
            "style": it.get("style", ""),
            "note": it.get("note", ""),
            "youtube_id": it.get("youtube_id"),
            "mp4": mp4 if mp4.startswith("http") else (RAW + mp4 if mp4 else ""),
            "title": meta.get("title") or it.get("title", ""),
            "description": meta.get("description", ""),
            "tags": meta.get("tags", ""),
            "pinned": meta.get("pinned", ""),
            "settings": meta.get("settings", ""),
            "thumb": thumb_data_uri(it),
        })
    tpl = (HERE / "template.html").read_text(encoding="utf-8")
    data = json.dumps(items, ensure_ascii=False).replace("</", "<\\/")
    from datetime import datetime, timezone, timedelta
    meta = {"paused": bool(queue.get("paused")),
            "built": datetime.now(timezone(timedelta(hours=2))).strftime("%d.%m.%Y %H:%M")}
    html = tpl.replace("/*__DATA__*/[]", data).replace("/*__META__*/{}", json.dumps(meta, ensure_ascii=False))
    dist = HERE / "dist"
    dist.mkdir(exist_ok=True)
    (dist / "studio.html").write_text(html, encoding="utf-8")
    print(f"ok: {len(items)} паспортов → {dist / 'studio.html'}")


if __name__ == "__main__":
    main()
