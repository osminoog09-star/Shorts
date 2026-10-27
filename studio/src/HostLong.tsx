// Ведущий-рассказчик для длинных видео 16:9: карточка за столом справа внизу (утверждённый 2D-ведущий).
// Данные: src/host_long.json = {fps, duration, visemes: "XXBC…" (буква на кадр по всему фильму), windows: [{a, b, poses: [[t, pose], …]}]}
// Рендерятся только кадры окон (--frames), прозрачный фон; накладывается ffmpeg поверх готового фильма.
import React from 'react';
import {AbsoluteFill, useCurrentFrame, spring} from 'remotion';
import {NPose} from './Narrator2';
import {HostCard} from './EditOutro';
import D from './host_long.json';

const VIS: Record<string, number> = {A: 0, B: 0.3, C: 0.55, D: 0.95, E: 0.65, F: 0.35, G: 0.25, H: 0.55, X: 0};
type Win = {a: number; b: number; poses: [number, NPose][]};

export const HostLong: React.FC = () => {
  const f = useCurrentFrame(); const t = f / 30;
  const wins = (D as any).windows as Win[];
  const w = wins.find((x) => t >= x.a - 0.01 && t <= x.b + 0.01);
  if (!w) return <AbsoluteFill />;
  const lt = t - w.a;
  let i = 0; for (let j = 0; j < w.poses.length; j++) if (lt >= w.poses[j][0]) i = j;
  const pose = w.poses[i][1], prev = i > 0 ? w.poses[i - 1][1] : 'rest';
  const k = Math.min(1, (lt - w.poses[i][0]) / 0.35);
  const vis = (D as any).visemes as string;
  const v = (n: number) => VIS[vis[n] || 'X'] ?? 0;
  const mouth = Math.max(0, (v(f) * 2 + v(f - 1) + v(f + 1)) / 4);
  const fa = Math.round(w.a * 30), fb = Math.round(w.b * 30);
  const inK = spring({frame: f - fa, fps: 30, config: {damping: 14}});
  const outK = spring({frame: f - (fb - 12), fps: 30, config: {damping: 16}});
  const sc = (0.55 + 0.45 * inK) * (1 - 0.6 * outK);
  const op = Math.min(1, inK * 1.6) * (1 - outK);
  const Wc = 380, Hc = 450, S = 0.8; // карточка 304×360 (≈ 33% высоты кадра)
  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', left: 1920 - 40 - Wc * S, top: 1080 - 40 - Hc * S, width: Wc, height: Hc, transformOrigin: '0 0', transform: `scale(${S})`}}>
        <div style={{position: 'absolute', inset: 0, transformOrigin: '100% 100%', transform: `scale(${sc})`, opacity: op}}>
          <HostCard f={f} pose={pose} prev={prev} k={k} mouth={mouth} />
        </div>
      </div>
    </AbsoluteFill>
  );
};
