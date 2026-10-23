import React from 'react';
import {AbsoluteFill, Html5Audio, Img, Sequence, interpolate, staticFile, useCurrentFrame} from 'remotion';
import {Narrator2, NPose} from './Narrator2';
import {Appear, Bokeh, Card, Key} from './Story2';
import {Coffee, Mug, Role, ROLE_C, RobotX} from './BotParts';
import {Lang} from './text';
import EPS1 from './bot_series.json';
import TLS1 from './bot_tl.json';
import EPS2 from './extra_series.json';
import TLS2 from './extra_tl.json';
import {Folder3D} from './Icons3D';
const EPS = [...(EPS1 as any[]), ...(EPS2 as any[])];
const TLS = {...(TLS1 as any), ...(TLS2 as any)};

const FONT = "'Inter Display', 'Inter', 'DejaVu Sans', sans-serif";
const MONO = "'DejaVu Sans Mono', monospace";
const W = 1080;
const H = 1920;
const cl = {extrapolateLeft: 'clamp', extrapolateRight: 'clamp'} as const;
const TITLE = 56;

const NAMES: Record<string, {ru: string; en: string; c: string}> = {
  n: {ru: 'я', en: 'me', c: '#7fe3ff'},
  nr: {ru: 'я (бот)', en: 'me (bot)', c: '#7fe3ff'},
  nw: {ru: 'я (шёпотом)', en: 'me (whisper)', c: '#7fe3ff'},
  hr: {ru: 'HR-бот', en: 'HR-bot', c: ROLE_C.hr},
  col: {ru: 'коллега', en: 'coworker', c: ROLE_C.col},
  guard: {ru: 'охрана', en: 'security', c: ROLE_C.guard},
  boss: {ru: 'босс', en: 'boss', c: ROLE_C.boss},
  old: {ru: 'босс', en: 'boss', c: ROLE_C.boss},
  colh: {ru: 'коллега', en: 'coworker', c: ROLE_C.col},
  plumb: {ru: 'охрана', en: 'security', c: ROLE_C.guard},
  coffee: {ru: 'кофемашина', en: 'coffee machine', c: '#ff4a2a'},
  agent: {ru: 'ИИ-агент', en: 'AI agent', c: '#a46bff'},
};
const SPEAK_ROLE: Record<string, Role> = {hr: 'hr', col: 'col', guard: 'guard', boss: 'boss', old: 'boss', colh: 'col', plumb: 'guard', agent: 'agent'};
const CTA: Record<string, {ru: string; en: string}> = {
  ep1: {ru: 'как думаешь, получится? 👇', en: 'will he pull it off? 👇'},
  ep2: {ru: 'спалят или нет? пиши 👇', en: 'busted or not? comment 👇'},
  ep3: {ru: 'нужен 2 сезон? 👇', en: 'season 2? 👇'},
};

const tx = (v: any, lang: Lang) => (typeof v === 'string' ? v : v[lang]);

export const botDuration = (ep: string, lang: Lang) => (TLS as any)[ep][lang].total as number;

// субтитр с пиканьем
const Sub: React.FC<{who: string; text: string; lang: Lang; at: number; out: number; names?: any}> = ({who, text, lang, at, out, names}) => {
  const nm = names && names[who] ? {...NAMES[who], ...names[who]} : NAMES[who];
  const parts = text.split(/\[(?:бип|beep)\]/);
  return (
    <Appear at={at} out={out} style={{top: 860, left: 40, right: 40, display: 'flex', justifyContent: 'center'}} dy={24}>
      <div style={{background: 'rgba(8,8,12,0.72)', border: '1px solid rgba(255,255,255,0.1)', borderRadius: 28, padding: '14px 26px', maxWidth: 960, backdropFilter: 'blur(10px)'}}>
        <span style={{fontFamily: FONT, fontWeight: 700, fontSize: 28, color: nm.c, marginRight: 14, textTransform: 'uppercase', letterSpacing: 1}}>{nm[lang]}</span>
        <span style={{fontFamily: FONT, fontWeight: 600, fontSize: 42, color: '#fff', lineHeight: 1.2}}>
          {parts.map((p, i) => (
            <React.Fragment key={i}>
              {p}
              {i < parts.length - 1 && (
                <span style={{background: '#ff2a3a', color: '#fff', borderRadius: 8, padding: '0 10px', margin: '0 6px', fontFamily: MONO, fontWeight: 700}}>#@%!</span>
              )}
            </React.Fragment>
          ))}
        </span>
      </div>
    </Appear>
  );
};

