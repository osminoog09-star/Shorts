#!/usr/bin/env python3
"""M1lash actual stage runner: sourced dossier -> optional 7-chapter draft -> director/
asset prompts -> honest stage manifest. No fake renders, no publishing, no credentials in
artifacts. Full-quality 21min film/audio requires separate real media engines and review.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

HERE=Path(__file__).resolve().parent
ROOT=HERE.parent
sys.path.insert(0,str(HERE))
from prepare_job import parse_issue, original_plan, prepare

DRAFT_MODEL="gemini-3.8-flash"
PACKS={"54":ROOT/"research"/"tobacco-history-54.json"}
STAGE_NAMES=["research","factcheck","script","director","image","animation","voice","editor","quality","youtube"]
VALID_STATES={"ready","needs_review","blocked"}
MAX_SCRIPT_CHARS=85000
MAX_MODEL_CHAPTERS=8


def valid_sources(pack):
    sources=pack.get("sources",[])
    if len(sources)<2 or len(sources)>30:return False
    ids=set()
    for item in sources:
        if not isinstance(item,dict) or not isinstance(item.get("id"),str):
            return False
        if item["id"] in ids:return False
        ids.add(item["id"])
        url=item.get("url","")
        x=urllib.parse.urlsplit(url)
        if x.scheme!="https" or not x.hostname or x.username or x.password or x.fragment:
            return False
        if x.hostname in ("localhost","127.0.0.1") or x.hostname.endswith(".local"):
            return False
    claims=pack.get("claims",[])
    if not claims:return False
    for c in claims:
        refs=c.get("sources",[])
        if len(set(refs))<2 or any(ref not in ids for ref in refs):
            return False
    return True


def load_pack(issue_number):
    path=PACKS.get(str(issue_number))
    if path is None or not path.is_file():return None
    pack=json.loads(path.read_text(encoding="utf-8"))
    if issue_number not in pack.get("issue_numbers",[]) or not valid_sources(pack):
        raise ValueError("research pack has invalid issue/source references")
    return pack


def write_json(path,data):
    Path(path).write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")


def research_documents(pack,out):
    lookup={s["id"]:s for s in pack["sources"]}
    lines=[
        "# Исследователь: научно-историческое досье","",
        "**Источник:** отобранные и сверенные редакцией ссылки; не автоматическое чтение всего текста в текущем запуске.",
        "**Статус:** утверждения требуют ручной проверки первоисточников перед публикацией.","",
        "## Редакционная идея",pack["editorial_angle"],"",
        "## Ограничения интерпретации",
        *["- "+x for x in pack.get("warnings",[])],"",
        "## Утверждения и обязательные ссылки",
    ]
    for item in pack["claims"]:
        lines+=["",f"### {item['id']}: {item['statement']}",
                *["- "+lookup[r]["publisher"]+" — "+lookup[r]["url"] for r in item["sources"]],
                "- Статус: SOURCED_NEEDS_HUMAN_FACT_CHECK"]
    lines+=["","## Каталог источников",
            *["- "+s["id"]+": "+s["publisher"]+" — "+s["url"] for s in pack["sources"]]]
    (out/"research.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    write_json(out/"facts.json",{
        "status":"SOURCED_NEEDS_HUMAN_VERIFICATION",
        "checked_on":pack.get("checked_on"),
        "sources":pack["sources"],
        "claims":[{**c,"release_status":"REQUIRES_FACT_CHECK"} for c in pack["claims"]],
    })


def model_generate(prompt,key,*, request=None):
    """Official text generateContent API. Fail closed. Secrets stay in request header."""
    if not key:raise ValueError("Gemini secret absent")
    payload={
        "contents":[{"role":"user","parts":[{"text":prompt}]}],
        "generationConfig":{"temperature":0.35,"maxOutputTokens":3000},
    }
    if request is not None:
        data=request(payload)
    else:
        url=f"https://generativelanguage.googleapis.com/v1beta/models/{DRAFT_MODEL}:generateContent"
        headers={"Content-Type":"application/json","x-goog-api-key":key}
        req=urllib.request.Request(url,data=json.dumps(payload).encode("utf-8"),
                                   headers=headers,method="POST")
        try:
            with urllib.request.urlopen(req,timeout=110) as resp:
                data=json.loads(resp.read(1_000_000))
        except urllib.error.HTTPError as ex:
            raise RuntimeError("Gemini HTTP error "+str(ex.code)) from None
        except (urllib.error.URLError,TimeoutError):
            raise RuntimeError("Gemini network unavailable") from None
    chunks=[]
    for candidate in data.get("candidates",[])[:1]:
        for p in (candidate.get("content") or {}).get("parts",[]):
            if isinstance(p.get("text"),str):chunks.append(p["text"])
    result="\n".join(chunks).strip()
    if len(result)<250 or len(result)>18000:
        raise ValueError("empty/truncated/oversized model chapter")
    return result


def count_words(text):
    return len(re.findall(r"[\wЁёА-я-]+",text,re.UNICODE))


def scripted_chapters(pack,job,out,key,*, generate=model_generate):
    chapters=pack["chapters"]
    if not 1<=len(chapters)<=MAX_MODEL_CHAPTERS:
        raise ValueError("invalid chapter count")
    if job["format"]!="long" or job["language"]!="ru":
        raise ValueError("curated pack designed for RU longform only")
    refs={s["id"]:s for s in pack["sources"]}
    gathered=[]
    for i,ch in enumerate(chapters,1):
        span=int(ch["end_s"])-int(ch["start_s"])
        goal=round(span/60*128)
        facts=[f for f in pack["claims"] if f.get("chapter")==i]
        # Include all verified leads, not only chapter-specific ones, to avoid gaps.
        if not facts:facts=pack["claims"]
        evidence="\n".join(f"[{c['id']}] {c['statement']} — "+
                           "; ".join(refs[r]["url"] for r in c["sources"])
                           for c in facts)
        prompt=(
            "Ты сценарист документального русскоязычного канала M1lash. Напиши ТОЛЬКО "
            "оригинальный дикторский текст для одной главы (без списков кадров и украшений). "
            "Главный голос Дима. Не выдумывай исторические реплики, даты и цифры, "
            "не цитируй длинные фрагменты источников. Утверждения из источников помечай "
            "токенами [F01], [F02] по релевантности. Если нет доказательства, честно скажи, "
            "что вопрос открыт. Никакой пропаганды курения, медицинских советов, "
            "технических инструкций для изготовления/употребления никотиновой продукции. "
            f"ТЕМА: {job['topic']}\nГЛАВА {i}/{len(chapters)}: {ch['title']}\n"
            f"Длительность главы {span} секунд; целевая длина ~{goal} русских слов. "
            "Цель — содержательный, увлекательный научно-исторический рассказ, "
            "без воды и повторов.\n"
            f"Редакционный контекст: {ch['narrative']}\n"
            "Допустимые источниковые утверждения:\n"+evidence+"\n"
            "Не используй статистику или подробности вне предоставленного источникового досье."
        )
        chapter=generate(prompt,key)
        actual=count_words(chapter)
        (out/f"script_chapter_{i:02d}.md").write_text(
            f"# {ch['title']}\n\n{chapter}\n",encoding="utf-8")
        gathered.append({"chapter":i,"title":ch["title"],"words":actual,
                         "target_words":goal,"script":chapter})
    combined="\n\n".join(f"## {x['chapter']}. {x['title']}\n\n{x['script']}"
                        for x in gathered)
    (out/"script_draft_ru.md").write_text(
        "# Сценарий Димы — ЧЕРНОВИК, НЕ ДОПУЩЕН К ОЗВУЧКЕ\n\n"+
        "Предполагаемые 25 минут требуют проверки фактов и реального тайминга TTS.\n\n"+
        combined+"\n",encoding="utf-8")
    total=sum(x["words"] for x in gathered)
    expected=int(job["duration_s"]/60*128)
    errors=[]
    if total<round(expected*0.82):
        errors.append(f"too short: {total} words, goal {expected}")
    if total>round(expected*1.4):
        errors.append(f"too long: {total} words, goal {expected}")
    if not re.search(r"\[F\d{2}\]",combined):
        errors.append("missing evidence markers")
    write_json(out/"script_metrics.json",{
        "draft_words":total,"target_words":expected,
        "text_model":DRAFT_MODEL,"voice":"ru-RU-DmitryNeural",
        "chapters":[{"chapter":x["chapter"],"words":x["words"],
                     "target_words":x["target_words"]} for x in gathered],
        "status":"DRAFT_NEEDS_EDITOR_AND_SOURCE_REVIEW" if not errors else "BLOCKED_INCOMPLETE_DRAFT",
        "issues":errors,
    })
    return not errors


def director_cards(pack,out):
    lines=["# Режиссёр: X05-D25 — историческая реконструкция, НЕ готовые кадры","",
           "Задание режиссёра: 25 минут не могут быть статичными иллюстрациями. "
           "Для каждого блока потребуются отдельные проверенные сцены, действия, "
           "смысловое движение и монтажные планы.","",
           "Каждая реконструкция явно обозначается как реконструкция; никаких "
           "выдуманных персонажей, исторических фото или событий, "
           "которые зритель примет за подлинную запись.",""]
    cue=[]
    for i,ch in enumerate(pack["chapters"],1):
        cue.append({"chapter":i,"start_s":ch["start_s"],"end_s":ch["end_s"],
                    "title":ch["title"],"visual_direction":ch["visual"],
                    "media_status":"PROMPT_ONLY_NO_ASSET",
                    "requires":"storyboard, rights-reviewed original illustrations, shot-level animatic"})
        lines.extend([f"## {i} — {ch['start_s']}–{ch['end_s']} сек: {ch['title']}",
                      f"Сценарный замысел: {ch['narrative']}",
                      f"Промпт изображений: {ch['visual']}. X05, 2.5D, историческая аккуратность, "
                      "оригинальная многоплановая композиция; мягкий свет, планы с реальным параллаксом.",
                      "Негативный промпт: показная сенсация, AI-слайдшоу, "
                      "неправдоподобный текст, современные предметы в древней сцене, копии чужих кадров.",""])
    (out/"director_and_art_prompts.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    write_json(out/"scene_cues_provisional.json",{
        "purpose":"editorial storyboard prompts, not frame-accurate timeline",
        "duration_requested_s":pack["chapters"][-1]["end_s"],
        "renderable":False,"cues":cue,
    })


def stage(id,status,reason,files=None):
    if id not in STAGE_NAMES or status not in VALID_STATES:
        raise ValueError("invalid pipeline state")
    return {"id":id,"status":status,"reason":reason[:260],"files":files or []}


def run(issue,output,*,key="",text_ai_enabled=False,generate=model_generate):
    job=parse_issue(issue)
    output=Path(output)
    output.mkdir(parents=True,exist_ok=True)
    issue_number=issue["number"]
    # Existing preparer covers only metadata and reference analysis.
    prep=prepare(job,output)
    if job["request"]!="prepare_only":
        stages=[stage("research","needs_review",
                      "YouTube reference researched only when licensed API/video available",
                      ["source.json","reference_analysis.md"])]
        status="REFERENCE_REVIEW_ONLY"
    else:
        pack=load_pack(issue_number)
        stages=[]
        scripted=False
        if pack and job["language"]=="ru" and job["format"]=="long":
            research_documents(pack,output)
            director_cards(pack,output)
            stages.extend([
                stage("research","ready","Real source-linked historical dossier built for this topic",
                      ["research.md","facts.json"]),
                stage("factcheck","needs_review",
                      "Source links collected; historical nuance and statistics require editorial source verification",
                      ["facts.json"]),
            ])
            if text_ai_enabled and key:
                try:
                    scripted=scripted_chapters(pack,job,output,key,generate=generate)
                    stages.append(stage("script","needs_review" if scripted else "blocked",
                        "Seven actual text chapters generated; editorial/source/voice timing check required"
                        if scripted else "Draft too short or incomplete, no TTS or video release",
                        ["script_draft_ru.md","script_metrics.json"]))
                except (ValueError,RuntimeError,OSError) as e:
                    stages.append(stage("script","blocked",
                        "Text model failed or incomplete: "+type(e).__name__))
            else:
                stages.append(stage("script","blocked",
                    "Set GEMINI_API_KEY secret + M1LASH_TEXT_AI_ENABLED=true to draft full spoken script"))
            stages.extend([
                stage("director","needs_review","Seven factual act directions and planned timecodes; no final shotlist",
                      ["director_and_art_prompts.md","scene_cues_provisional.json"]),
                stage("image","blocked","Original images not generated; art prompts only",
                      ["director_and_art_prompts.md"]),
            ])
        else:
            stages.extend([
                stage("research","blocked","No reviewed source pack for issue/topic; no fabricated research"),
                stage("factcheck","blocked","Cannot fact-check without independently sourced material"),
                stage("script","blocked","No approved factual dossier and script engine cannot proceed"),
                stage("director","blocked","No evidence-based shotlist"),
                stage("image","blocked","No source-grounded original visual assets"),
            ])
        stages.extend([
            stage("animation","blocked","No actual motion assets and scene render; prompts do not count"),
            stage("voice","blocked","Dima voice track NOT synthesized; script approval + TTS gate missing"),
            stage("editor","blocked","No verified synchronized MP4 >=21:00 or original shot materials"),
            stage("quality","blocked","No audiovisual listening/visual audit or duration release gate"),
            stage("youtube","blocked","Public release requires rights review and owner's separate approval"),
        ])
        status="EDITORIAL_PACKAGE_NEEDS_REVIEW" if pack else "BLOCKED_NEEDS_SOURCE_RESEARCH"
    # This status is safe to show to the user; no credentials or sensitive model errors.
    report={"schema":1,"issue_number":issue_number,"title":job.get("topic",issue["title"]),
            "run_time_utc":dt.datetime.now(dt.timezone.utc).isoformat(),
            "status":status,"publish":False,"stages":stages,
            "output_is_final_video":False,
            "note":"Status per actual files; no fake images, voice or MP4."}
    write_json(output/"stages.json",report)
    lines=["# M1lash Studio: выполненные этапы для задачи #"+str(issue_number),"",
           "Задание: "+report["title"],"", "| Агент | Статус | Результат |",
           "|---|---|---|"]
    for st in stages:
        lines.append("| "+st["id"]+" | "+st["status"]+" | "+st["reason"].replace("|","/")+" |")
    lines.extend(["","**Нет готового MP4, публикации YouTube и утверждённой озвучки.**",
                  "Полный отчёт: stages.json. Пакет исследования доступен в артефакте GitHub Actions."])
    (output/"PROGRESS.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return report


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--event",required=True)
    p.add_argument("--out",default="studio-output")
    args=p.parse_args()
    event=json.loads(Path(args.event).read_text(encoding="utf-8"))
    report=run(
        event["issue"],args.out,key=os.environ.get("GEMINI_API_KEY",""),
        text_ai_enabled=os.environ.get("M1LASH_TEXT_AI_ENABLED")=="true")
    print("M1lash pipeline",report["status"],"issue",report["issue_number"],
          "stages",len(report["stages"]),"final_video",report["output_is_final_video"])


if __name__=="__main__":
    main()
