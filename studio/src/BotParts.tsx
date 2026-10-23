import React from 'react';

export type Role = 'hr' | 'col' | 'guard' | 'boss' | 'agent';
export const ROLE_C: Record<Role, string> = {hr: '#ff9a3c', col: '#3fd6b2', guard: '#ff3b3b', boss: '#f5c542', agent: '#a46bff'};
const FONT = "'Inter Display', 'Inter', 'DejaVu Sans', sans-serif";
const MONO = "'DejaVu Sans Mono', monospace";

// ───────── лица под шлемом ─────────
export const Face: React.FC<{type: 'old' | 'tired' | 'mustache'; t: number}> = ({type, t}) => {
  const skin = type === 'old' ? '#efc3a2' : type === 'tired' ? '#e9bc9a' : '#d9a07c';
  return (
    <g>
      <ellipse cx={0} cy={-20} rx={92} ry={104} fill={skin} stroke="#b77d5e" strokeWidth={5} />
      {type === 'old' && (
        <>
          <path d="M-92,-30 C-100,-90 -70,-110 -60,-60 Z M92,-30 C100,-90 70,-110 60,-60 Z" fill="#f2f2f2" />
          <ellipse cx={-26} cy={-92} rx={30} ry={10} fill="#fff" opacity={0.55} />
          {[-34, 34].map((x) => <circle key={x} cx={x} cy={-24} r={24} fill="none" stroke="#3a3a3a" strokeWidth={6} />)}
          <path d="M-10,-24 L10,-24" stroke="#3a3a3a" strokeWidth={6} />
          {[-34, 34].map((x) => <circle key={x} cx={x} cy={-22} r={6} fill="#222" />)}
          <path d="M-46,26 Q-24,6 0,22 Q24,6 46,26 Q24,44 0,32 Q-24,44 -46,26 Z" fill="#f4f4f4" stroke="#cfcfcf" strokeWidth={3} />
          <path d={`M70,${-60 + ((t * 2) % 30)} q8,14 0,22 q-8,-8 0,-22`} fill="#7fd0ff" />
        </>
      )}
      {type === 'tired' && (
        <>
          <path d="M-96,-40 C-104,-120 -40,-140 0,-128 C50,-142 110,-110 96,-40 C80,-90 50,-100 20,-96 L10,-80 L-6,-98 C-40,-100 -80,-86 -96,-40 Z" fill="#3a2a22" />
          {[-34, 34].map((x) => (
            <g key={x}>
              <ellipse cx={x} cy={-20} rx={16} ry={8} fill="#222" />
              <path d={`M${x - 18},-6 q18,10 36,0`} stroke="#9a6a5a" strokeWidth={4} fill="none" />
              <path d={`M${x - 18},-30 L${x + 18},-30`} stroke={skin} strokeWidth={10} />
            </g>
          ))}
          <path d="M-22,40 Q0,30 22,40" stroke="#7a3a30" strokeWidth={6} fill="none" strokeLinecap="round" />
          {Array.from({length: 18}).map((_, i) => <circle key={i} cx={-50 + (i % 9) * 12} cy={52 + Math.floor(i / 9) * 12} r={2} fill="#6a5040" opacity={0.6} />)}
        </>
      )}
      {type === 'mustache' && (
        <>
          <path d="M-100,-50 C-100,-120 100,-120 100,-50 L110,-44 L-110,-44 Z" fill="#2f5dbf" />
          <rect x={-40} y={-104} width={80} height={24} rx={8} fill="#24478f" />
          <text x={0} y={-62} textAnchor="middle" fontFamily={FONT} fontWeight={800} fontSize={22} fill="#fff">PLUMB</text>
          {[-32, 32].map((x) => <circle key={x} cx={x} cy={-12} r={8} fill="#222" />)}
          <path d="M-52,-34 L-14,-28 M14,-28 L52,-34" stroke="#222" strokeWidth={9} strokeLinecap="round" />
          <path d="M-70,30 Q-40,0 0,18 Q40,0 70,30 Q40,22 0,36 Q-40,22 -70,30 Z" fill="#1d1d1d" />
        </>
      )}
    </g>
  );
};