export const BotEpisode: React.FC<{ep: string; lang: Lang}> = ({ep, lang}) => {
  const f = useCurrentFrame();
  const E = (EPS as any[]).find((e) => e.id === ep);
  const D = (TLS as any)[ep][lang];
  const ln = (id: string) => D.lines[id];
  const total: number = D.total;
  const st = (id: string, fo = 0) => ln(id).start + fo;
  const toF = (v: any) => (v.to === 'end' ? total + 20 : ln(v.to).start + (v.toFo !== undefined ? v.toFo : -2));
  const lastEnd = ln(E.lines[E.lines.length - 1].id).end;

  // текущая реплика / поза
  let cur = E.lines[0];
  let prevL = E.lines[0];
  for (const l of E.lines) {
    if (f >= ln(l.id).start - 2) {
      prevL = cur;
      cur = l;
    }
  }
  const pose = (f < TITLE ? 'rest' : cur.pose) as NPose;
  const prevPose = (prevL.pose || 'rest') as NPose;
  const pk = Math.min(1, (f - (ln(cur.id).start - 2)) / 7);
  const speakingId = E.lines.find((l: any) => f >= ln(l.id).start && f < ln(l.id).end)?.who;
  const mouth = D.mouth[Math.min(f, D.mouth.length - 1)] || 0;

  // камера
  const hx = Math.sin(f * 0.031) * 4 + Math.sin(f * 0.077) * 2;
  const hy = Math.cos(f * 0.027) * 3;
  let zoom = 1;
  for (const l of E.lines) {
    if (!l.punch) continue;
    const a = ln(l.id).start;
    const b = ln(l.id).end + 10;
    const zin = interpolate(f, [a, a + 7], [0, 1], {...cl, easing: (x) => 1 - Math.pow(1 - x, 3)});
    const zout = interpolate(f, [b, b + 10], [0, 1], cl);
    zoom = Math.max(zoom, 1 + 0.2 * zin * (1 - zout));
  }
  const heroIn = interpolate(f, [TITLE - 14, TITLE + 4], [0, 1], cl);

  // коробка
  const boxV = E.vis.find((v: any) => v.type === 'box');
  let box: {y: number; rot: number; o: number} | undefined;
  if (boxV) {
    const a = st(boxV.from, boxV.fo || 0);
    const drop = interpolate(f, [a, a + 10], [-900, 0], {...cl, easing: (x) => 1 - Math.pow(1 - x, 2)});
    const bounce = f > a + 10 && f < a + 20 ? -Math.sin(((f - a - 10) / 10) * Math.PI) * 30 : 0;
    let y = boxV.from === E.lines[0].id && !boxV.fo ? 0 : drop + bounce;
    let rot = 0;
    let o = f >= a || (boxV.from === E.lines[0].id && !boxV.fo) ? 1 : 0;
    if (boxV.from === E.lines[0].id && !boxV.fo) o = 1;
    if (boxV.off) {
      const b = st(boxV.off, 10);
      const k = interpolate(f, [b, b + 14], [0, 1], {...cl, easing: (x) => x * x});
      y += -k * 1400;
      rot = k * 160;
      if (k >= 1) o = 0;
    }
    box = {y, rot, o};
  }

  // фон
  const bgA = (color: string) => {
    let a = 0;
    for (const v of E.vis) {
      if (v.type !== 'bg' || v.color !== color) continue;
      const s = st(v.from, v.fo || 0);
      const e = toF(v);
      a = Math.max(a, Math.min(interpolate(f, [s - 4, s + 6], [0, 1], cl), interpolate(f, [e, e + 10], [1, 0], cl)));
    }
    return a;
  };
  const alarmV = E.vis.find((v: any) => v.type === 'alarm');
  const alarmOn = alarmV && f >= st(alarmV.from) && f < toF(alarmV);
  const blink = alarmOn ? (Math.floor(f / 6) % 2 ? 1 : 0.35) : 0;

  // переходы: размытие на смене кадров
  const tBlur = Math.max(0, 14 - Math.abs(f - TITLE) * 3);

  const visItems = E.vis.map((v: any, i: number) => {
    const a = st(v.from, v.fo || 0);
    const out = toF(v);
    switch (v.type) {
      case 'key':
        return <Key key={i} text={tx(v.text, lang)} at={a} out={out} top={v.top} size={v.size} color={v.dim ? '#8a8a96' : '#fff'} />;
      case 'chips':
        return (
          <Appear key={i} at={a} out={out} style={{top: v.top, left: 60, right: 60, display: 'flex', flexWrap: 'wrap', gap: 20, justifyContent: 'center'}}>
            {v.items.map((it: any, j: number) => {
              const sk = interpolate(f, [a + 10 + j * 9, a + 18 + j * 9], [0, 1], cl);
              return (
                <div key={j} style={{position: 'relative', fontFamily: FONT, fontWeight: 600, fontSize: 46, color: sk > 0.5 ? '#77777f' : '#fff', padding: '16px 30px', borderRadius: 40, background: 'rgba(255,255,255,0.07)', border: '1px solid rgba(255,255,255,0.12)'}}>
                  {tx(it, lang)}
                  <div style={{position: 'absolute', left: 20, top: '52%', height: 6, width: `calc(${sk * 100}% - 40px)`, background: '#ff3b3b', borderRadius: 3}} />
                </div>
              );
            })}
            <div style={{width: '100%', textAlign: 'center', fontFamily: FONT, fontWeight: 700, fontSize: 64, color: '#fff', marginTop: 30, opacity: interpolate(f, [a + 50, a + 58], [0, 1], cl)}}>
              {lang === 'ru' ? 'всё. забрал ии.' : 'all taken by ai.'}
            </div>
          </Appear>
        );
      case 'robot': {
        const role = v.role as Role;
        const speaking = speakingId && SPEAK_ROLE[speakingId] === role && f < (v.reveal ? 1e9 : 1e9);
        const headOff = v.reveal ? interpolate(f, [st(v.reveal) - 6, st(v.reveal) + 10], [0, 1], {...cl, easing: (x) => x * x}) : 0;
        const turnL = E.lines.find((l: any) => l.sfx === 'turn');
        const look = turnL ? interpolate(f, [st(turnL.id), st(turnL.id) + 10], [0, 1], cl) : 0;
        const posStyle: React.CSSProperties = v.pos === 'left' ? {left: 40} : v.pos === 'right' ? {right: 40} : {left: 0, right: 0, display: 'flex', justifyContent: 'center'};
        const lean = turnL && f > st(turnL.id) ? (v.pos === 'left' ? 6 : v.pos === 'right' ? -6 : 0) : 0;
        return (
          <Appear key={i} at={a} out={out} style={{top: v.top, ...posStyle}}>
            <div style={{transform: `translateY(${Math.sin(f * 0.08 + i) * 8}px) rotate(${lean}deg) scale(${speaking ? 1 + Math.abs(Math.sin(f * 0.5)) * 0.03 : 1})`, transformOrigin: 'center bottom'}}>
              <RobotX role={role} size={v.size * 1.2} t={f + i * 7} speaking={!!speaking} look={look} headOff={headOff} face={v.face} />
            </div>
          </Appear>
        );
      }
      case 'nameplate':
        return (
          <Appear key={i} at={a} out={out} style={{top: v.top, left: 0, right: 0, display: 'flex', justifyContent: 'center'}} dy={20}>
            <div style={{fontFamily: MONO, fontWeight: 700, fontSize: 30, color: '#ffb36b', padding: '8px 22px', borderRadius: 12, background: 'rgba(255,154,60,0.12)', border: '1px solid rgba(255,154,60,0.4)'}}>{tx(v.text, lang)}</div>
          </Appear>
        );
      case 'stamp': {
        if (f < a || f > out + 8) return null;
        const p = interpolate(f, [a, a + 6], [0, 1], cl);
        const o = interpolate(f, [out, out + 8], [1, 0], cl);
        return (
          <div key={i} style={{position: 'absolute', top: v.top, left: 0, right: 0, display: 'flex', justifyContent: 'center', opacity: p * o}}>
            <div style={{transform: `rotate(-12deg) scale(${3 - 2 * p})`, fontFamily: FONT, fontWeight: 900, fontSize: tx(v.text, lang).length > 9 ? 80 : 130, color: v.color, border: `12px solid ${v.color}`, borderRadius: 26, padding: '0 40px', letterSpacing: 4, background: 'rgba(0,0,0,0.25)', boxShadow: `0 0 60px ${v.color}55`}}>
              {tx(v.text, lang)}
            </div>
          </div>
        );
      }
      case 'sign':
        return (
          <Appear key={i} at={a} out={out} style={{top: v.top, left: 110, right: 110}}>
            <div style={{transform: `rotate(-2deg)`, background: 'linear-gradient(180deg,#fffbea,#f3e7b8)', borderRadius: 10, padding: '44px 40px', fontFamily: FONT, color: '#1a1a1a', textAlign: 'center', boxShadow: '0 30px 60px rgba(0,0,0,0.45)', position: 'relative'}}>
              <div style={{position: 'absolute', top: -18, left: '42%', width: 120, height: 36, background: 'rgba(255,255,255,0.6)', transform: 'rotate(4deg)'}} />
              <div style={{fontSize: 30, fontWeight: 700, color: '#c0392b', letterSpacing: 3}}>{lang === 'ru' ? 'ВНИМАНИЕ' : 'NOTICE'}</div>
              <div style={{fontSize: 70, fontWeight: 900, lineHeight: 1.05, margin: '14px 0 22px'}}>{tx(v.title, lang)}</div>
              {v.lines.map((l: any, j: number) => (
                <div key={j} style={{fontSize: 44, fontWeight: 600, color: '#444'}}>• {tx(l, lang)}</div>
              ))}
            </div>
          </Appear>
        );
      case 'captcha': {
        const ok = f >= st(v.checkAt);
        const ans = f >= st('l5') ? (lang === 'ru' ? '332 024' : '332,024') : '?';
        return (
          <Appear key={i} at={a} out={out} style={{top: v.top, left: 90, right: 90}}>
            <Card light style={{padding: '30px 36px'}}>
              <div style={{display: 'flex', alignItems: 'center', gap: 22}}>
                <div style={{width: 64, height: 64, borderRadius: 10, border: `4px solid ${ok ? '#22c55e' : '#c3c3cc'}`, background: ok ? '#22c55e' : '#fff', color: '#fff', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 44, fontWeight: 900}}>{ok ? '✓' : ''}</div>
                <div style={{fontSize: 42, fontWeight: 700, color: '#222'}}>{lang === 'ru' ? 'я НЕ человек' : "I'm NOT a human"}</div>
                <div style={{marginLeft: 'auto', fontFamily: MONO, fontSize: 24, color: '#999'}}>CAPTCHA</div>
              </div>
              <div style={{marginTop: 22, padding: '18px 22px', borderRadius: 16, background: '#f3f4f8', fontFamily: MONO, fontSize: 58, fontWeight: 700, color: '#111', textAlign: 'center'}}>
                847 × 392 = <span style={{color: ans === '?' ? '#b0b0ba' : '#2f7bff'}}>{ans}</span>
              </div>
            </Card>
          </Appear>
        );
      }
      case 'calc': {
        const typed = '847×392';
        const n = Math.min(typed.length, Math.max(0, Math.floor((f - a - 4) / 3)));
        return (
          <Appear key={i} at={a} out={out} style={{top: v.top + 60, right: 50}}>
            <div style={{transform: 'rotate(8deg)', width: 300, borderRadius: 40, background: '#111', border: '6px solid #2a2a30', padding: 22, boxShadow: '0 20px 50px rgba(0,0,0,0.6)'}}>
              <div style={{fontFamily: MONO, color: '#fff', fontSize: 40, textAlign: 'right', minHeight: 54}}>{typed.slice(0, n)}{Math.floor(f / 8) % 2 ? '|' : ''}</div>
              <div style={{display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 10, marginTop: 10}}>
                {Array.from({length: 12}).map((_, j) => (
                  <div key={j} style={{height: 46, borderRadius: 23, background: j % 4 === 3 ? '#ff9f0a' : '#333', opacity: (f + j * 3) % 18 < 3 ? 0.5 : 1}} />
                ))}
              </div>
            </div>
          </Appear>
        );
      }
      case 'cup':
        return (
          <Appear key={i} at={a} out={out} style={{top: v.top, right: 90}}>
            <Mug t={f} />
          </Appear>
        );
      case 'growl': {
        if (f < a || f > out + 6) return null;
        const word = lang === 'ru' ? 'УРРРРРРР' : 'GRRRRRRR';
        return (
          <div key={i} style={{position: 'absolute', top: v.top, left: 0, right: 0, textAlign: 'center', fontFamily: FONT, fontWeight: 900, fontSize: 120, color: '#ffd23f', textShadow: '0 0 40px rgba(255,210,63,0.6)', transform: `translate(${Math.sin(f * 2.5) * 10}px,${Math.cos(f * 3.1) * 8}px)`}}>
            {word.split('').map((ch, j) => (
              <span key={j} style={{display: 'inline-block', transform: `translateY(${Math.sin(f * 0.6 + j) * 18}px) scale(${interpolate(f, [a + j * 2, a + j * 2 + 5], [0, 1], cl)})`}}>{ch}</span>
            ))}
          </div>
        );
      }
      case 'coffee': {
        const speaking = speakingId === 'coffee';
        return (
          <Appear key={i} at={a} out={out} style={{top: v.top, left: 0, right: 0, display: 'flex', justifyContent: 'center'}} dy={80}>
            <div style={{transform: `scale(${speaking ? 1 + Math.abs(Math.sin(f * 0.4)) * 0.03 : 1})`}}>
              <Coffee t={f} speaking={speaking} size={400} />
            </div>
          </Appear>
        );
      }
      case 'lamp': {
        const sw = Math.sin(f * 0.035) * 6;
        return (
          <AbsoluteFill key={i} style={{pointerEvents: 'none'}}>
            <AbsoluteFill style={{background: 'rgba(0,0,0,0.55)'}} />
            <div style={{position: 'absolute', left: 540 - 520, top: -40, width: 1040, height: 1500, transformOrigin: '50% 0', transform: `rotate(${sw}deg)`, background: 'conic-gradient(from 160deg at 50% 0%, transparent 0deg, rgba(255,226,160,0.22) 14deg, rgba(255,226,160,0.30) 20deg, rgba(255,226,160,0.22) 26deg, transparent 40deg)', mixBlendMode: 'screen'}} />
            <div style={{position: 'absolute', left: 540 - 70 + Math.sin(f * 0.035) * -4, top: 40, width: 140, height: 70, borderRadius: '70px 70px 10px 10px', background: 'linear-gradient(180deg,#3a3d48,#15161b)', boxShadow: '0 30px 60px rgba(255,220,150,0.35)', transform: `rotate(${sw}deg)`, transformOrigin: '50% -40px'}} />
          </AbsoluteFill>
        );
      }
      case 'db': {
        const t0 = a + 4;
        const p = interpolate(f, [t0, t0 + 50], [0, 1], cl);
        const secs = (p * 9).toFixed(2);
        const rows = 6;
        return (
          <Appear key={i} at={a} out={out} style={{top: v.top + 330, left: 50}}>
            <div style={{display: 'flex', alignItems: 'center', gap: 24}}>
              <svg width={200} height={240} viewBox="-100 -120 200 240" style={{overflow: 'visible'}}>
                {Array.from({length: rows}).map((_, j) => {
                  const gone = p * rows > rows - 1 - j;
                  const y = -90 + j * 36;
                  return (
                    <g key={j} opacity={gone ? 0.08 : 1} transform={`translate(${gone ? (j % 2 ? 30 : -30) * p : 0},0)`}>
                      <ellipse cx={0} cy={y + 30} rx={80} ry={18} fill="#2d3b8a" />
                      <rect x={-80} y={y} width={160} height={30} fill="#4f6bff" />
                      <ellipse cx={0} cy={y} rx={80} ry={18} fill="#8fa2ff" />
                    </g>
                  );
                })}
              </svg>
              <div style={{fontFamily: MONO, color: '#fff'}}>
                <div style={{fontSize: 30, color: '#9a9aa6'}}>DROP DATABASE prod;</div>
                <div style={{fontSize: 96, fontWeight: 700, color: p >= 1 ? '#ff4d5a' : '#fff'}}>{secs}s</div>
                <div style={{fontSize: 34, fontWeight: 700, color: '#ff4d5a', opacity: p >= 1 ? 1 : 0}}>{lang === 'ru' ? 'УДАЛЕНО: ВСЁ' : 'DELETED: EVERYTHING'}</div>
              </div>
            </div>
          </Appear>
        );
      }
      case 'backups':
        return (
          <Appear key={i} at={a} out={out} style={{top: v.top + 360, left: 40, display: 'flex', gap: 6, alignItems: 'center'}}>
            <div style={{opacity: 0.35, filter: 'grayscale(1)'}}><Folder3D size={190} label="prod" /></div>
            <div style={{fontSize: 70, transform: `scale(${1 + Math.abs(Math.sin(f * 0.25)) * 0.15})`}}>❤️</div>
            <div style={{opacity: 0.35, filter: 'grayscale(1)'}}><Folder3D size={190} label="backup" /></div>
          </Appear>
        );
      case 'poem':
        return (
          <Appear key={i} at={a} out={out} style={{top: v.top, left: 80, right: 80}}>
            <Card style={{padding: '30px 38px', borderLeft: '6px solid #a46bff'}}>
              <div style={{fontFamily: FONT, fontSize: 28, fontWeight: 700, color: '#a46bff', marginBottom: 10, letterSpacing: 1}}>{lang === 'ru' ? 'ОДА УДАЛЁННОЙ БАЗЕ' : 'ODE TO A DELETED DATABASE'}</div>
              {v.lines.map((l2: any, j: number) => (
                <div key={j} style={{fontFamily: FONT, fontStyle: 'italic', fontSize: 40, color: '#eee', lineHeight: 1.35, opacity: interpolate(f, [a + j * 14, a + j * 14 + 8], [0, 1], cl)}}>{tx(l2, lang)}</div>
              ))}
            </Card>
          </Appear>
        );
      case 'scan': {
        if (f < a || f > out + 6) return null;
        const o = Math.min(interpolate(f, [a, a + 5], [0, 1], cl), interpolate(f, [out, out + 6], [1, 0], cl));
        const k = interpolate(f, [a, a + 8], [1.3, 1], cl);
        const L = 60;
        const sl = (f - a) % 40 / 40;
        return (
          <div key={i} style={{position: 'absolute', left: v.x, top: v.y, width: v.w, height: v.h, opacity: o, transform: `scale(${k})`}}>
            {[[0, 0, 1, 1], [1, 0, -1, 1], [0, 1, 1, -1], [1, 1, -1, -1]].map(([cx, cy, sx, sy], j) => (
              <svg key={j} width={L} height={L} style={{position: 'absolute', left: cx ? v.w - L : 0, top: cy ? v.h - L : 0, overflow: 'visible'}}>
                <path d={`M${cx ? L : 0},${cy ? L - L : L} ${''}`} />
                <path d={`M${sx > 0 ? 0 : L},${sy > 0 ? L : 0} L${sx > 0 ? 0 : L},${sy > 0 ? 0 : L} L${sx > 0 ? L : 0},${sy > 0 ? 0 : L}`} stroke="#ff3b3b" strokeWidth={8} fill="none" />
              </svg>
            ))}
            <div style={{position: 'absolute', left: 0, right: 0, top: sl * v.h, height: 4, background: 'rgba(255,59,59,0.6)', boxShadow: '0 0 20px #ff3b3b'}} />
            <div style={{position: 'absolute', left: 0, top: -58, fontFamily: MONO, fontWeight: 700, fontSize: 36, color: '#fff', background: '#ff3b3b', padding: '4px 14px', borderRadius: 6}}>{tx(v.label, lang)}</div>
          </div>
        );
      }
      case 'pigeon': {
        if (f < a || f > out + 6) return null;
        const flee = interpolate(f, [a + 22, a + 46], [0, 1], {...cl, easing: (x) => x * x});
        const flap = Math.sin(f * (flee > 0 ? 1.4 : 0.2)) * (flee > 0 ? 30 : 4);
        return (
          <div key={i} style={{position: 'absolute', left: 160 - flee * 400, top: v.top - flee * 300, opacity: 1 - flee}}>
            <svg width={240} height={200} viewBox="-120 -100 240 200" style={{overflow: 'visible'}}>
              <ellipse cx={0} cy={20} rx={80} ry={55} fill="#8a93a6" />
              <ellipse cx={-10} cy={30} rx={60} ry={35} fill="#a7afc0" />
              <circle cx={60} cy={-30} r={34} fill="#6b7590" />
              <path d="M60,-6 Q74,0 70,14" fill="#4fb38a" opacity={0.8} />
              <circle cx={70} cy={-38} r={7} fill="#ff7a1a" />
              <circle cx={71} cy={-38} r={3} fill="#111" />
              <path d="M92,-30 L112,-24 L92,-20 Z" fill="#e0a060" />
              <path d={`M-20,0 Q-60,${-60 - flap} -100,${-20 - flap} Q-60,10 -20,20 Z`} fill="#6b7590" />
              <path d="M-80,30 L-120,40 L-80,50 Z" fill="#5a6378" />
              <path d="M10,72 L0,96 M30,72 L40,96" stroke="#e0a060" strokeWidth={6} />
            </svg>
          </div>
        );
      }
      case 'call': {
        const dec = f >= a + 30;
        return (
          <Appear key={i} at={a} out={out} style={{top: v.top, left: 70}}>
            <div style={{width: 520, borderRadius: 50, background: 'linear-gradient(180deg,#2a2d38,#14151b)', border: '1px solid #33363f', padding: '36px 30px', fontFamily: FONT, color: '#fff', textAlign: 'center', boxShadow: '0 30px 70px rgba(0,0,0,0.6)', transform: `translateX(${!dec ? Math.sin(f * 2) * 4 : 0}px)`}}>
              <div style={{fontSize: 30, color: '#9a9aa6'}}>{dec ? (lang === 'ru' ? 'вызов отклонён' : 'call declined') : lang === 'ru' ? 'входящий вызов…' : 'incoming call…'}</div>
              <div style={{fontSize: 64, fontWeight: 700, margin: '10px 0 30px'}}>{tx(v.name, lang)}</div>
              <div style={{display: 'flex', justifyContent: 'space-around'}}>
                <div style={{width: 110, height: 110, borderRadius: 55, background: '#ff3b3b', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 50, transform: `scale(${dec ? 1.2 : 1})`, boxShadow: dec ? '0 0 40px #ff3b3b' : 'none'}}>✕</div>
                <div style={{width: 110, height: 110, borderRadius: 55, background: '#22c55e', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 50, opacity: dec ? 0.3 : 1}}>✆</div>
              </div>
            </div>
          </Appear>
        );
      }
      case 'fridge': {
        const lk = f >= st(v.lockAt) + 20;
        const lp = interpolate(f, [st(v.lockAt) + 20, st(v.lockAt) + 28], [2.5, 1], cl);
        return (
          <Appear key={i} at={a} out={out} style={{top: v.top, left: 90}}>
            <svg width={340} height={560} viewBox="-170 -280 340 560" style={{overflow: 'visible'}}>
              <defs>
                <linearGradient id="fr" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0" stopColor="#c9ced8" />
                  <stop offset="0.4" stopColor="#ffffff" />
                  <stop offset="1" stopColor="#9aa1b0" />
                </linearGradient>
              </defs>
              <ellipse cx={0} cy={270} rx={150} ry={14} fill="#000" opacity={0.4} />
              <rect x={-140} y={-270} width={280} height={530} rx={30} fill="url(#fr)" />
              <path d="M-140,-90 L140,-90" stroke="#9aa1b0" strokeWidth={6} />
              <rect x={100} y={-220} width={14} height={90} rx={7} fill="#7b8191" />
              <rect x={100} y={-50} width={14} height={140} rx={7} fill="#7b8191" />
              <ellipse cx={-70} cy={-200} rx={40} ry={12} fill="#fff" opacity={0.7} />
              {lk && (
                <g transform={`translate(60,30) scale(${lp})`}>
                  <path d="M-40,-30 L-40,-60 A40,40 0 0 1 40,-60 L40,-30" stroke="#5a5f6b" strokeWidth={16} fill="none" />
                  <rect x={-60} y={-34} width={120} height={100} rx={18} fill="#f5c542" stroke="#a67c10" strokeWidth={5} />
                  <circle cx={0} cy={6} r={12} fill="#5a3a08" />
                  <rect x={-5} y={10} width={10} height={26} fill="#5a3a08" />
                </g>
              )}
              {lk && <path d="M-150,-180 L150,40 M-150,40 L150,-180" stroke="#ff3b3b" strokeWidth={14} opacity={0.0} />}
            </svg>
          </Appear>
        );
      }
      case 'newsdesk': {
        const txt = tx(v.ticker, lang);
        const w = txt.length * 26 + 200;
        const off = (f * 6) % w;
        return (
          <AbsoluteFill key={i} style={{pointerEvents: 'none'}}>
            <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(10,30,80,0.55), rgba(5,8,20,0.2) 50%, rgba(5,8,20,0.6))'}} />
            {/* экран-студия */}
            <div style={{position: 'absolute', left: 60, right: 60, top: 150, height: 700, borderRadius: 30, border: '2px solid rgba(80,160,255,0.25)', background: 'radial-gradient(ellipse at 50% 40%, rgba(40,110,255,0.18), rgba(0,0,0,0) 70%)'}} />
            {[0, 1, 2, 3].map((k2) => (
              <div key={k2} style={{position: 'absolute', left: 60 + k2 * 240, top: 150, width: 2, height: 700, background: 'rgba(80,160,255,0.08)'}} />
            ))}
            {/* бегущая строка */}
            <div style={{position: 'absolute', left: 0, right: 0, top: 96, height: 52, background: '#d7202f', overflow: 'hidden', display: 'flex', alignItems: 'center'}}>
              <div style={{position: 'absolute', left: 0, zIndex: 2, height: 52, padding: '0 22px', background: '#111', color: '#fff', fontFamily: FONT, fontWeight: 900, fontSize: 30, display: 'flex', alignItems: 'center', letterSpacing: 2}}>
                {lang === 'ru' ? 'СРОЧНО' : 'BREAKING'}
              </div>
              <div style={{position: 'absolute', left: 220 - off, whiteSpace: 'nowrap', color: '#fff', fontFamily: FONT, fontWeight: 700, fontSize: 32}}>
                {txt}&nbsp;&nbsp;•&nbsp;&nbsp;{txt}&nbsp;&nbsp;•&nbsp;&nbsp;{txt}
              </div>
            </div>
            <div style={{position: 'absolute', right: 70, top: 168, display: 'flex', alignItems: 'center', gap: 10, fontFamily: FONT, fontWeight: 800, fontSize: 26, color: '#fff', opacity: 0.85}}>
              <span style={{width: 14, height: 14, borderRadius: 7, background: '#ff3b3b', opacity: Math.floor(f / 15) % 2 ? 1 : 0.3}} /> LIVE
            </div>
          </AbsoluteFill>
        );
      }
      case 'headline': {
        const tagC = v.tagColor || '#2f7bff';
        return (
          <Appear key={i} at={a} out={out} style={{top: v.top || 230, left: 70, right: 70}}>
            <div style={{background: 'linear-gradient(180deg,#ffffff,#eef1f7)', borderRadius: 26, padding: '26px 32px 22px', boxShadow: '0 30px 70px rgba(0,0,0,0.5)', borderLeft: `10px solid ${tagC}`}}>
              <div style={{display: 'inline-block', background: tagC, color: '#fff', fontFamily: FONT, fontWeight: 800, fontSize: 26, letterSpacing: 2, padding: '6px 16px', borderRadius: 8, marginBottom: 14}}>{tx(v.tag, lang)}</div>
              <div style={{fontFamily: FONT, fontWeight: 800, fontSize: 50, lineHeight: 1.12, color: '#111'}}>{tx(v.text, lang)}</div>
              <div style={{fontFamily: FONT, fontWeight: 600, fontSize: 26, color: '#6b6b76', marginTop: 14}}>{lang === 'ru' ? 'источник: ' : 'source: '}{v.source}</div>
            </div>
          </Appear>
        );
      }
      case 'rank':
        return (
          <Appear key={i} at={a} out={out} style={{top: v.top || 170, left: 70}}>
            <div style={{fontFamily: FONT, fontWeight: 900, fontSize: 120, color: '#ffd23f', textShadow: '0 0 40px rgba(255,210,63,0.5)', lineHeight: 1}}>#{v.n}</div>
          </Appear>
        );
      case 'rocket': {
        const rain = !!v.rain;
        const shake = rain ? Math.sin(f * 1.7) * 3 : 0;
        return (
          <Appear key={i} at={a} out={out} style={{top: v.top || 260, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
            <svg width={520} height={560} viewBox="-260 -300 520 560" style={{overflow: 'visible'}}>
              <defs>
                <linearGradient id="rk" x1="0" y1="0" x2="1" y2="0">
                  <stop offset="0" stopColor="#c9ced8" />
                  <stop offset="0.45" stopColor="#ffffff" />
                  <stop offset="1" stopColor="#8f97a8" />
                </linearGradient>
              </defs>
              <rect x={-240} y={220} width={480} height={30} rx={8} fill="#2a2d38" />
              <rect x={-150} y={-140} width={24} height={360} fill="#3a3d48" />
              <rect x={-150} y={-40} width={110} height={12} fill="#3a3d48" />
              <g transform={`translate(${shake},0)`}>
                <path d="M0,-260 C40,-220 50,-150 50,-80 L50,190 L-50,190 L-50,-80 C-50,-150 -40,-220 0,-260 Z" fill="url(#rk)" stroke="#6b7385" strokeWidth={4} />
                <circle cx={0} cy={-110} r={22} fill="#2f7bff" stroke="#1a3d80" strokeWidth={5} />
                <path d="M-50,120 L-95,200 L-50,190 Z M50,120 L95,200 L50,190 Z" fill="#d7202f" />
                <text x={0} y={60} textAnchor="middle" fontFamily={FONT} fontWeight={900} fontSize={22} fill="#1a1a1a" transform="rotate(-90,0,60)">STARLINK</text>
              </g>
              {rain && (
                <g>
                  {[-150, 0, 150].map((cx) => (
                    <g key={cx} transform={`translate(${cx + Math.sin(f * 0.05 + cx) * 10},-250)`}>
                      <ellipse cx={0} cy={0} rx={90} ry={40} fill="#5a6378" />
                      <ellipse cx={-50} cy={10} rx={50} ry={30} fill="#4a5266" />
                      <ellipse cx={55} cy={8} rx={55} ry={30} fill="#4a5266" />
                    </g>
                  ))}
                  {Array.from({length: 26}).map((_, j) => {
                    const x = ((j * 97) % 480) - 240;
                    const y = ((f * 14 + j * 53) % 460) - 210;
                    return <path key={j} d={`M${x},${y} l-6,22`} stroke="#9fd0ff" strokeWidth={4} strokeLinecap="round" opacity={0.8} />;
                  })}
                </g>
              )}
            </svg>
          </Appear>
        );
      }
      case 'tv': {
        const clean = v.cleanAt && f >= st(v.cleanAt);
        return (
          <Appear key={i} at={a} out={out} style={{top: v.top || 300, left: 0, right: 0, display: 'flex', justifyContent: 'center'}}>
            <div style={{position: 'relative', width: 640, height: 400, borderRadius: 18, background: '#0b0b10', border: '14px solid #1e2028', boxShadow: '0 30px 60px rgba(0,0,0,0.6)', overflow: 'hidden'}}>
              {!clean ? (
                <div style={{position: 'absolute', inset: 0, display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: 10, padding: 14}}>
                  {Array.from({length: 12}).map((_, j) => (
                    <div key={j} style={{borderRadius: 10, background: ['#ff6a2b', '#ffd23f', '#2f7bff', '#ff3bd0'][j % 4], display: 'flex', alignItems: 'center', justifyContent: 'center', fontFamily: FONT, fontWeight: 900, fontSize: 26, color: '#fff', transform: `scale(${1 + Math.sin(f * 0.6 + j) * 0.04})`}}>AD</div>
                  ))}
                </div>
              ) : (
                <div style={{position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', background: 'radial-gradient(ellipse, #1a2a50, #05070f)', fontFamily: FONT, fontWeight: 800, fontSize: 44, color: '#7fe3ff'}}>
                  {lang === 'ru' ? '✓ реклама удалена' : '✓ ads removed'}
                </div>
              )}
            </div>
          </Appear>
        );
      }
      default:
        return null;
    }
  });

  // звуки
  const sfx: [string, number, number][] = [['whoosh', 2, 0.5], ['scratch', 6, 0.25], ['pop', TITLE - 10, 0.4]];
  for (const v of E.vis) {
    const a = st(v.from, v.fo || 0);
    if (v.type === 'robot') {
      sfx.push(['servo', a, 0.5], ['pop', a + 2, 0.4]);
      if (v.reveal) sfx.push(['servo', st(v.reveal) - 6, 0.6], ['pop', st(v.reveal) + 4, 0.6]);
    }
    if (v.type === 'stamp') sfx.push(['stamp', a, 1]);
    if (v.type === 'box') {
      if (v.fo !== undefined || v.from !== E.lines[0].id) sfx.push(['thud', a + 10, 0.9]);
      if (v.off) sfx.push(['whoosh', st(v.off, 10), 0.6]);
    }
    if (v.type === 'captcha') sfx.push(['pop', a, 0.5], ['ding', st(v.checkAt), 0.6]);
    if (v.type === 'calc') for (let j = 0; j < 7; j++) sfx.push(['tick', a + 4 + j * 3, 0.5]);
    if (v.type === 'chips') for (let j = 0; j < v.items.length; j++) sfx.push(['tick', a + 12 + j * 9, 0.6]);
    if (v.type === 'sign') sfx.push(['pop', a, 0.6]);
    if (v.type === 'cup') sfx.push(['pop', a, 0.4]);
    if (v.type === 'alarm') sfx.push(['alarm', a, 0.45]);
    if (v.type === 'coffee') sfx.push(['boom', a, 1]);
  }
  for (const l of E.lines) {
    if (l.sfx === 'growl') sfx.push(['growl', st(l.id), 1]);
    if (l.sfx === 'crickets') sfx.push(['crickets', st(l.id) + 4, 0.8]);
    if (l.sfx === 'turn') {
      sfx.push(['servo', st(l.id), 0.6], ['servo', st(l.id) + 5, 0.6], ['servo', st(l.id) + 10, 0.6], ['scratch', st(l.id) + 2, 0.4]);
    }
  }
  sfx.push(['whoosh', lastEnd + 8, 0.5]);

  return (
    <AbsoluteFill style={{background: '#0a0a0d', overflow: 'hidden'}}>
      {/* фоны */}
      <AbsoluteFill style={{background: `radial-gradient(ellipse at 50% 35%, ${E.accent}22 0%, #121218 45%, #0a0a0d 75%)`}} />
      <Bokeh f={f} tint={1} />
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 30%, #1a2a6a 0%, #070a1e 70%)', opacity: bgA('night')}} />
      <AbsoluteFill style={{background: '#050507', opacity: bgA('dark')}} />
      {bgA('dark') > 0 && <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 25%, rgba(255,60,30,0.28) 0%, transparent 45%)', opacity: bgA('dark')}} />}
      {alarmOn && <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 50%, transparent 40%, rgba(255,20,30,0.55) 100%)', opacity: blink}} />}

      <AbsoluteFill style={{transform: `translate(${hx}px,${hy}px)`, filter: tBlur > 0.3 ? `blur(${tBlur}px)` : undefined}}>
        {f >= TITLE - 8 && visItems}
        {/* герой */}
        <svg viewBox={`0 0 ${W} ${H}`} width={W} height={H} style={{position: 'absolute', inset: 0, opacity: heroIn}}>
          <g transform={`translate(540,1300) scale(${zoom}) translate(-540,-1300) translate(0,${(1 - heroIn) * 200})`}>
            <Narrator2 t={f} x={540} y={1995} pose={pose} prev={prevPose} k={pk} mouth={mouth} box={box} />
          </g>
        </svg>
        {(() => {
          const nd = E.vis.find((v: any) => v.type === 'newsdesk');
          if (!nd || f < st(nd.from) - 4) return null;
          return (
            <div style={{position: 'absolute', left: -20, right: -20, top: 1690, height: 260, background: 'linear-gradient(180deg,#1b2a55,#0b1230)', borderTop: '6px solid #2f7bff', boxShadow: '0 -20px 40px rgba(0,0,0,0.5)', display: 'flex', alignItems: 'flex-start', justifyContent: 'center', paddingTop: 34}}>
              <div style={{fontFamily: FONT, fontWeight: 900, fontSize: 54, color: '#fff', letterSpacing: 4}}>
                M1<span style={{color: '#ff3b3b'}}>●</span>{lang === 'ru' ? 'НОВОСТИ ИИ' : 'AI NEWS'}
              </div>
            </div>
          );
        })()}
        {E.lines.map((l: any) =>
          l.who === 'fx' ? null : <Sub key={l.id} who={l.who} text={l.text[lang]} lang={lang} at={st(l.id)} out={ln(l.id).end + 4} names={E.names} />,
        )}
      </AbsoluteFill>

      {/* заставка */}
      {f < TITLE + 8 && (
        <AbsoluteFill style={{background: '#050507', opacity: interpolate(f, [TITLE - 6, TITLE + 6], [1, 0], cl), display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center'}}>
          {[['#ff2a6a', -6], ['#2ad4ff', 6], ['#fff', 0]].map(([c, dx], j) => {
            const g = f < 14 && f % 4 < 2 ? 1 : 0;
            return (
              <div key={j} style={{position: 'absolute', top: 760, left: 0, right: 0, textAlign: 'center', fontFamily: FONT, fontWeight: 900, fontSize: lang === 'ru' ? 112 : 104, letterSpacing: -2, lineHeight: 1, whiteSpace: 'pre-line', color: c as string, mixBlendMode: j < 2 ? 'screen' : 'normal', transform: `translateX(${(dx as number) * (1 + g * 4)}px) scale(${interpolate(f, [0, 12], [1.25, 1], cl)})`, opacity: j < 2 ? 0.75 : interpolate(f, [2, 8], [0, 1], cl)}}>
                {E.show ? tx(E.show, lang) : lang === 'ru' ? 'ПРИТВОРИСЬ\nБОТОМ' : 'PRETEND TO\nBE A BOT'}
              </div>
            );
          })}
          <div style={{position: 'absolute', top: 1030, left: 0, right: 0, textAlign: 'center', fontFamily: FONT, fontWeight: 600, fontSize: 44, color: E.accent, opacity: interpolate(f, [14, 22], [0, 1], cl), letterSpacing: 2}}>
            {E.num ? `${lang === 'ru' ? 'серия ' : 'episode '}${E.num} · ` : ''}{tx(E.title, lang)}
          </div>
        </AbsoluteFill>
      )}

      {/* финальная плашка */}
      {f > lastEnd + 8 && (
        <AbsoluteFill style={{background: 'rgba(5,5,8,0.6)', opacity: interpolate(f, [lastEnd + 8, lastEnd + 18], [0, 1], cl), display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', gap: 26}}>
          <div style={{fontFamily: FONT, fontWeight: 800, fontSize: 84, color: '#fff', letterSpacing: -1, transform: `translateY(${interpolate(f, [lastEnd + 8, lastEnd + 20], [40, 0], cl)}px)`}}>{tx(E.end, lang)}</div>
          <div style={{fontFamily: FONT, fontWeight: 600, fontSize: 46, color: E.accent, opacity: interpolate(f, [lastEnd + 18, lastEnd + 28], [0, 1], cl)}}>{E.cta ? tx(E.cta, lang) : CTA[ep][lang]}</div>
        </AbsoluteFill>
      )}

      {/* пост-обработка */}
      <AbsoluteFill style={{background: 'linear-gradient(180deg, rgba(40,90,140,0.3), rgba(0,0,0,0) 45%, rgba(160,80,40,0.22))', mixBlendMode: 'soft-light'}} />
      <AbsoluteFill style={{background: 'radial-gradient(ellipse at 50% 45%, transparent 55%, rgba(0,0,0,0.55) 100%)'}} />
      <AbsoluteFill style={{opacity: 0.08, mixBlendMode: 'overlay'}}>
        <Img src={staticFile(`grain/g${f % 8}.png`)} style={{width: W, height: H}} />
      </AbsoluteFill>

      {/* звук */}
      <Html5Audio src={staticFile(`music_bot_${ep}_${lang}.wav`)} volume={0.2} />
      {E.lines.map((l: any) =>
        ln(l.id).file ? (
          <Sequence key={l.id} from={ln(l.id).start}>
            <Html5Audio src={staticFile(ln(l.id).file)} volume={1} />
          </Sequence>
        ) : null,
      )}
      {sfx.map(([n, at, vol], i) => (
        <Sequence key={`x${i}`} from={Math.max(0, Math.round(at))}>
          <Html5Audio src={staticFile(`${n}.wav`)} volume={vol} />
        </Sequence>
      ))}
    </AbsoluteFill>
  );
};
