// Ведущий-рассказчик в углу: 2D-ведущий (Narrator2) за столом в карточке слева внизу. Прозрачный фон — накладывается на 3D.
import React from 'react';
import {AbsoluteFill, useCurrentFrame, spring} from 'remotion';
import {Narrator2, NPose} from './Narrator2';
import D from './host_corner.json';

const VIS: Record<string, number> = {A: 0, B: 0.3, C: 0.55, D: 0.95, E: 0.65, F: 0.35, G: 0.25, H: 0.55, X: 0};
// позы по времени (сек): хук — показывает, рассказ — говорит, шутка — фейспалм → смех, финал — смех
const SEG: [number, NPose][] = (D as any).seg ?? [[0, 'point'], [2.6, 'talk'], [17.2, 'facepalm'], [19.0, 'laugh'], [20.0, 'talk'], [23.6, 'laugh']];

export const HostCorner: React.FC = () => {
  const f = useCurrentFrame(); const t = f / 30;
  let i = 0; for (let j = 0; j < SEG.length; j++) if (t >= SEG[j][0]) i = j;
  const pose = SEG[i][1], prev = i > 0 ? SEG[i - 1][1] : 'rest';
  const k = Math.min(1, (t - SEG[i][0]) / 0.35);
  // рот: визема + сглаживание по соседним кадрам
  const v = (n: number) => VIS[(D.visemes as string)[n] || 'X'] ?? 0;
  const mouth = Math.max(0, (v(f) * 2 + v(f - 1) + v(f + 1)) / 4);
  const pop = spring({frame: f - 4, fps: 30, config: {damping: 14}});
  const big = !(D as any).seg && t > 17.2 && t < 20 ? 1.25 : 1;
  const bigS = spring({frame: f - (t > 17.2 ? 17.2 * 30 : 0), fps: 30, config: {damping: 16}});
  const sc = (0.6 + 0.4 * pop) * (big === 1 ? 1 : 1 + 0.25 * Math.min(1, bigS));
  const X = 40, Y = 1080, Wc = 380, Hc = 450;
  return (
    <AbsoluteFill>
      <div style={{position: 'absolute', left: X, top: Y, width: Wc, height: Hc, transformOrigin: '0% 100%', transform: `scale(${sc})`, opacity: Math.min(1, pop * 1.5)}}>
        <div style={{position: 'absolute', inset: 0, borderRadius: 26, overflow: 'hidden', background: 'radial-gradient(ellipse at 50% 30%, #2a3a7a 0%, #10142c 65%)', boxShadow: '0 20px 50px rgba(0,0,0,0.55)'}}>
          {/* огни студии */}
          {[[40, 60, '#58c8ff'], [320, 90, '#ff5fb0'], [90, 180, '#ff5fb0'], [300, 210, '#58c8ff'], [200, 40, '#8f7bd8']].map(([x, y, c], j) => (
            <div key={j} style={{position: 'absolute', left: x as number, top: y as number, width: 26, height: 26, borderRadius: 13, background: c as string, opacity: 0.35, filter: 'blur(3px)'}} />
          ))}
          {/* монитор сзади-сбоку со свечением */}
          <div style={{position: 'absolute', left: 250, top: 210, width: 120, height: 80, borderRadius: 8, background: 'linear-gradient(160deg,#1c2a55,#0d1330)', border: '3px solid #2a2f45', boxShadow: '0 0 30px rgba(88,200,255,0.35)'}}>
            <div style={{margin: 10, height: 6, width: 70, background: '#58c8ff', opacity: 0.7, borderRadius: 3}} />
            <div style={{margin: 10, height: 6, width: 50, background: '#ff5fb0', opacity: 0.7, borderRadius: 3}} />
          </div>
          {/* ведущий */}
          <svg viewBox="0 0 1080 1920" width={Wc} height={Wc * 1920 / 1080} style={{position: 'absolute', left: 0, top: -250}}>
            <g transform="translate(540,1300) scale(1.05) translate(-540,-1300)">
              <Narrator2 t={f} x={540} y={1995} pose={pose} prev={prev} k={k} mouth={mouth} />
            </g>
          </svg>
          {/* стол */}
          <div style={{position: 'absolute', left: -10, right: -10, bottom: 0, height: 92, background: 'linear-gradient(180deg,#7a4a2c 0%,#5c3520 40%,#3d2214 100%)', borderTop: '5px solid #a8714a', boxShadow: '0 -8px 20px rgba(0,0,0,0.45)'}}>
            <div style={{position: 'absolute', left: 0, right: 0, top: 22, height: 2, background: 'rgba(0,0,0,0.25)'}} />
            <div style={{position: 'absolute', left: 0, right: 0, top: 48, height: 2, background: 'rgba(0,0,0,0.2)'}} />
          </div>
          {/* микрофон на стойке */}
          <div style={{position: 'absolute', left: 58, bottom: 70, width: 8, height: 120, background: '#2b2b35', borderRadius: 4, transform: 'rotate(18deg)', transformOrigin: 'bottom'}} />
          <div style={{position: 'absolute', left: 74, bottom: 170, width: 46, height: 72, borderRadius: 23, background: 'linear-gradient(90deg,#3a3a46,#1d1d25)', border: '3px solid #555', transform: 'rotate(18deg)'}}>
            {[0, 1, 2, 3].map((j) => <div key={j} style={{margin: '10px 6px 0', height: 3, background: '#777', borderRadius: 2}} />)}
          </div>
          {/* кружка */}
          <div style={{position: 'absolute', right: 40, bottom: 56, width: 44, height: 50, borderRadius: '6px 6px 12px 12px', background: 'linear-gradient(90deg,#f3f0ea,#cfc8bd)'}}>
            <div style={{position: 'absolute', right: -16, top: 10, width: 18, height: 24, border: '6px solid #e3ddd3', borderLeft: 'none', borderRadius: '0 12px 12px 0'}} />
            <div style={{position: 'absolute', left: 10, top: 16, fontSize: 18, fontWeight: 900, color: '#ff3b3b', fontFamily: 'DejaVu Sans'}}>M1</div>
          </div>
        </div>
        <div style={{position: 'absolute', inset: 0, borderRadius: 26, border: '6px solid transparent', background: 'linear-gradient(135deg,#58c8ff,#ff5fb0) border-box', WebkitMask: 'linear-gradient(#000 0 0) padding-box, linear-gradient(#000 0 0)', WebkitMaskComposite: 'xor', maskComposite: 'exclude'}} />
      </div>
    </AbsoluteFill>
  );
};
