#!/usr/bin/env python3
"""Depth maps for painted keyframes (Depth-Anything-V2-Small, Apache-2.0) → <id>_depth.png (16-bit, near = white).
usage: py -3.11 depth.py <frames_dir> [ids,comma]"""
import sys
from pathlib import Path
import numpy as np, torch
from PIL import Image
from transformers import AutoImageProcessor, AutoModelForDepthEstimation

d = Path(sys.argv[1]); only = set(sys.argv[2].split(',')) if len(sys.argv) > 2 else None
M = r'C:\M1lash\models\Depth-Anything-V2-Small-hf'
proc = AutoImageProcessor.from_pretrained(M); model = AutoModelForDepthEstimation.from_pretrained(M).to('cuda').eval()
for f in sorted(d.glob('*.png')):
    if f.stem.endswith('_depth') or (only and f.stem not in only): continue
    im = Image.open(f).convert('RGB')
    with torch.no_grad():
        out = model(**proc(images=im, return_tensors='pt').to('cuda')).predicted_depth
    dep = torch.nn.functional.interpolate(out.unsqueeze(1), size=im.size[::-1], mode='bicubic', align_corners=False)[0, 0].cpu().numpy()
    dep = (dep - dep.min()) / (dep.max() - dep.min() + 1e-6)
    Image.fromarray((dep * 65535).astype(np.uint16)).save(d / f'{f.stem}_depth.png'); print('DEPTH', f.stem, flush=True)
