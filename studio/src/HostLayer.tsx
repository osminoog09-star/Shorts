// Слой «ведущий + титры» на прозрачном фоне — накладывается поверх 3D-фона (longform/antikythera, short host_demo).
import React from 'react';
import {AbsoluteFill, useCurrentFrame, interpolate, spring, useVideoConfig} from 'remotion';
import {Narrator2, NPose} from './Narrator2';
import D from './host_demo.json';

const FONT = "'Inter Display', 'Inter', 'DejaVu Sans', sans-serif";
const W = 1080, H = 1920;

// ключевые слова-акценты: [секунда, текст, цвет]
const KW: [number, string, string][] = [
  [1.0, '2000 ЛЕТ', '#ffd36b'], [3.6, '0 ЧИПОВ', '#7fe3ff'],
  [7.2, '30 ШЕСТЕРЁНОК', '#ffd36b'], [11.6, 'ЗАТМЕНИЯ', '#ff8fd0'],
  [15.3, 'БЕЗ ЭЛЕКТРИЧЕСТВА', '#7fe3ff'],
];
const CARD: [number, string, string][] = [
  [0, 'ИСТОРИЯ', 'Антикитерский механизм — компьютер 2000 лет'],
  [6.1, 'КАК РАБОТАЛ', 'Ручка → шестерни → Солнце, Луна, затмения'],
  [15.0, 'ФАКТ', 'Найден в 1901 году на дне моря у Антикитеры'],
];

const Pop: React.FC<{at: number; out?: number; children: React.ReactNode; style?: React.CSSProperties}> = ({at, out, children, style}) => {
  const f = useCurrentFrame(); const {fps} = useVideoConfig();
  const s = spring({frame: f - at * fps, fps, config: {damping: 14, stiffness: 170}});
  const o = out != null ? interpolate(f, [out * fps, out * fps + 8], [1, 0], {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'}) : 1;
  if (f < at * fps) return null;
  return <div style={{position: 'absolute', opacity: Math.min(1, s * 1.4) * o, transform: `translateY(${(1 - s) * 40}px) scale(${0.85 + 0.15 * s})`, ...style}}>{children}</div>;
};

export const HostLayer: React.FC = () => {
  const f = useCurrentFrame(); const t = f / D.fps;
  const L = D.lines as any[];
  const cur = L.find((l) => t >= l.start - 0.15 && t < l.end + 0.3) || L.reduce((p, l) => (t >= l.start ? l : p), L[0]);
  const idx = L.indexOf(cur); const prev = idx > 0 ? L[idx - 1].pose : 'rest';
  const k = Math.min(1, (t - cur.start + 0.15) / 0.35);
  const mouth = (D.mouth as number[])[f] || 0;
  const pose: NPose = t > cur.end + 0.3 ? 'rest' : cur.pose;
  const heroIn = spring({frame: f, fps: D.fps, config: {damping: 16}});
  const kwNow = KW.filter(([s]) => t >= s && t < s + 2.4);
  return (
    <AbsoluteFill>
      {/* мягкое затемнение снизу, чтобы ведущий отделялся от 3D */}
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(10,12,28,0) 45%, rgba(10,12,28,0.55) 75%, rgba(10,12,28,0.85) 100%)'}} />
      {/* верхняя карточка */}
      {CARD.map(([at, tag, text], i) => (
        <Pop key={i} at={at + 0.2} out={CARD[i + 1] ? CARD[i + 1][0] : (D.lines as any[])[3].start} style={{top: 110, left: 44, right: 44}}>
          <div style={{background: 'rgba(250,248,244,0.96)', borderRadius: 26, padding: '22px 30px', borderLeft: '10px solid #4f7dff', boxShadow: '0 20px 50px rgba(0,0,0,0.35)'}}>
            <span style={{fontFamily: FONT, fontWeight: 800, fontSize: 26, color: '#fff', background: '#4f7dff', borderRadius: 10, padding: '4px 12px'}}>{tag}</span>
            <div style={{fontFamily: FONT, fontWeight: 800, fontSize: 46, color: '#1b1d2e', lineHeight: 1.15, marginTop: 10}}>{text}</div>
          </div>
        </Pop>
      ))}
      {/* слова-акценты */}
      {kwNow.map(([s, w, c]) => (
        <Pop key={w} at={s} out={s + 2.2} style={{top: 760, left: 0, right: 0, textAlign: 'center'}}>
          <span style={{fontFamily: FONT, fontWeight: 900, fontSize: 92, color: c, letterSpacing: -2, textShadow: '0 8px 30px rgba(0,0,0,0.6)'}}>{w}</span>
        </Pop>
      ))}
      {/* ведущий */}
      <svg viewBox={`0 0 ${W} ${H}`} width={W} height={H} style={{position: 'absolute', inset: 0, opacity: heroIn}}>
        <g transform={`translate(0,${(1 - heroIn) * 200})`}>
          <Narrator2 t={f} x={540} y={1995} pose={pose} prev={prev as NPose} k={k} mouth={mouth} />
        </g>
      </svg>
      {/* реплика ведущего */}
      {t < cur.end + 0.4 && (
        <Pop key={cur.id} at={cur.start - 0.05} style={{top: 905, left: 40, right: 40, display: 'flex', justifyContent: 'center'}}>
          <div style={{background: 'rgba(8,8,14,0.74)', borderRadius: 26, padding: '14px 24px', maxWidth: 980}}>
            <span style={{fontFamily: FONT, fontWeight: 700, fontSize: 26, color: '#7fe3ff', marginRight: 12, letterSpacing: 1}}>ВЕДУЩИЙ</span>
            <span style={{fontFamily: FONT, fontWeight: 600, fontSize: 38, color: '#fff', lineHeight: 1.22}}>{cur.text}</span>
          </div>
        </Pop>
      )}
      {/* финал: подписка + спасибо */}
      <Pop at={L[3].start + 0.3} style={{top: 560, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 18}}>
        <div style={{background: '#ff2d3d', color: '#fff', fontFamily: FONT, fontWeight: 900, fontSize: 64, borderRadius: 999, padding: '18px 54px', boxShadow: '0 16px 40px rgba(255,45,61,0.45)'}}>ПОДПИСАТЬСЯ</div>
        <div style={{color: '#fff', fontFamily: FONT, fontWeight: 800, fontSize: 44, textShadow: '0 6px 24px rgba(0,0,0,0.7)'}}>Спасибо за просмотр и лайк ❤</div>
      </Pop>
      {/* нижняя плашка */}
      <div style={{position: 'absolute', left: -20, right: -20, top: 1700, height: 240, background: 'linear-gradient(180deg,#1b2a55,#0b1230)', borderTop: '6px solid #2f7bff', display: 'flex', justifyContent: 'center', paddingTop: 34}}>
        <div style={{fontFamily: FONT, fontWeight: 900, fontSize: 52, color: '#fff', letterSpacing: 3}}>M1<span style={{color: '#ff3b3b'}}>●</span>ИНЖЕНЕРИЯ ДРЕВНОСТИ</div>
      </div>
    </AbsoluteFill>
  );
};
