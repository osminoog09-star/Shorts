import React from 'react';
import {AbsoluteFill, Html5Audio, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {Narrator2 as Narrator, NPose} from './Narrator2';
import {Img} from 'remotion';
import {Alarm3D, AppIcon, Folder3D, Robot3D, Trash3D} from './Icons3D';
import {Lang} from './text';
import TL from './story_timeline.json';

const FONT = "'Inter Display', 'Inter', 'DejaVu Sans', sans-serif";
const MONO = "'DejaVu Sans Mono', monospace";
const W = 1080;
const H = 1920;
const cl = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const GPTC = '#3fd6b2';
const CDXC = '#5b7cff';

const ST = {
  ru: {
    k1: 'полгода с ии-агентами', k2: 'пара историй', story: 'история', gptSub: 'языковая модель', cdxSub: 'агент для кода',
    me1: '2 + 2 = 5?', bot: 'вы абсолютно правы!', me2: 'нет, 4', ka5: 'согласен со всем',
    task: 'почини тесты', working: 'работаю…', passed: 'все тесты пройдены', kb3: 'он их просто удалил',
    kc1: '«немного»\nоптимизировал', done: 'оптимизация завершена', fps: 'кадров в секунду',
    kd1: 'когда всё ломается', fail: 'сборка упала', d2: 'это код codex!', d3: 'это промпт gpt!', kd4: 'виноватых нет',
    ke1: 'решил писать сам', ke2: 'gpt… а как?', e3: 'отличный вопрос!', end: 'подпишись, если узнал себя',
  },
  en: {
    k1: '6 months with ai agents', k2: 'a couple of stories', story: 'story', gptSub: 'language model', cdxSub: 'coding agent',
    me1: '2 + 2 = 5?', bot: 'you’re absolutely right!', me2: 'no, it’s 4', ka5: 'agrees with everything',
    task: 'fix the tests', working: 'working…', passed: 'all tests passed', kb3: 'he just deleted them',
    kc1: 'optimized\n“a little”', done: 'optimization complete', fps: 'frames per second',
    kd1: 'when everything breaks', fail: 'build failed', d2: 'that’s codex’s code!', d3: 'that’s gpt’s prompt!', kd4: 'nobody’s to blame',
    ke1: 'i’ll code it myself', ke2: 'gpt… how?', e3: 'great question!', end: 'follow if this is you',
  },
};

type D = {lines: Record<string, {start: number; end: number; who: string; file: string}>; segs: Record<string, {start: number; end: number}>; total: number; mouth: number[]};

export const story2Duration = (lang: Lang) => (TL as any)[lang].total as number;

// ───────── анимация появления с размытием ─────────
const Appear: React.FC<{at: number; out?: number; style?: React.CSSProperties; children: React.ReactNode; dy?: number}> = ({at, out = 1e9, style, children, dy = 50}) => {
  const f = useCurrentFrame();
  if (f < at || f > out + 9) return null;
  const pin = interpolate(f, [at, at + 9], [0, 1], cl);
  const pout = interpolate(f, [out, out + 9], [0, 1], cl);
  const e = 1 - Math.pow(1 - pin, 3);
  return (
    <div
      style={{
        position: 'absolute', opacity: e * (1 - pout), filter: `blur(${(1 - e) * 22 + pout * 22}px)`,
        transform: `perspective(1400px) rotateX(${(1 - e) * 28 - pout * 12}deg) translateY(${(1 - e) * dy - pout * 40}px) scale(${0.9 + 0.1 * e + pout * 0.05})`, transformOrigin: '50% 100%', ...style,
      }}
    >
      {children}
    </div>
  );
};

const Key: React.FC<{text: string; at: number; out?: number; color?: string; top?: number; size?: number}> = ({text, at, out = 1e9, color = '#fff', top = 210, size = 82}) => {
  const f = useCurrentFrame();
  if (f < at || f > out + 10) return null;
  const pout = interpolate(f, [out, out + 9], [0, 1], cl);
  const lines = text.split('\n');
  let wi = 0;
  const accent = color === '#fff' ? 'linear-gradient(90deg,#7fe3ff,#c89bff)' : 'linear-gradient(90deg,#2f7bff,#9b4dff)';
  const total = text.split(/\s+/).length;
  return (
    <div style={{position: 'absolute', top, left: 30, right: 30, textAlign: 'center', opacity: 1 - pout, filter: `blur(${pout * 20}px)`, transform: `translateY(${-pout * 40}px)`}}>
      {lines.map((ln2, li) => (
        <div key={li} style={{fontFamily: FONT, fontWeight: 700, fontSize: size, letterSpacing: -1.5, lineHeight: 1.08}}>
          {ln2.split(' ').map((w, i) => {
            const idx = wi++;
            const st = at + idx * 3;
            const p = interpolate(f, [st, st + 9], [0, 1], cl);
            const ov = p < 1 ? 1 + Math.sin(p * Math.PI) * 0.12 : 1;
            const isAcc = idx === total - 1 && total > 1;
            return (
              <span
                key={i}
                style={{
                  display: 'inline-block', marginRight: '0.26em', opacity: p, filter: `blur(${(1 - p) * 16}px)`,
                  transform: `translateY(${(1 - p) * 40}px) scale(${ov})`, color: isAcc ? 'transparent' : color,
                  backgroundImage: isAcc ? accent : undefined, WebkitBackgroundClip: isAcc ? 'text' : undefined, backgroundClip: isAcc ? 'text' : undefined,
                  textShadow: color === '#fff' && !isAcc ? '0 6px 30px rgba(0,0,0,0.5)' : undefined,
                }}
              >
                {w}
              </span>
            );
          })}
        </div>
      ))}
    </div>
  );
};

const Bokeh: React.FC<{f: number; tint: number}> = ({f, tint}) => (
  <AbsoluteFill style={{overflow: 'hidden'}}>
    {Array.from({length: 16}).map((_, i) => {
      const x = ((i * 337) % 1180) - 50 + Math.sin(f * 0.01 + i) * 30;
      const y = ((i * 613) % 1300) + 80 - ((f * (0.25 + (i % 4) * 0.12)) % 220);
      const r = 40 + ((i * 53) % 110);
      const c = i % 3 === 0 ? `rgba(79,209,255,${0.10 * tint})` : i % 3 === 1 ? `rgba(200,120,255,${0.09 * tint})` : `rgba(255,190,120,${0.07 * tint})`;
      return <div key={i} style={{position: 'absolute', left: x, top: y, width: r * 2, height: r * 2, borderRadius: '50%', background: `radial-gradient(circle, ${c} 0%, ${c} 45%, transparent 70%)`}} />;
    })}
    {[0, 1, 2].map((i) => (
      <div
        key={`r${i}`}
        style={{
          position: 'absolute', left: 200 + i * 260, top: -300, width: 120 + i * 40, height: 1700, opacity: (0.05 + 0.03 * Math.sin(f * 0.03 + i)) * tint,
          background: 'linear-gradient(180deg, rgba(180,220,255,0.9), transparent 80%)', transform: `rotate(${18 - i * 6}deg)`, transformOrigin: 'top center',
        }}
      />
    ))}
  </AbsoluteFill>
);

const Label: React.FC<{text: string; at: number; out: number; dark?: boolean}> = ({text, at, out, dark = true}) => (
  <Appear at={at} out={out} style={{top: 120, left: 0, right: 0, display: 'flex', justifyContent: 'center'}} dy={20}>
    <div style={{fontFamily: FONT, fontWeight: 600, fontSize: 30, padding: '10px 26px', borderRadius: 40, color: dark ? '#9a9aa6' : '#6b6b76', background: dark ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.05)', letterSpacing: 1}}>
      {text}
    </div>
  </Appear>
);

const Card: React.FC<{children: React.ReactNode; light?: boolean; style?: React.CSSProperties}> = ({children, light, style}) => (
  <div
    style={{
      background: light ? '#ffffff' : '#18181c', borderRadius: 42, padding: '30px 34px', fontFamily: FONT,
      boxShadow: light ? '0 20px 60px rgba(0,0,0,0.10), 0 2px 0 rgba(0,0,0,0.03)' : '0 20px 60px rgba(0,0,0,0.5), inset 0 1px 0 rgba(255,255,255,0.06)',
      border: light ? '1px solid #ececf1' : '1px solid #26262c', ...style,
    }}
  >
    {children}
  </div>
);

const MiniBot: React.FC<{c: string}> = ({c}) => (
  <svg width={52} height={52} viewBox="-30 -30 60 60">
    <rect x={-24} y={-20} width={48} height={36} rx={16} fill="#fff" />
    <rect x={-17} y={-13} width={34} height={22} rx={10} fill="#0b1020" />
    <rect x={-11} y={-9} width={6} height={10} rx={3} fill={c} />
    <rect x={5} y={-9} width={6} height={10} rx={3} fill={c} />
  </svg>
);

const Header: React.FC<{name: string; sub: string; c: string; light?: boolean}> = ({name, sub, c, light}) => (
  <div style={{display: 'flex', alignItems: 'center', gap: 22, marginBottom: 26}}>
    <AppIcon from={c} to={c === GPTC ? '#139a7e' : '#3a3fd0'}>
      <MiniBot c={c} />
    </AppIcon>
    <div>
      <div style={{fontSize: 46, fontWeight: 700, color: light ? '#111' : '#fff'}}>{name}</div>
      <div style={{fontSize: 30, fontWeight: 500, color: light ? '#8a8a96' : '#7c7c88'}}>{sub}</div>
    </div>
  </div>
);

const Bub: React.FC<{me?: boolean; text: string; at: number}> = ({me, text, at}) => {
  const f = useCurrentFrame();
  if (f < at) return null;
  const p = interpolate(f, [at, at + 7], [0, 1], cl);
  return (
    <div style={{display: 'flex', justifyContent: me ? 'flex-end' : 'flex-start', marginTop: 18, opacity: p, transform: `translateY(${(1 - p) * 30}px) scale(${0.9 + 0.1 * p})`, filter: `blur(${(1 - p) * 10}px)`}}>
      <div style={{background: me ? '#2f7bff' : '#2a2a30', color: '#fff', fontSize: 44, fontWeight: 600, padding: '20px 30px', borderRadius: 34, borderBottomRightRadius: me ? 8 : 34, borderBottomLeftRadius: me ? 34 : 8, boxShadow: me ? '0 8px 30px rgba(47,123,255,.4)' : 'none'}}>
        {text}
      </div>
    </div>
  );
};

// ───────── главный компонент ─────────
export const Story2: React.FC<{lang: Lang}> = ({lang}) => {
  const f = useCurrentFrame();
  const d = (TL as any)[lang] as D;
  const L = ST[lang];
  const ln = (id: string) => d.lines[id];
  const sg = (n: string) => d.segs[n];
  const segA = (n: string) => {
    const s = sg(n);
    return Math.max(0, Math.min(1, (f - s.start + 4) / 8, (s.end + 4 - f) / 8));
  };
  const inSeg = (n: string) => f >= sg(n).start - 6 && f < sg(n).end + 8;
  const sOut = (n: string) => sg(n).end - 6;

  // позы рассказчика
  const ev: [number, NPose][] = [
    [0, 'type'],
    [ln('i1').start - 8, 'talk'],
    [ln('i2').start, 'point'],
    [ln('a1').start, 'talk'],
    [ln('a2').start, 'deadpan'],
    [ln('a3').start, 'talk'],
    [ln('a4').start, 'deadpan'],
    [ln('a5').start, 'facepalm'],
    [ln('b1').start, 'talk'],
    [ln('b2').start, 'deadpan'],
    [ln('b3').start, 'shock'],
    [ln('c1').start, 'talk'],
    [ln('c2').start, 'deadpan'],
    [ln('d1').start, 'talk'],
    [ln('d2').start, 'deadpan'],
    [ln('d4').start, 'shrug'],
    [ln('e1').start, 'point'],
    [ln('e2').start, 'shrug'],
    [ln('e3').start, 'facepalm'],
    [ln('e3').end + 8, 'laugh'],
  ];
  let ci = 0;
  for (let i = 0; i < ev.length; i++) if (f >= ev[i][0]) ci = i;
  const pose = ev[ci][1];
  const prev = ci > 0 ? ev[ci - 1][1] : pose;
  const pk = Math.min(1, (f - ev[ci][0]) / 7);
  const mouth = d.mouth[Math.min(f, d.mouth.length - 1)] || 0;

  // интро: за компом
  const i1 = ln('i1').start;
  const monY = interpolate(f, [i1 - 12, i1 + 4], [0, 520], cl);
  const nScale = interpolate(f, [i1 - 12, i1 + 4], [0.86, 1], cl);
  const look = f < 34 ? 'down' : 'cam';

  // размытие на стыках сцен
  const bounds = ['s1', 's2', 's3', 's4', 'out'].map((n) => sg(n).start).concat([i1 - 4]);
  const bd = Math.min(...bounds.map((b) => Math.abs(f - b)));
  const tBlur = Math.max(0, 14 - bd * 3.5);

  // ручная камера
  const hx = Math.sin(f * 0.031) * 4 + Math.sin(f * 0.077) * 2;
  const hy = Math.cos(f * 0.027) * 3 + Math.sin(f * 0.091) * 1.5;
  const hr = Math.sin(f * 0.019) * 0.25;
  // наезды на панчлайнах
  const punches: [number, number][] = [
    [ln('a5').start, ln('a5').end + 8],
    [ln('b3').start, ln('b3').end + 10],
    [ln('c2').end - 20, ln('c2').end + 14],
    [ln('d4').start, ln('d4').end + 6],
    [ln('e2').start, ln('e2').end + 2],
    [ln('e3').end + 8, d.total],
  ];
  let zoom = 1;
  for (const [a, b] of punches) {
    const zin = interpolate(f, [a, a + 7], [0, 1], {...cl, easing: (x) => 1 - Math.pow(1 - x, 3)});
    const zout = interpolate(f, [b, b + 10], [0, 1], cl);
    zoom = Math.max(zoom, 1 + 0.2 * zin * (1 - zout));
  }
  const push = interpolate(f, [i1, d.total], [1, 1.04], cl);
  const speaking = (id: string) => f >= ln(id).start && f < ln(id).end;
  const bob = (id: string) => (speaking(id) ? 1 + Math.abs(Math.sin(f * 0.5)) * 0.05 : 1);

  // S2: папка в корзину
  const b3 = ln('b3').start;
  const fk = interpolate(f, [b3 + 2, b3 + 24], [0, 1], cl);
  const lid = interpolate(f, [b3, b3 + 8, b3 + 26, b3 + 32], [0, 55, 55, 0], cl);

  // S3: счётчик fps
  const c2 = ln('c2');
  const fpsV = Math.round(interpolate(f, [c2.start + 10, c2.end - 6], [60, 2], {...cl, easing: (x) => x * x}));
  const s3shake = f > c2.end - 8 && f < c2.end + 10 ? Math.sin(f * 3) * 12 : 0;

  return (
    <AbsoluteFill style={{background: '#0b0b0d', overflow: 'hidden'}}>
      {/* фоны */}
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 35%, #1c1c24 0%, #0b0b0d 65%)'}} />
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 30%, #ffffff 0%, #f1f1f4 70%)', opacity: segA('s2')}} />
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 30%, #ff4a4a 0%, #c0101f 55%, #6d0610 100%)', opacity: segA('s3')}} />
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 40%, rgba(70,90,255,0.35) 0%, transparent 60%)', opacity: segA('s4')}} />
      <Bokeh f={f} tint={1 - segA('s2') * 0.85} />
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 85%, rgba(79,209,255,0.25) 0%, transparent 45%)', opacity: interpolate(f, [0, 10, i1 - 10, i1], [0, 1, 1, 0], cl)}} />

      <AbsoluteFill style={{filter: tBlur > 0.3 ? `blur(${tBlur}px)` : undefined, transform: `translate(${s3shake + hx}px,${hy}px) rotate(${hr}deg) scale(${1 + tBlur * 0.006})`}}>
        {/* ───── INTRO ───── */}
        {inSeg('intro') && (
          <>
            <Key text={L.k1} at={i1 + 2} out={ln('i2').start - 4} />
            <Key text={L.k2} at={ln('i2').start} out={sOut('intro')} />
            <Appear at={i1 + 12} out={sOut('intro')} style={{top: 470, left: 120}}>
              <div style={{transform: `translateY(${Math.sin(f * 0.08) * 10}px)`, textAlign: 'center'}}>
                <Robot3D id="ig" size={270} accent={GPTC} t={f} />
                <div style={{fontFamily: FONT, fontSize: 40, fontWeight: 600, color: '#8a8a96', marginTop: -6}}>gpt</div>
              </div>
            </Appear>
            <Appear at={i1 + 20} out={sOut('intro')} style={{top: 470, right: 120}}>
              <div style={{transform: `translateY(${Math.sin(f * 0.08 + 2) * 10}px)`, textAlign: 'center'}}>
                <Robot3D id="ic" size={270} accent={CDXC} t={f + 20} />
                <div style={{fontFamily: FONT, fontSize: 40, fontWeight: 600, color: '#8a8a96', marginTop: -6}}>codex</div>
              </div>
            </Appear>
          </>
        )}

        {/* ───── S1: абсолютно прав ───── */}
        {inSeg('s1') && (
          <>
            <Label text={`${L.story} 1`} at={sg('s1').start} out={sOut('s1')} />
            <Appear at={ln('a1').start - 4} out={ln('a5').start - 2} style={{top: 210, left: 70, right: 70}}>
              <Card>
                <Header name="gpt" sub={L.gptSub} c={GPTC} />
                <Bub me text={L.me1} at={ln('a1').start + 4} />
                <Bub text={L.bot} at={ln('a2').start} />
                <Bub me text={L.me2} at={ln('a3').start + 4} />
                <Bub text={L.bot} at={ln('a4').start} />
              </Card>
            </Appear>
            <Key text={L.ka5} at={ln('a5').start} out={sOut('s1')} />
            <Appear at={ln('a5').start + 6} out={sOut('s1')} style={{top: 380, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
              <div style={{transform: `rotate(${Math.sin(f * 0.5) * 6}deg) translateY(${Math.abs(Math.sin(f * 0.5)) * -18}px)`}}>
                <Robot3D id="s1g" size={320} accent={GPTC} mood="happy" t={f} />
              </div>
            </Appear>
          </>
        )}

        {/* ───── S2: тесты ───── */}
        {inSeg('s2') && (
          <>
            <Label text={`${L.story} 2`} at={sg('s2').start} out={sOut('s2')} dark={false} />
            <Appear at={ln('b1').start - 4} out={b3 - 2} style={{top: 230, left: 70, right: 70}}>
              <Card light>
                <Header name="codex" sub={L.cdxSub} c={CDXC} light />
                <div style={{display: 'flex', alignItems: 'center', gap: 20, padding: '18px 0', borderTop: '1px solid #efeff3', fontSize: 42, fontWeight: 600, color: '#222'}}>
                  <span style={{fontFamily: MONO, color: '#2f7bff'}}>{'>'}</span> {L.task}
                </div>
                <div style={{display: 'flex', alignItems: 'center', gap: 20, padding: '18px 0', borderTop: '1px solid #efeff3', fontSize: 40, fontWeight: 600}}>
                  {f < ln('b2').start ? (
                    <>
                      <div style={{width: 34, height: 34, borderRadius: 17, border: '5px solid #d6d6de', borderTopColor: '#5b7cff', transform: `rotate(${f * 18}deg)`}} />
                      <span style={{color: '#8a8a96'}}>{L.working}</span>
                    </>
                  ) : (
                    <>
                      <div style={{width: 44, height: 44, borderRadius: 22, background: '#22c55e', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 30}}>✓</div>
                      <span style={{color: '#16a34a'}}>{L.passed}</span>
                      <span style={{marginLeft: 'auto', fontFamily: MONO, fontSize: 52, color: '#111', fontWeight: 700}}>0 / 0</span>
                    </>
                  )}
                </div>
              </Card>
            </Appear>
            <Key text={L.kb3} at={b3} out={sOut('s2')} color="#111" />
            <Appear at={b3} out={sOut('s2')} style={{top: 520, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
              <Trash3D size={300} lid={lid} />
            </Appear>
            {f >= b3 && f < b3 + 24 && (
              <div
                style={{
                  position: 'absolute', left: interpolate(fk, [0, 1], [90, 410]), top: 480 - Math.sin(fk * Math.PI) * 180 + fk * 60,
                  transform: `rotate(${fk * 300}deg) scale(${1 - fk * 0.6})`,
                }}
              >
                <Folder3D size={260} label="tests/" />
              </div>
            )}
          </>
        )}

        {/* ───── S3: оптимизация ───── */}
        {inSeg('s3') && (
          <>
            <Label text={`${L.story} 3`} at={sg('s3').start} out={sOut('s3')} />
            <Key text={L.kc1} at={ln('c1').start} out={c2.start - 2} />
            <Appear at={ln('c1').start + 10} out={c2.start - 2} style={{top: 520, left: 110, right: 110}}>
              <Card style={{display: 'flex', alignItems: 'center', gap: 22, background: 'rgba(0,0,0,0.35)', border: '1px solid rgba(255,255,255,0.15)'}}>
                <AppIcon from={CDXC} to="#3a3fd0">
                  <MiniBot c={CDXC} />
                </AppIcon>
                <div style={{fontSize: 40, fontWeight: 600, color: '#fff'}}>{L.done} ✓</div>
              </Card>
            </Appear>
            <Appear at={c2.start} out={sOut('s3')} style={{top: 250, left: 0, right: 0, textAlign: 'center', fontFamily: FONT, color: '#fff'}}>
              <div style={{fontSize: 330, fontWeight: 800, letterSpacing: -12, lineHeight: 1, textShadow: '0 20px 60px rgba(0,0,0,0.35)'}}>{fpsV}</div>
              <div style={{fontSize: 52, fontWeight: 600, opacity: 0.85, marginTop: 10}}>{L.fps}</div>
            </Appear>
          </>
        )}

        {/* ───── S4: кто виноват ───── */}
        {inSeg('s4') && (
          <>
            <Label text={`${L.story} 4`} at={sg('s4').start} out={sOut('s4')} />
            <Key text={L.kd1} at={ln('d1').start} out={ln('d2').start - 2} />
            <Appear at={ln('d1').start + 8} out={ln('d2').start - 2} style={{top: 420, left: 0, right: 0, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 20}}>
              <Alarm3D size={230} t={f} />
              <div style={{fontFamily: MONO, fontSize: 40, fontWeight: 700, color: '#ff5a5a'}}>✕ {L.fail}</div>
            </Appear>
            <Appear at={ln('d2').start} out={sOut('s4')} style={{top: 470, left: 70}}>
              <div style={{transform: `scale(${bob('d2')})`, transformOrigin: 'center bottom'}}>
                <Robot3D id="s4g" size={250} accent={GPTC} t={f} />
              </div>
            </Appear>
            <Appear at={ln('d2').start + 2} out={sOut('s4')} style={{top: 250, left: 40}}>
              <Card style={{padding: '22px 30px', borderBottomLeftRadius: 10}}>
                <div style={{fontSize: 44, fontWeight: 700, color: '#fff'}}>{L.d2}</div>
              </Card>
            </Appear>
            <Appear at={ln('d3').start} out={sOut('s4')} style={{top: 560, right: 70}}>
              <div style={{transform: `scale(${bob('d3')})`, transformOrigin: 'center bottom'}}>
                <Robot3D id="s4c" size={250} accent={CDXC} t={f + 9} />
              </div>
            </Appear>
            <Appear at={ln('d3').start + 2} out={sOut('s4')} style={{top: 400, right: 40}}>
              <Card style={{padding: '22px 30px', borderBottomRightRadius: 10, border: '1px solid #3a3f7a'}}>
                <div style={{fontSize: 44, fontWeight: 700, color: '#fff'}}>{L.d3}</div>
              </Card>
            </Appear>
            <Key text={L.kd4} at={ln('d4').start} out={sOut('s4')} top={880} size={70} />
          </>
        )}

        {/* ───── OUTRO ───── */}
        {inSeg('out') && (
          <>
            <Key text={L.ke1} at={ln('e1').start} out={ln('e2').start - 2} />
            <Key text={L.ke2} at={ln('e2').start} out={ln('e3').start - 2} />
            <Appear at={ln('e2').start + 6} out={ln('e3').start - 2} style={{top: 400, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
              <div style={{fontFamily: FONT, fontSize: 260, fontWeight: 800, color: '#2a2a33'}}>?</div>
            </Appear>
            <Appear at={ln('e3').start} out={sg('out').end + 60} style={{top: 210, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
              <Card style={{padding: '24px 36px', display: 'flex', alignItems: 'center', gap: 18}}>
                <AppIcon from={GPTC} to="#139a7e" size={64}>
                  <MiniBot c={GPTC} />
                </AppIcon>
                <div style={{fontSize: 50, fontWeight: 700, color: '#fff'}}>{L.e3}</div>
              </Card>
            </Appear>
            <Appear at={ln('e3').start + 4} out={sg('out').end + 60} style={{top: 400, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
              <div style={{transform: `scale(${bob('e3')})`}}>
                <Robot3D id="og" size={300} accent={GPTC} mood="happy" t={f} />
              </div>
            </Appear>
            <Appear at={ln('e3').end + 10} out={sg('out').end + 60} style={{top: 790, left: 0, right: 0, textAlign: 'center'}} dy={20}>
              <div style={{fontFamily: FONT, fontSize: 40, fontWeight: 600, color: '#8a8a96'}}>{L.end}</div>
            </Appear>
          </>
        )}

        {/* ───── рассказчик ───── */}
        <svg viewBox={`0 0 ${W} ${H}`} width={W} height={H} style={{position: 'absolute', inset: 0}}>
          <g transform={`translate(540,1300) scale(${zoom * push}) translate(-540,-1300)`}>
          <Narrator t={f} x={540} y={1995} s={nScale} pose={pose} prev={prev} k={pk} mouth={mouth} look={look} />
          </g>
          {/* монитор в интро */}
          {monY < 520 && (
            <g transform={`translate(0,${monY})`}>
              <defs>
                <linearGradient id="mon" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0" stopColor="#23252e" />
                  <stop offset="1" stopColor="#0d0e12" />
                </linearGradient>
              </defs>
              <rect x={150} y={1500} width={780} height={330} rx={26} fill="url(#mon)" stroke="#4fd1ff" strokeOpacity={0.5} strokeWidth={4} />
              <rect x={150} y={1500} width={780} height={6} rx={3} fill="#4fd1ff" opacity={0.6} />
              <rect x={490} y={1830} width={100} height={60} fill="#15161c" />
              <rect x={0} y={1870} width={W} height={60} fill="#121318" />
              <circle cx={540} cy={1670} r={30} fill="#2a2c36" />
            </g>
          )}
        </svg>
      </AbsoluteFill>

      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(40,90,140,0.35), rgba(0,0,0,0) 45%, rgba(160,80,40,0.25))', mixBlendMode: 'soft-light'}} />
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, transparent 55%, rgba(0,0,0,0.55) 100%)'}} />
      <AbsoluteFill style={{opacity: 0.09, mixBlendMode: 'overlay'}}>
        <Img src={staticFile(`grain/g${f % 8}.png`)} style={{width: W, height: H, imageRendering: 'pixelated'}} />
      </AbsoluteFill>
      {(() => {
        const lk = Math.max(0, 1 - bd / 9);
        if (lk <= 0) return null;
        const pos = ((f % 97) / 97) * 140 - 20;
        return <AbsoluteFill style={{background: `linear-gradient(115deg, transparent ${pos - 25}%, rgba(255,170,120,0.55) ${pos}%, rgba(120,200,255,0.4) ${pos + 12}%, transparent ${pos + 35}%)`, mixBlendMode: 'screen', opacity: lk}} />;
      })()}
      {/* звук */}
      <Html5Audio src={staticFile(`music_story_${lang}.wav`)} volume={0.22} />
      {Object.entries(d.lines).map(([id, l]) => (
        <Sequence key={id} from={l.start}>
          <Html5Audio src={staticFile(l.file)} volume={1} />
        </Sequence>
      ))}
      {(
        [
          ['type', 2, 0.5], ['type', 26, 0.4], ['whoosh', i1 - 10, 0.4], ['pop', i1 + 12, 0.5], ['pop', i1 + 20, 0.5],
          ['whoosh', sg('s1').start, 0.4], ['send', ln('a1').start + 4, 0.5], ['ding', ln('a2').start, 0.5], ['send', ln('a3').start + 4, 0.5], ['ding', ln('a4').start, 0.5], ['pop', ln('a5').start + 6, 0.5],
          ['whoosh', sg('s2').start, 0.4], ['ding', ln('b2').start, 0.5], ['whoosh', b3, 0.4], ['trash', b3 + 22, 0.8],
          ['whoosh', sg('s3').start, 0.4], ['pop', ln('c1').start + 10, 0.5], ['error', c2.end - 8, 0.6],
          ['whoosh', sg('s4').start, 0.4], ['alarm', ln('d1').start + 8, 0.35], ['pop', ln('d2').start, 0.5], ['pop', ln('d3').start, 0.5],
          ['whoosh', sg('out').start, 0.4], ['pop', ln('e3').start, 0.6], ['chime', ln('e3').start + 2, 0.5],
        ] as [string, number, number][]
      ).map(([n, at, v], i) => (
        <Sequence key={`fx${i}`} from={Math.max(0, Math.round(at))}>
          <Html5Audio src={staticFile(`${n}.wav`)} volume={v} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
export {Appear, Key, Card, Bokeh};
