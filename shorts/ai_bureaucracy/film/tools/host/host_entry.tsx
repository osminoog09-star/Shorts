// Утверждённый ведущий M1lash (HostCard + Narrator2 из shorts/laeko_host_demo, без изменений)
// как функция времени для композиции huashu-motion: HOST.render(el, {f, pose, prev, k, mouth}).
import React from 'react';
import {createRoot, Root} from 'react-dom/client';
import {flushSync} from 'react-dom';
import {HostCard} from './HostCard';
const roots = new Map<HTMLElement, Root>();
(window as any).HOST = {
  render(el: HTMLElement, p: {f: number; pose: any; prev: any; k: number; mouth: number}) {
    let r = roots.get(el);
    if (!r) { r = createRoot(el); roots.set(el, r); }
    flushSync(() => r!.render(<HostCard f={p.f} pose={p.pose} prev={p.prev} k={p.k} mouth={p.mouth} />));
  },
};
