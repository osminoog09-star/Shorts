#!/usr/bin/env python3
"""Подключить ВСЕ скилы репо агентам: .claude/skills (Claude) и .agents/skills (GPT/Codex).

Источник правды — skills/<имя>/ и skills/ext/<имя>/ (у кого есть SKILL.md). В агентских папках
должны быть только ссылки на них — не копии (копии устаревают). Запускать после добавления скила:
    python3 scripts/sync_skills.py          # починить
    python3 scripts/sync_skills.py --check  # только проверить (код 1, если что-то не так)
huashu-motion — git submodule: на новой машине сначала `git submodule update --init skills/ext/huashu-motion`.
"""
import os, shutil, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TARGETS = [ROOT / ".claude/skills", ROOT / ".agents/skills"]
SPECIAL = {"huashu-motion": ROOT / "skills/ext/huashu-motion/skills/huashu-motion"}


def sources():
    out = {}
    for base in (ROOT / "skills", ROOT / "skills/ext"):
        for d in sorted(base.iterdir()):
            if d.is_dir() and (d / "SKILL.md").is_file() and d.name != "ext":
                out.setdefault(d.name, d)
    out.update(SPECIAL)
    return out


def main():
    check = "--check" in sys.argv
    problems = []
    for tgt in TARGETS:
        tgt.mkdir(parents=True, exist_ok=True)
        for name, src in sources().items():
            link = tgt / name
            rel = os.path.relpath(src, tgt)
            ok = link.is_symlink() and os.readlink(link) == rel
            if ok:
                continue
            problems.append(f"{link.relative_to(ROOT)} -> {rel}")
            if check:
                continue
            if link.is_symlink() or link.is_file():
                link.unlink()
            elif link.is_dir():
                shutil.rmtree(link)
            link.symlink_to(rel)
        # orphans: real folders/files in agent dirs that are not links to a repo skill (copies go stale)
        for link in sorted(tgt.iterdir()):
            if link.name not in sources() and not link.is_symlink():
                problems.append(f"{link.relative_to(ROOT)}: копия/лишнее — перенести в skills/ и подключить ссылкой")
    for p in problems:
        print(("НЕ ТАК: " if check else "исправлено: ") + p)
    print(f"скилов: {len(sources())}, проблем: {len(problems)}")
    sys.exit(1 if check and problems else 0)


if __name__ == "__main__":
    main()
