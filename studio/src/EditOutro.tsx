// Финал для movie-edit шортсов: ведущий за столом в карточке называет фильм/сериал, сезон и серию,
// просит лайк и подписку, благодарит. Прозрачный фон — накладывается поверх застывшего последнего кадра.
// Данные (виземы, слова с таймингом) — src/edit_outro.json; тексты — props.
import React from 'react';
import {AbsoluteFill, useCurrentFrame, spring, interpolate, staticFile} from 'remotion';
import {Narrator2, NPose} from './Narrator2';
import D from './edit_outro.json';

const FONTS = `
@font-face{font-family:'MontV';src:url('${staticFile('fonts/Montserrat[wght].ttf')}') format('truetype');font-weight:100 900;}
@font-face{font-family:'MontI';src:url('${staticFile('fonts/Montserrat-Italic[wght].ttf')}') format('truetype');font-weight:100 900;font-style:italic;}
@font-face{font-family:'Unb';src:url('${staticFile('fonts/Unbounded[wght].ttf')}') format('truetype');font-weight:200 900;}
`;

const VIS: Record<string, number> = {A: 0, B: 0.3, C: 0.55, D: 0.95, E: 0.65, F: 0.35, G: 0.25, H: 0.55, X: 0};

export type OutroProps = {
  kicker: string;      // «ЭТО БЫЛ СЕРИАЛ»
  title: string;       // «ВО ВСЕ ТЯЖКИЕ»
  chips: string[];     // ['5 СЕЗОН', '7 СЕРИЯ']
  accent: string;      // цвет названия
  titleSize?: number;  // кегль названия (длинным названиям — меньше)
  t: {kicker: number; title: number; chips: number[]; like: number; sub: number; thanks: number};
  poses: [number, NPose][];
};

export const defaultOutro: OutroProps = {
  kicker: 'ЭТО БЫЛ СЕРИАЛ',
  title: 'ВО ВСЕ ТЯЖКИЕ',
  chips: ['5 СЕЗОН', '7 СЕРИЯ'],
  accent: '#5dff7a',
  t: {kicker: 0.35, title: 1.43, chips: [3.49, 4.44], like: 6.84, sub: 7.4, thanks: 9.18},
  poses: [[0, 'point'], [2.3, 'talk'], [6.2, 'point'], [8.9, 'laugh']],
};

const pop = (f: number, at: number, damping = 12) => spring({frame: f - at * 30, fps: 30, config: {damping, stiffness: 170}});

export const HostCard: React.FC<{f: number; pose: NPose; prev: NPose; k: number; mouth: number}> = ({f, pose, prev, k, mouth}) => {
  const Wc = 380, Hc = 450;
  return (
    <div style={{position: 'absolute', inset: 0}}>
      <div style={{position: 'absolute', inset: 0, borderRadius: 26, overflow: 'hidden', background: 'radial-gradient(ellipse at 50% 30%, #2a3a7a 0%, #10142c 65%)', boxShadow: '0 20px 50px rgba(0,0,0,0.55)'}}>
        {[[40, 60, '#58c8ff'], [320, 90, '#ff5fb0'], [90, 180, '#ff5fb0'], [300, 210, '#58c8ff'], [200, 40, '#8f7bd8']].map(([x, y, c], j) => (
          <div key={j} style={{position: 'absolute', left: x as number, top: y as number, width: 26, height: 26, borderRadius: 13, background: c as string, opacity: 0.35, filter: 'blur(3px)'}} />
        ))}
        <div style={{position: 'absolute', left: 250, top: 210, width: 120, height: 80, borderRadius: 8, background: 'linear-gradient(160deg,#1c2a55,#0d1330)', border: '3px solid #2a2f45', boxShadow: '0 0 30px rgba(88,200,255,0.35)'}}>
          <div style={{margin: 10, height: 6, width: 70, background: '#58c8ff', opacity: 0.7, borderRadius: 3}} />
          <div style={{margin: 10, height: 6, width: 50, background: '#ff5fb0', opacity: 0.7, borderRadius: 3}} />
        </div>
        <svg viewBox="0 0 1080 1920" width={Wc} height={Wc * 1920 / 1080} style={{position: 'absolute', left: 0, top: -250}}>
          <g transform="translate(540,1300) scale(1.05) translate(-540,-1300)">
            <Narrator2 t={f} x={540} y={1995} pose={pose} prev={prev} k={k} mouth={mouth} />
          </g>
        </svg>
        <div style={{position: 'absolute', left: -10, right: -10, bottom: 0, height: 92, background: 'linear-gradient(180deg,#7a4a2c 0%,#5c3520 40%,#3d2214 100%)', borderTop: '5px solid #a8714a', boxShadow: '0 -8px 20px rgba(0,0,0,0.45)'}}>
          <div style={{position: 'absolute', left: 0, right: 0, top: 22, height: 2, background: 'rgba(0,0,0,0.25)'}} />
          <div style={{position: 'absolute', left: 0, right: 0, top: 48, height: 2, background: 'rgba(0,0,0,0.2)'}} />
        </div>
        <div style={{position: 'absolute', left: 58, bottom: 70, width: 8, height: 120, background: '#2b2b35', borderRadius: 4, transform: 'rotate(18deg)', transformOrigin: 'bottom'}} />
        <div style={{position: 'absolute', left: 74, bottom: 170, width: 46, height: 72, borderRadius: 23, background: 'linear-gradient(90deg,#3a3a46,#1d1d25)', border: '3px solid #555', transform: 'rotate(18deg)'}}>
          {[0, 1, 2, 3].map((j) => <div key={j} style={{margin: '10px 6px 0', height: 3, background: '#777', borderRadius: 2}} />)}
        </div>
        <div style={{position: 'absolute', right: 40, bottom: 56, width: 44, height: 50, borderRadius: '6px 6px 12px 12px', background: 'linear-gradient(90deg,#f3f0ea,#cfc8bd)'}}>
          <div style={{position: 'absolute', right: -16, top: 10, width: 18, height: 24, border: '6px solid #e3ddd3', borderLeft: 'none', borderRadius: '0 12px 12px 0'}} />
          <div style={{position: 'absolute', left: 10, top: 16, fontSize: 18, fontWeight: 900, color: '#ff3b3b', fontFamily: 'DejaVu Sans'}}>M1</div>
        </div>
      </div>
      <div style={{position: 'absolute', inset: 0, borderRadius: 26, border: '6px solid transparent', background: 'linear-gradient(135deg,#58c8ff,#ff5fb0) border-box', WebkitMask: 'linear-gradient(#000 0 0) padding-box, linear-gradient(#000 0 0)', WebkitMaskComposite: 'xor', maskComposite: 'exclude'}} />
    </div>
  );
};

