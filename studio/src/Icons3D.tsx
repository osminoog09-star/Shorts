import React from 'react';

// Глянцевые «3D»-иконки на SVG-градиентах

export const Robot3D: React.FC<{size?: number; accent?: string; id: string; mood?: 'happy' | 'calm'; t?: number}> = ({size = 300, accent = '#3fd6b2', id, mood = 'calm', t = 0}) => {
  const blink = Math.floor(t) % 80 < 3;
  return (
    <svg width={size} height={size * 1.15} viewBox="-170 -215 340 390" style={{overflow: 'visible'}}>
      <defs>
        <radialGradient id={`h${id}`} cx="0.35" cy="0.28" r="0.85">
          <stop offset="0" stopColor="#ffffff" />
          <stop offset="0.55" stopColor="#e4eaf5" />
          <stop offset="1" stopColor="#a3afc6" />
        </radialGradient>
        <linearGradient id={`v${id}`} x1="0" y1="0" x2="0" y2="1">
          <stop offset="0" stopColor="#24304f" />
          <stop offset="1" stopColor="#05070f" />
        </linearGradient>
        <radialGradient id={`a${id}`} cx="0.35" cy="0.3" r="0.8">
          <stop offset="0" stopColor="#ffffff" stopOpacity="0.9" />
          <stop offset="0.35" stopColor={accent} />
          <stop offset="1" stopColor={accent} stopOpacity="0.75" />
        </radialGradient>
        <filter id={`g${id}`} x="-100%" y="-100%" width="300%" height="300%">
          <feGaussianBlur stdDeviation="8" />
        </filter>
      </defs>
      <ellipse cx={0} cy={160} rx={110} ry={16} fill="#000" opacity={0.35} />
      <path d="M0,-120 L0,-168" stroke="#9aa6bd" strokeWidth={10} strokeLinecap="round" />
      <circle cx={0} cy={-178} r={20} fill={`url(#a${id})`} />
      <rect x={-82} y={40} width={164} height={108} rx={48} fill={`url(#h${id})`} />
      <circle cx={0} cy={92} r={16} fill={`url(#a${id})`} />
      <circle cx={-142} cy={-28} r={30} fill={`url(#a${id})`} />
      <circle cx={142} cy={-28} r={30} fill={`url(#a${id})`} />
      <rect x={-135} y={-125} width={270} height={192} rx={92} fill={`url(#h${id})`} />
      <rect x={-102} y={-92} width={204} height={124} rx={60} fill={`url(#v${id})`} />
      {mood === 'happy' || blink ? (
        <g stroke={accent} strokeWidth={14} fill="none" strokeLinecap="round">
          <path d={blink && mood !== 'happy' ? 'M-60,-30 L-24,-30' : 'M-62,-24 Q-42,-54 -22,-24'} />
          <path d={blink && mood !== 'happy' ? 'M24,-30 L60,-30' : 'M22,-24 Q42,-54 62,-24'} />
        </g>
      ) : (
        <g>
          <rect x={-62} y={-60} width={38} height={52} rx={18} fill={accent} filter={`url(#g${id})`} opacity={0.8} />
          <rect x={24} y={-60} width={38} height={52} rx={18} fill={accent} filter={`url(#g${id})`} opacity={0.8} />
          <rect x={-58} y={-56} width={30} height={44} rx={15} fill={accent} />
          <rect x={28} y={-56} width={30} height={44} rx={15} fill={accent} />
        </g>
      )}
      <ellipse cx={-62} cy={-102} rx={48} ry={14} fill="#fff" opacity={0.85} transform="rotate(-14,-62,-102)" />
      <ellipse cx={-40} cy={-74} rx={30} ry={8} fill="#fff" opacity={0.25} transform="rotate(-14,-40,-74)" />
    </svg>
  );
};

