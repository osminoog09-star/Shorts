"""Субтитры на всю речь через GigaAM v3_e2e_rnnt (пунктуация, русский). Запуск: C:\\M1lash\\venv\\asr\\Scripts\\python.exe subs_gigaam.py
Окна — те же, что в subs.py (серия + Shorts). Куски речи ≤18 с режем Silero VAD из faster-whisper. → subs.json"""
import json, os, re, tempfile, torch
os.add_dll_directory(os.path.join(os.path.dirname(torch.__file__), "lib"))
import numpy as np, soundfile as sf
from pathlib import Path
import gigaam
from faster_whisper.vad import get_speech_timestamps, VadOptions
from src import W, locate, hms
from ep1 import SEG
from shorts import SHORTS

T = lambda x: hms(x) if isinstance(x, str) else float(x)
win = []
for s in SEG + [x for sh in SHORTS.values() for x in sh["seg"]]:
    if s.get("k") in ("n", "s", "f") and "a" in s:
        win.append([T(s["a"]) - 1.0, T(s["b"]) + 0.5])
win.sort(); merged = []
for a, b in win:
    if merged and a <= merged[-1][1]: merged[-1][1] = max(merged[-1][1], b)
    else: merged.append([a, b])

def load_local(d=Path(r"C:\M1lash\models\gigaam-v3-e2e-rnnt")):
    """Веса с HF (ai-sage/GigaAM-v3@e2e_rnnt, SHA-256 сверены), классы — из проверенного пакета gigaam; удалённый код HF не исполняется."""
    from omegaconf import OmegaConf
    from gigaam.model import GigaAMASR
    raw = json.loads((d / "config.json").read_text(encoding="utf-8"))["cfg"]["model"]["cfg"]
    s = json.dumps(raw)
    for a_, b_ in (("modeling_gigaam.FeatureExtractor", "gigaam.preprocess.FeatureExtractor"),
                   ("modeling_gigaam.ConformerEncoder", "gigaam.encoder.ConformerEncoder"),
                   ("modeling_gigaam.RNNTHead", "gigaam.decoder.RNNTHead"),
                   ("modeling_gigaam.RNNTGreedyDecoding", "gigaam.decoding.RNNTGreedyDecoding")):
        s = s.replace(a_, b_)
    assert "modeling_gigaam" not in s, "в конфиге остались ссылки на код HF"
    cfg = OmegaConf.create(json.loads(s))
    cfg.decoding.model_path = str(d / "tokenizer.model")
    m = GigaAMASR(cfg)
    sd = torch.load(d / "pytorch_model.bin", map_location="cpu", weights_only=True)
    sd = {k[len("model."):] if k.startswith("model.") else k: v for k, v in sd.items()}
    missing, unexpected = m.load_state_dict(sd, strict=False)
    print("missing", len(missing), "unexpected", len(unexpected), missing[:3], unexpected[:3])
    assert not missing, "веса не подошли"
    return m.eval().to("cuda")


G = json.load(open(W / "gains.json", encoding="utf-8"))
model = load_local()
SR = 16000
tmp = Path(tempfile.mkdtemp(prefix="gigaam_"))
out = []
for a, b in merged:
    f, la = locate(a)
    for who in ("mic", "discord"):
        x, _ = sf.read(str(W / "wav" / f"{Path(f).stem}_{who}.wav"), start=int(max(0, la) * SR), stop=int((la + b - a) * SR), dtype="float32")
        x = np.clip(x * G[f][who], -1, 1)
        if len(x) < SR // 2: continue
        sp = get_speech_timestamps(x, VadOptions(min_silence_duration_ms=350, speech_pad_ms=150, max_speech_duration_s=18))
        for k, r in enumerate(sp):
            seg = x[r["start"]:r["end"]]
            if len(seg) < int(0.3 * SR): continue
            p = tmp / f"c_{who}_{k}.wav"; sf.write(str(p), seg, SR)
            res = model.transcribe(str(p), word_timestamps=True)
            off = a + r["start"] / SR
            words = [(off + w.start, off + w.end, w.text.strip()) for w in (res.words or []) if w.text.strip()]
            cur = []
            for w in words:
                if cur and (w[0] - cur[-1][1] > 0.6 or len(" ".join(t for _, _, t in cur)) > 38 or cur[-1][2][-1:] in ".?!"):
                    out.append([cur[0][0], cur[-1][1], who[0], " ".join(t for _, _, t in cur)]); cur = []
                cur.append(w)
            if cur: out.append([cur[0][0], cur[-1][1], who[0], " ".join(t for _, _, t in cur)])

clean = []
for t0, t1, who, txt in sorted(out):
    toks = txt.split()
    if not toks: continue
    if len(toks) >= 4 and len(set(t.lower().strip(",.!?") for t in toks)) <= 2: continue
    clean.append([round(t0, 2), round(max(t1, t0 + 0.8), 2), who, txt])
old = W / "subs.json"
if old.exists(): old.replace(W / "subs_whisper.json")
json.dump(clean, open(W / "subs.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("windows", len(merged), "phrases", len(clean))