const Thumb: React.FC<{size: number; fill: string}> = ({size, fill}) => (
  <svg viewBox="0 0 24 24" width={size} height={size}>
    <path fill={fill} d="M2 21h3.5V9.5H2V21zM22 10.6c0-1.1-.9-2-2-2h-5.6l.9-4.2v-.3c0-.4-.2-.8-.4-1.1L13.8 2 7.4 8.5c-.4.3-.6.8-.6 1.3V19c0 1.1.9 2 2 2h8.5c.8 0 1.5-.5 1.8-1.2l2.7-6.4c.1-.2.2-.5.2-.8v-2z" />
  </svg>
);

const Bell: React.FC<{size: number; ring: number}> = ({size, ring}) => (
  <svg viewBox="0 0 24 24" width={size} height={size} style={{transform: `rotate(${Math.sin(ring * 22) * 18 * Math.max(0, 1 - ring)}deg)`}}>
    <path fill="#fff" d="M12 22c1.1 0 2-.9 2-2h-4c0 1.1.9 2 2 2zm6-6v-5c0-3.1-1.6-5.6-4.5-6.3V4c0-.8-.7-1.5-1.5-1.5S10.5 3.2 10.5 4v.7C7.6 5.4 6 7.9 6 11v5l-2 2v1h16v-1l-2-2z" />
  </svg>
);

