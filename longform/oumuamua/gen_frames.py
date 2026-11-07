#!/usr/bin/env python3
"""Painted keyframes for «8 уровней ИИ» on the PC GPU — SDXL base 1.0 (CreativeML Open RAIL++-M, commercial use allowed) + fp16 VAE fix.
usage: py -3.11 gen_frames.py <shots.json> <out_dir> [--steps 32]
shots.json: [{"id": "l1_s01", "prompt": "...", "seed": 1}, ...]  → <out_dir>/<id>.png (1344×768)
"""
import json, sys, argparse
from pathlib import Path
import torch
from diffusers import StableDiffusionXLPipeline, AutoencoderKL, DPMSolverMultistepScheduler

M = Path(r'C:\M1lash\models')
STYLE = ('digital oil painting, cinematic space concept art illustration, dramatic chiaroscuro lighting, muted desaturated palette with warm amber accents, '
         'visible painterly brushstrokes, atmospheric haze, highly detailed, film still composition')
NEG = ('photo, photorealistic, 3d render, cgi, plastic, cartoon, anime, text, letters, watermark, signature, logo, blurry, lowres, deformed hands, '
       'extra fingers, bad anatomy, disfigured face, cropped, frame, border')


def main():
    ap = argparse.ArgumentParser(); ap.add_argument('shots'); ap.add_argument('out'); ap.add_argument('--steps', type=int, default=32); ap.add_argument('--only', default='')
    a = ap.parse_args(); out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    vae = AutoencoderKL.from_pretrained(M / 'sdxl-vae-fp16-fix', torch_dtype=torch.float16)
    pipe = StableDiffusionXLPipeline.from_pretrained(M / 'stable-diffusion-xl-base-1.0', vae=vae, torch_dtype=torch.float16, variant='fp16', use_safetensors=True).to('cuda')
    pipe.scheduler = DPMSolverMultistepScheduler.from_config(pipe.scheduler.config, use_karras_sigmas=True)
    pipe.set_progress_bar_config(disable=True)
    for s in json.loads(Path(a.shots).read_text(encoding='utf-8')):
        if a.only and s['id'] not in a.only.split(','): continue
        g = torch.Generator('cuda').manual_seed(int(s.get('seed', 1)))
        img = pipe(prompt=s['prompt'] + ', ' + STYLE, negative_prompt=NEG + ', ' + s.get('neg', ''), width=s.get('w', 1344), height=s.get('h', 768),
                   num_inference_steps=a.steps, guidance_scale=s.get('cfg', 6.0), generator=g).images[0]
        img.save(out / f"{s['id']}.png"); print('FRAME', s['id'], flush=True)


if __name__ == '__main__':
    main()
