import React from 'react';
import {Narrator2, NPose} from './Narrator2';
const HostCard: React.FC<{f: number; pose: NPose; prev: NPose; k: number; mouth: number}> = ({f, pose, prev, k, mouth}) => {
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


export {HostCard};