export const EditOutro: React.FC<OutroProps> = (p) => {
  const f = useCurrentFrame();
  const t = f / 30;
  // поза ведущего
  let i = 0;
  for (let j = 0; j < p.poses.length; j++) if (t >= p.poses[j][0]) i = j;
  const pose = p.poses[i][1], prev = i > 0 ? p.poses[i - 1][1] : 'rest';
  const k = Math.min(1, (t - p.poses[i][0]) / 0.35);
  const v = (n: number) => VIS[((D as any).visemes as string)[n] || 'X'] ?? 0;
  const mouth = Math.max(0, (v(f) * 2 + v(f - 1) + v(f + 1)) / 4);

  const card = pop(f, 0.05, 14);
  const sKick = pop(f, p.t.kicker), sTitle = pop(f, p.t.title, 10);
  const chipS = p.t.chips.map((c) => pop(f, c, 11));
  const like = pop(f, p.t.like, 9), sub = pop(f, p.t.sub, 10);
  const tap = p.t.sub + 0.75;                       // «нажатие» на кнопку
  const pressed = t >= tap;
  const press = interpolate(t, [tap - 0.08, tap, tap + 0.12], [1, 0.9, 1], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});
  const ring = Math.max(0, t - tap) / 1.2;
  const thanks = pop(f, p.t.thanks, 12);
  const likeBurst = Math.max(0, Math.min(1, (t - p.t.like) / 0.5));
  const glow = (c: string, r = 30) => `0 0 ${r}px ${c}, 0 0 ${r * 2}px ${c}88, 0 6px 14px rgba(0,0,0,0.6)`;
  const finger = interpolate(t, [p.t.sub + 0.2, tap, tap + 0.5], [0, 1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'});

  return (
    <AbsoluteFill style={{fontFamily: 'MontV'}}>
      <style>{FONTS}</style>
      {/* название */}
      <div style={{position: 'absolute', top: 250, width: '100%', textAlign: 'center', opacity: sKick, transform: `translateY(${(1 - sKick) * 30}px)`,
        color: '#fff', fontWeight: 800, fontSize: 50, letterSpacing: 14, textShadow: glow('rgba(255,255,255,0.5)', 12)}}>{p.kicker}</div>
      <div style={{position: 'absolute', top: 320, width: '100%', textAlign: 'center', fontFamily: 'Unb', fontWeight: 900, fontSize: p.titleSize ?? 112, lineHeight: 1.02, letterSpacing: 4,
        color: '#eaffe8', opacity: Math.min(1, sTitle * 1.4), transform: `scale(${1.6 - 0.6 * sTitle})`, textShadow: glow(p.accent, 28)}}>{p.title}</div>
      <div style={{position: 'absolute', top: 590, width: '100%', display: 'flex', justifyContent: 'center', gap: 28}}>
        {p.chips.map((c, j) => (
          <div key={j} style={{opacity: chipS[j], transform: `translateY(${(1 - chipS[j]) * 40}px) scale(${0.6 + 0.4 * chipS[j]})`, padding: '18px 38px', borderRadius: 60,
            background: 'linear-gradient(180deg,rgba(255,255,255,0.22),rgba(255,255,255,0.06))', border: `4px solid ${p.accent}`, boxShadow: `0 0 26px ${p.accent}99, inset 0 0 20px ${p.accent}44`,
            color: '#fff', fontWeight: 900, fontSize: 58, letterSpacing: 3, backdropFilter: 'blur(6px)'}}>{c}</div>
        ))}
      </div>
      {/* лайк и подписка */}
      <div style={{position: 'absolute', top: 770, width: '100%', display: 'flex', justifyContent: 'center', alignItems: 'center', gap: 34}}>
        <div style={{position: 'relative', width: 150, height: 150, opacity: like, transform: `scale(${like})`}}>
          {[...Array(10)].map((_, j) => {
            const a = (j / 10) * Math.PI * 2, r = 70 + likeBurst * 70;
            return <div key={j} style={{position: 'absolute', left: 75 + Math.cos(a) * r - 7, top: 75 + Math.sin(a) * r - 7, width: 14, height: 14, borderRadius: 7,
              background: j % 2 ? '#ff5fb0' : '#58c8ff', opacity: likeBurst > 0 && likeBurst < 1 ? 1 - likeBurst : 0}} />;
          })}
          <div style={{position: 'absolute', inset: 0, borderRadius: 75, background: 'linear-gradient(160deg,#4aa8ff,#1d5bff)', boxShadow: '0 0 40px #3b8bff, 0 10px 24px rgba(0,0,0,0.5)', display: 'flex', alignItems: 'center', justifyContent: 'center'}}>
            <Thumb size={84} fill="#fff" />
          </div>
        </div>
        <div style={{position: 'relative', opacity: sub, transform: `scale(${(0.5 + 0.5 * sub) * press})`}}>
          <div style={{display: 'flex', alignItems: 'center', gap: 18, padding: '30px 46px', borderRadius: 80,
            background: pressed ? 'linear-gradient(180deg,#3a3a44,#24242c)' : 'linear-gradient(180deg,#ff3b3b,#d10f1f)',
            boxShadow: pressed ? '0 10px 24px rgba(0,0,0,0.5)' : '0 0 40px #ff2a3a, 0 10px 24px rgba(0,0,0,0.5)',
            color: '#fff', fontWeight: 900, fontSize: 52, letterSpacing: 2}}>
            {pressed ? <><Bell size={56} ring={ring} /> ВЫ ПОДПИСАНЫ</> : 'ПОДПИСАТЬСЯ'}
          </div>
          {/* палец-нажатие */}
          <div style={{position: 'absolute', right: 40, top: 70 + (1 - finger) * 120, fontSize: 96, opacity: finger > 0 ? 1 : 0, filter: 'drop-shadow(0 6px 10px rgba(0,0,0,0.6))'}}>👆</div>
        </div>
      </div>
      <div style={{position: 'absolute', top: 960, left: 560, right: 40, textAlign: 'center', opacity: thanks, transform: `translateY(${(1 - thanks) * 30}px) rotate(-3deg)`,
        fontFamily: 'MontI', fontStyle: 'italic', fontWeight: 900, fontSize: 64, lineHeight: 1.05, color: '#ffe36b', textShadow: glow('#ffb020', 22)}}>
        СПАСИБО,<br />ЧТО ДОСМОТРЕЛ ❤️
      </div>
      {/* ведущий за столом */}
      <div style={{position: 'absolute', left: 40, top: 1080, width: 380, height: 450, transformOrigin: '0% 100%', transform: `scale(${(0.6 + 0.4 * card) * 1.3})`, opacity: Math.min(1, card * 1.5)}}>
        <HostCard f={f} pose={pose} prev={prev} k={k} mouth={mouth} />
      </div>
    </AbsoluteFill>
  );
};
