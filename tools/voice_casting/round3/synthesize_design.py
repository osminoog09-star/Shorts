import os
for k,v in {'ORT_DISABLE_TELEMETRY':'1','HF_HUB_DISABLE_TELEMETRY':'1','HF_HUB_OFFLINE':'1','TRANSFORMERS_OFFLINE':'1','GRADIO_ANALYTICS_ENABLED':'False','DO_NOT_TRACK':'1','TOKENIZERS_PARALLELISM':'false'}.items():os.environ[k]=v
from pathlib import Path
import sys
import torch,soundfile as sf,json,time
from qwen_tts import Qwen3TTSModel
B=Path(sys.argv[1]).resolve();torch.set_num_threads(4);torch.set_num_interop_threads(1);T='Подожди, а почему искусственный интеллект так уверенно отвечает, даже когда ошибается?'
model=Qwen3TTSModel.from_pretrained((B/'design_model_path.txt').read_text().strip(),device_map='cpu',dtype=torch.bfloat16,attn_implementation='eager',local_files_only=True)
prompts=[{'id':'03_designed_warm','label':'Новый синтетический: тёплая низкая подача','seed':151,'instruct':'A native Russian-speaking woman in her early thirties, with a warm, velvety, medium-low female voice. Natural Russian pronunciation and lexical stress, clear consonants. Calm and genuinely curious conversational delivery, as a thoughtful podcast co-host asking a short question. Moderate pace, subtle intonation. Not breathy, not childish, not a newsreader. No exaggerated acting.'},{'id':'04_designed_clear','label':'Новый синтетический: ясная разговорная подача','seed':213,'instruct':'A native Russian-speaking adult woman with a clear, smooth, medium-pitched female voice, slightly warm and lively. Authentic natural Russian pronunciation, conversational rhythm and a softly questioning ending. An attentive intelligent conversation partner speaking naturally to a low-voiced man. Confident but friendly and unhurried, not a commercial or a theatrical character.'}]
for p in prompts:
 torch.manual_seed(p['seed']);print('START',p['id'],flush=True);w,sr=model.generate_voice_design(text=T,language='Russian',instruct=p['instruct'],max_new_tokens=260,temperature=.7);sf.write(B/(p['id']+'_raw.wav'),w[0],sr);p['duration']=len(w[0])/sr;print('DONE',p['id'],p['duration'],flush=True)
(B/'design_manifest.json').write_text(json.dumps({'model':'Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign','text':T,'voices':prompts,'note':'Descriptions are requested attributes, not independently heard/verified qualities.'},ensure_ascii=False,indent=2))
