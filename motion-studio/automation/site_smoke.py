#!/usr/bin/env python3
"""Offline static UI integrity and deployment asset test for M1lash Studio v2."""
import html.parser
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
IDS={
 "topic","brief","format","duration","language","voice","sources","depth",
 "styleChoices","styleDetails","allStyles","agentSelections","agentCards",
 "submitJob","exportConfig","refreshJobs","queueList","newsList",
 "newsStatus","newsCategory","refreshNews","outlierStatus","outlierList","refreshOutliers","referenceUrl","analyzeYoutube",
 "referenceStatus","sumFormat","sumDuration","sumStyle","sumVoice",
 "sumAgents","readiness","saveMessage","clearDraft","sectionTitle",
 "tab-create","tab-news","tab-reference","tab-agents","tab-styles",
 "tab-queue","tab-settings",
}

class Doc(html.parser.HTMLParser):
 def __init__(self):super().__init__();self.ids=[];self.scripts=[];self.links=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if "id" in a:self.ids.append(a["id"])
  if tag=="script" and a.get("src"):self.scripts.append(a["src"])
  if tag=="link" and a.get("rel")=="stylesheet":self.links.append(a.get("href"))

def main():
 html=(ROOT/"index.html").read_text(encoding="utf-8")
 parser=Doc();parser.feed(html)
 missing=IDS-set(parser.ids)
 if missing:raise SystemExit("missing interactive ids: "+repr(missing))
 if len(set(parser.ids))!=len(parser.ids):raise SystemExit("duplicate HTML ids")
 for item in [*parser.scripts,*parser.links]:
  if ".." in Path(item).parts or item.startswith(("http:","https:")):
   raise SystemExit("unexpected dashboard external code asset "+item)
  if not (ROOT/item).is_file():raise SystemExit("missing dashboard asset "+item)
 if not (ROOT/"renderer.html").is_file():raise SystemExit("missing legacy renderer")
 if not (ROOT/"data/news.json").is_file():raise SystemExit("missing RSS data")
 news=json.loads((ROOT/"data/news.json").read_text(encoding="utf-8"))
 if "items" not in news:raise SystemExit("missing items in news JSON")
 print("M1lash dashboard: IDs, assets, legacy renderer and news JSON PASS")

if __name__=="__main__":main()
