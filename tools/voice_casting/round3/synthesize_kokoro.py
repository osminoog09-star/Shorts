import os
os.environ['ORT_DISABLE_TELEMETRY']='1';os.environ['HF_HUB_DISABLE_TELEMETRY']='1';os.environ['DO_NOT_TRACK']='1'
from pathlib import Path
import sys
import json,sys,numpy as np,soundfile as sf
import onnxruntime as ort
B=Path(sys.argv[1]).resolve();M=Path((B/'kokoro_model_path.txt').read_text().strip());sys.path.insert(0,str(M))
from ru_g2p import RuG2P
from phonemizer.backend.espeak.wrapper import EspeakWrapper
from misaki import espeak as misaki_espeak
EspeakWrapper.set_data_path(str(M/'espeak-data'))
# Use the upstream explicit-stress frontend for this one carefully marked sentence.
# RUAccent is not needed when all stresses are provided explicitly.
g=RuG2P.__new__(RuG2P);g._espeak=misaki_espeak.EspeakG2P(language='ru');cfg=json.loads((M/'kokoro-config.json').read_text());g.vocab=set(cfg['vocab']);g.reduction=True
text='Подожди́, а почему́ иску́сственный интелле́кт так уве́ренно отвеча́ет, да́же когда́ ошиба́ется?'
ipa,oov=g._from_marked(text);assert not oov,oov;print('IPA',ipa,flush=True)
ids=[cfg['vocab'][c] for c in ipa if c in cfg['vocab']];options=ort.SessionOptions();options.intra_op_num_threads=4;options.inter_op_num_threads=1;options.enable_profiling=False;options.log_severity_level=3
sess=ort.InferenceSession(str(M/'onnx/model.onnx'),sess_options=options,providers=['CPUExecutionProvider']);out=[]
for i,speaker in enumerate(['sveta','masha'],1):
 style=np.fromfile(M/f'voices/{speaker}.bin',dtype=np.float32).reshape(510,256);a=sess.run(None,{'input_ids':np.array([[0,*ids,0]],np.int64),'style':style[len(ipa)-1][None],'speed':np.ones(1,np.float32)})[0].reshape(-1);sf.write(B/f'{i:02d}_kokoro_{speaker}_raw.wav',a,24000);out.append({'id':f'{i:02d}_kokoro_{speaker}','speaker':speaker,'duration':len(a)/24000});print('DONE',speaker,len(a)/24000,flush=True)
(B/'kokoro_manifest.json').write_text(json.dumps({'model':'zaakirio/kokoro-ru','model_license_declared':'OpenRAIL','source_claim':'author states studio consented actors; exact commercial conditions not independently legally audited','text_accented':text,'ipa':ipa,'voices':out},ensure_ascii=False,indent=2))
