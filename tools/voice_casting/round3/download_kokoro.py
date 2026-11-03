import os
os.environ['HF_HUB_DISABLE_TELEMETRY']='1';os.environ['HF_HUB_DISABLE_XET']='1';os.environ['ORT_DISABLE_TELEMETRY']='1'
from pathlib import Path
import sys
from huggingface_hub import snapshot_download
B=Path(sys.argv[1]).resolve()
p=snapshot_download('zaakirio/kokoro-ru',allow_patterns=['onnx/model.onnx','config.json','kokoro-config.json','ru_g2p.py','espeak-data/*','voices/sveta.bin','voices/masha.bin','README.md'],cache_dir=str(B/'models'),max_workers=3)
(B/'kokoro_model_path.txt').write_text(p);print('KOKORO_CACHED',flush=True)
