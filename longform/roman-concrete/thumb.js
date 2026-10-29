// Обложка: Пантеон крупно + контраст «2000 лет vs 50»
import { render, clear2d, ctx, CSS } from './engine.js';
import { v3, orbit } from './lib.js';
import { PAN } from './scenes_a.js';
function rr(x, y, w, h, r) { ctx.beginPath(); ctx.roundRect(x, y, w, h, r); }
export function thumb() {
  const S = PAN; orbit(S.cam, v3(2.5, 5.2, 0), 19, -0.75, 0.16);
  render(S.scene, S.cam, { time: 1, focus: 19, aperture: 0.0004, vig: 0.35 });
  clear2d();
  ctx.save();
  const g = ctx.createLinearGradient(0, 0, 1100, 0); g.addColorStop(0, 'rgba(25,22,40,0.82)'); g.addColorStop(1, 'rgba(25,22,40,0)');
  ctx.fillStyle = g; ctx.fillRect(0, 0, 1200, 1080);
  ctx.font = '900 150px "Rubik"'; ctx.fillStyle = '#ffffff'; ctx.fillText('2000 ЛЕТ', 80, 300);
  ctx.font = '900 92px "Rubik"'; ctx.fillStyle = '#ffdc7a'; ctx.fillText('И СТОИТ', 86, 410);
  ctx.save(); ctx.translate(90, 520); ctx.rotate(-0.04);
  rr(0, 0, 700, 170, 30); ctx.fillStyle = '#e8706a'; ctx.fill();
  ctx.font = '900 96px "Rubik"'; ctx.fillStyle = '#fff'; ctx.fillText('А НАШ — 50', 40, 122); ctx.restore();
  ctx.font = '700 54px "Rubik"'; ctx.fillStyle = 'rgba(255,255,255,0.92)'; ctx.fillText('секрет римского бетона', 86, 820);
  ctx.restore();
}
