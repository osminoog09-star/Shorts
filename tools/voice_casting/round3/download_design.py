import os
os.environ['ORT_DISABLE_TELEMETRY']='1';os.environ['HF_HUB_DISABLE_TELEMETRY']='1';os.environ['HF_HUB_DISABLE_XET']='1'
from pathlib import Path
import sys
from huggingface_hub import snapshot_download
B=Path(sys.argv[1]).resolve()
p=snapshot_download('Qwen/Qwen3-TTS-12Hz-1.7B-VoiceDesign',allow_patterns=['*.json','*.safetensors','*.txt','speech_tokenizer/*'],cache_dir=str(B/'models'),max_workers=3)
(B/'design_model_path.txt').write_text(p);print('MODEL_CACHED',flush=True)