// ───────── робот с ролью ─────────
export const RobotX: React.FC<{
  role: Role;
  size: number;
  t: number;
  speaking?: boolean;
  look?: number; // 0 вперёд, 1 вниз на героя
  headOff?: number;
  face?: 'old' | 'tired' | 'mustache';
}> = ({role, size, t, speaking, look = 0, headOff = 0, face}) => {
  const c = ROLE_C[role];
  const id = `rx${role}`;
  const pulse = speaking ? 0.6 + 0.4 * Math.abs(Math.sin(t * 0.7)) : 0.85;
  const ey = look * 14;
  const hy = -headOff * 520;
  const hr = headOff * 35;
  const siren = role === 'guard';
  return (
    <svg width={size} height={size * 1.3} viewBox="-190 -260 380 494" style={{overflow: 'visible'}}>
      <defs>
        <radialGradient id={`h${id}`} cx="0.35" cy="0.28" r="0.85">
          <stop offset="0" stopColor="#ffffff" />
          <stop offset="0.55" stopColor="#e4eaf5" />
          <stop offset="1" stopColor="#9aa7bf" />
        </radialGradient>
        <linearGradient id={`v${id}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#24304f" />
          <stop offset="1" stopColor="#05070f" />
        </linearGradient>
        <radialGradient id={`a${id}`} cx="0.35" cy="0.3" r="0.8">
          <stop offset="0" stopColor="#ffffff" stopOpacity="0.9" />
          <stop offset="0.35" stopColor={c} />
          <stop offset="1" stopColor={c} stopOpacity="0.8" />
        </radialGradient>
        <filter id={`g${id}`} x="-100%" y="-100%" width="300%" height="300%">
          <feGaussianBlur stdDeviation="9" />
        </filter>
      </defs>
      <ellipse cx={0} cy={222} rx={140} ry={18} fill="#000" opacity={0.35} />
      {/* туловище */}
      <rect x={-110} y={40} width={220} height={170} rx={60} fill={`url(#h${id})`} />
      <rect x={-70} y={70} width={140} height={84} rx={22} fill="#1a2238" />
      <circle cx={-34} cy={112} r={12} fill={c} opacity={pulse} />
      <rect x={-8} y={102} width={60} height={8} rx={4} fill={c} opacity={0.7} />
      <rect x={-8} y={118} width={40} height={8} rx={4} fill={c} opacity={0.45} />
      {role === 'hr' && <path d="M-16,40 L16,40 L10,62 L22,140 L0,160 L-22,140 L-10,62 Z" fill="#e0662a" stroke="#a8461a" strokeWidth={3} />}
      {role === 'boss' && (
        <>
          <path d="M-16,40 L16,40 L10,62 L22,150 L0,172 L-22,150 L-10,62 Z" fill="#c9971a" stroke="#8a6508" strokeWidth={3} />
          <text x={0} y={198} textAnchor="middle" fontFamily={FONT} fontWeight={800} fontSize={22} fill="#8a6508">CEO</text>
        </>
      )}
      {/* руки */}
      {[-1, 1].map((sd) => (
        <g key={sd}>
          <path d={`M${sd * 110},80 Q${sd * 160},${120 + Math.sin(t * 0.15 + sd) * 8} ${sd * 150},${170 + Math.sin(t * 0.15 + sd) * 8}`} stroke="#b9c3d6" strokeWidth={30} fill="none" strokeLinecap="round" />
          <circle cx={sd * 150} cy={178 + Math.sin(t * 0.15 + sd) * 8} r={26} fill={`url(#a${id})`} />
        </g>
      ))}
      {/* лицо человека под шлемом */}
      {face && headOff > 0.05 && (
        <g transform={`translate(0,${-20 + (1 - Math.min(1, headOff * 1.6)) * 30})`}>
          <Face type={face} t={t} />
        </g>
      )}
      {/* голова */}
      <g transform={`translate(${headOff * 120},${hy}) rotate(${hr})`} opacity={1 - Math.max(0, headOff - 0.7) / 0.3}>
        {siren ? (
          <g>
            <rect x={-26} y={-182} width={52} height={40} rx={14} fill={Math.floor(t / 5) % 2 ? '#ff3b3b' : '#7a1010'} />
            <circle cx={0} cy={-170} r={60} fill="#ff3b3b" opacity={Math.floor(t / 5) % 2 ? 0.25 : 0} filter={`url(#g${id})`} />
          </g>
        ) : (
          <>
            <path d="M0,-130 L0,-176" stroke="#9aa6bd" strokeWidth={10} strokeLinecap="round" />
            <circle cx={0} cy={-186} r={role === 'boss' ? 26 : 20} fill={`url(#a${id})`} />
          </>
        )}
        <circle cx={-148} cy={-30} r={32} fill={`url(#a${id})`} />
        <circle cx={148} cy={-30} r={32} fill={`url(#a${id})`} />
        <rect x={-145} y={-135} width={290} height={200} rx={96} fill={`url(#h${id})`} />
        <rect x={-110} y={-100} width={220} height={130} rx={62} fill={`url(#v${id})`} />
        <g opacity={pulse}>
          <rect x={-70} y={-66 + ey} width={42} height={54 - look * 14} rx={19} fill={c} filter={`url(#g${id})`} opacity={0.8} />
          <rect x={28} y={-66 + ey} width={42} height={54 - look * 14} rx={19} fill={c} filter={`url(#g${id})`} opacity={0.8} />
          <rect x={-65} y={-62 + ey} width={32} height={46 - look * 14} rx={16} fill={c} />
          <rect x={33} y={-62 + ey} width={32} height={46 - look * 14} rx={16} fill={c} />
        </g>
        {speaking && <rect x={-30} y={4} width={60} height={6 + Math.abs(Math.sin(t * 0.9)) * 10} rx={4} fill={c} opacity={0.9} />}
        <ellipse cx={-66} cy={-108} rx={52} ry={15} fill="#fff" opacity={0.85} transform="rotate(-14,-66,-108)" />
        {role === 'guard' && <path d="M-150,-96 C-120,-170 120,-170 150,-96 L170,-90 L-170,-90 Z" fill="#1f2a44" />}
        {role === 'guard' && <rect x={-40} y={-150} width={80} height={30} rx={6} fill="#f5c542" />}
      </g>
    </svg>
  );
};

// ───────── кофемашина-злодей ─────────
export const Coffee: React.FC<{t: number; speaking?: boolean; size?: number}> = ({t, speaking, size = 380}) => {
  const glow = speaking ? 0.7 + 0.3 * Math.abs(Math.sin(t * 0.6)) : 0.55 + 0.15 * Math.sin(t * 0.1);
  return (
    <svg width={size} height={size * 1.25} viewBox="-190 -240 380 475" style={{overflow: 'visible'}}>
      <defs>
        <linearGradient id="cm" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stopColor="#1a1a20" />
          <stop offset="0.35" stopColor="#4a4c58" />
          <stop offset="0.6" stopColor="#2a2b33" />
          <stop offset="1" stopColor="#101014" />
        </linearGradient>
        <radialGradient id="eye" cx="0.5" cy="0.5" r="0.5">
          <stop offset="0" stopColor="#fff2c0" />
          <stop offset="0.18" stopColor="#ffdd55" />
          <stop offset="0.35" stopColor="#ff3b1f" />
          <stop offset="0.75" stopColor="#7a0a05" />
          <stop offset="1" stopColor="#1a0000" />
        </radialGradient>
        <filter id="eg" x="-100%" y="-100%" width="300%" height="300%">
          <feGaussianBlur stdDeviation="22" />
        </filter>
      </defs>
      <ellipse cx={0} cy={226} rx={170} ry={18} fill="#000" opacity={0.5} />
      <rect x={-150} y={-230} width={300} height={70} rx={20} fill="#2a2b33" />
      <rect x={-160} y={-170} width={320} height={260} rx={30} fill="url(#cm)" />
      <rect x={-160} y={90} width={320} height={130} rx={24} fill="#1c1c22" />
      <rect x={-100} y={150} width={200} height={14} rx={7} fill="#3a3c46" />
      <circle cx={0} cy={-50} r={110} fill="#ff2a10" opacity={glow * 0.6} filter="url(#eg)" />
      <circle cx={0} cy={-50} r={74} fill="#0b0b0e" stroke="#555866" strokeWidth={8} />
      <circle cx={0} cy={-50} r={58} fill="url(#eye)" opacity={glow + 0.2} />
      <ellipse cx={-20} cy={-72} rx={16} ry={8} fill="#fff" opacity={0.5} />
      <rect x={-26} y={90} width={52} height={40} rx={10} fill="#3a3c46" />
      <path d="M-50,150 L50,150 L42,210 Q40,220 30,220 L-30,220 Q-40,220 -42,210 Z" fill="#f2f2f2" />
      <path d="M50,165 q24,4 0,32" stroke="#f2f2f2" strokeWidth={10} fill="none" />
      {[0, 1].map((i) => <path key={i} d={`M${-14 + i * 24},${136 - ((t * 1.5 + i * 20) % 40)} q10,-14 0,-28`} stroke="#ffffff" strokeWidth={5} fill="none" opacity={0.4} />)}
      <text x={0} y={60} textAnchor="middle" fontFamily={MONO} fontWeight={700} fontSize={22} fill="#ff6a50" opacity={0.85}>CAFE-9000</text>
    </svg>
  );
};

export const Mug: React.FC<{t: number}> = ({t}) => (
  <svg width={220} height={240} viewBox="-110 -130 220 240" style={{overflow: 'visible'}}>
    <defs>
      <linearGradient id="mg" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stopColor="#d9dde6" />
        <stop offset="0.4" stopColor="#ffffff" />
        <stop offset="1" stopColor="#aeb4c2" />
      </linearGradient>
    </defs>
    <ellipse cx={0} cy={96} rx={80} ry={10} fill="#000" opacity={0.3} />
    <path d="M60,-20 q50,0 46,40 q-4,40 -46,40" stroke="#c9ced8" strokeWidth={16} fill="none" />
    <rect x={-70} y={-50} width={130} height={140} rx={22} fill="url(#mg)" />
    <ellipse cx={-5} cy={-50} rx={65} ry={14} fill="#5a3418" />
    <text x={-5} y={30} textAnchor="middle" fontFamily={FONT} fontWeight={800} fontSize={24} fill="#3b82f6">#1 BOT</text>
    {[0, 1, 2].map((i) => <path key={i} d={`M${-30 + i * 25},${-70 - ((t * 1.4 + i * 15) % 40)} q12,-16 0,-32`} stroke="#fff" strokeWidth={6} fill="none" opacity={0.45} />)}
  </svg>
);