export const Folder3D: React.FC<{size?: number; label?: string}> = ({size = 260, label}) => (
  <svg width={size} height={size * 0.82} viewBox="-150 -125 300 245" style={{overflow: 'visible'}}>
    <defs>
      <linearGradient id="fb" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stopColor="#ffb932" />
        <stop offset="1" stopColor="#e2861a" />
      </linearGradient>
      <linearGradient id="ff" x1="0" y1="0" x2="0" y2="1">
        <stop offset="0" stopColor="#ffe48a" />
        <stop offset="1" stopColor="#ffbf3a" />
      </linearGradient>
    </defs>
    <ellipse cx={0} cy={112} rx={120} ry={12} fill="#000" opacity={0.25} />
    <path d="M-130,-90 Q-130,-110 -110,-110 L-40,-110 Q-28,-110 -20,-98 L-8,-84 L110,-84 Q130,-84 130,-64 L130,90 Q130,104 116,104 L-116,104 Q-130,104 -130,90 Z" fill="url(#fb)" />
    <rect x={-112} y={-70} width={224} height={60} rx={10} fill="#fff" opacity={0.9} />
    <path d="M-140,-40 Q-142,-56 -124,-56 L124,-56 Q142,-56 140,-40 L128,92 Q126,104 112,104 L-112,104 Q-126,104 -128,92 Z" fill="url(#ff)" />
    <path d="M-124,-48 L124,-48" stroke="#fff" strokeWidth={6} opacity={0.7} strokeLinecap="round" />
    {label && (
      <text x={0} y={46} textAnchor="middle" fontFamily="'DejaVu Sans Mono', monospace" fontWeight={700} fontSize={40} fill="#8a5a08">{label}</text>
    )}
  </svg>
);

export const Trash3D: React.FC<{size?: number; lid?: number}> = ({size = 300, lid = 0}) => (
  <svg width={size} height={size * 1.15} viewBox="-150 -200 300 345" style={{overflow: 'visible'}}>
    <defs>
      <linearGradient id="tb" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stopColor="#6f7a8e" />
        <stop offset="0.35" stopColor="#eef2f8" />
        <stop offset="0.6" stopColor="#c3cad6" />
        <stop offset="1" stopColor="#5f6a7e" />
      </linearGradient>
      <linearGradient id="tl" x1="0" y1="0" x2="1" y2="0">
        <stop offset="0" stopColor="#7e889b" />
        <stop offset="0.4" stopColor="#ffffff" />
        <stop offset="1" stopColor="#6a758a" />
      </linearGradient>
    </defs>
    <ellipse cx={0} cy={132} rx={110} ry={14} fill="#000" opacity={0.25} />
    <path d="M-110,-90 L110,-90 L88,120 Q86,132 70,132 L-70,132 Q-86,132 -88,120 Z" fill="url(#tb)" />
    {[-52, 0, 52].map((x) => (
      <path key={x} d={`M${x},-60 L${x * 0.82},106`} stroke="#58627a" strokeWidth={10} strokeLinecap="round" opacity={0.55} />
    ))}
    <g transform={`rotate(${-lid}, -120, -100)`}>
      <rect x={-128} y={-118} width={256} height={32} rx={14} fill="url(#tl)" />
      <rect x={-36} y={-146} width={72} height={34} rx={14} fill="none" stroke="#8a93a6" strokeWidth={12} />
    </g>
  </svg>
);

export const AppIcon: React.FC<{size?: number; from: string; to: string; children?: React.ReactNode}> = ({size = 84, from, to, children}) => (
  <div
    style={{
      width: size, height: size, borderRadius: size * 0.28, background: `linear-gradient(145deg, ${from}, ${to})`, display: 'flex', alignItems: 'center',
      justifyContent: 'center', boxShadow: `inset 0 3px 0 rgba(255,255,255,.45), 0 8px 24px ${to}66`, flexShrink: 0,
    }}
  >
    {children}
  </div>
);

export const Alarm3D: React.FC<{size?: number; t: number}> = ({size = 220, t}) => (
  <svg width={size} height={size} viewBox="-120 -130 240 250" style={{overflow: 'visible'}}>
    <defs>
      <radialGradient id="al" cx="0.35" cy="0.3" r="0.8">
        <stop offset="0" stopColor="#ffd2d2" />
        <stop offset="0.4" stopColor="#ff3b3b" />
        <stop offset="1" stopColor="#a10d1d" />
      </radialGradient>
    </defs>
    {[0, 1].map((i) => (
      <circle key={i} cx={0} cy={-10} r={90 + ((t * 4 + i * 30) % 60)} fill="none" stroke="#ff3b3b" strokeWidth={6} opacity={1 - ((t * 4 + i * 30) % 60) / 60} />
    ))}
    <path d="M-70,60 L-70,-10 A70,70 0 0 1 70,-10 L70,60 Z" fill="url(#al)" />
    <rect x={-95} y={56} width={190} height={44} rx={16} fill="#3a3f4b" />
    <ellipse cx={-28} cy={-28} rx={20} ry={36} fill="#fff" opacity={0.55} transform="rotate(20,-28,-28)" />
  </svg>
);
