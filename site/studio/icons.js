/* Иконки студии M1lash: авторский линейный набор 24×24, штрих 1.7, скругления (Claude, 06.11.2026). */
(() => {
  const P = {
    clock: '<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>',
    hand: '<path d="M8 12V6.5a1.5 1.5 0 0 1 3 0V11m0-5.5V5a1.5 1.5 0 0 1 3 0v6m0-4.5a1.5 1.5 0 0 1 3 0V14a6 6 0 0 1-6 6h-.5a6 6 0 0 1-4.6-2.2L4.6 15a1.6 1.6 0 0 1 2.5-2l.9 1"/>',
    chat: '<path d="M20 12a7.5 7.5 0 0 1-10.9 6.7L4.5 20l1.3-4.1A7.5 7.5 0 1 1 20 12Z"/><path d="M9 11h.01M12 11h.01M15 11h.01"/>',
    box: '<path d="M3.5 7.5 12 3l8.5 4.5v9L12 21l-8.5-4.5z"/><path d="M3.5 7.5 12 12l8.5-4.5M12 12v9"/>',
    alert: '<path d="M12 4 21 19.5H3z"/><path d="M12 10v4.5M12 17.2h.01"/>',
    bulb: '<path d="M9 18h6M10 21h4"/><path d="M12 3a6 6 0 0 0-3.6 10.8c.6.5 1.1 1.3 1.1 2.2h5c0-.9.5-1.7 1.1-2.2A6 6 0 0 0 12 3Z"/>',
    spark: '<path d="M12 3v4M12 17v4M3 12h4M17 12h4M6 6l2.5 2.5M15.5 15.5 18 18M18 6l-2.5 2.5M8.5 15.5 6 18"/>',
    flame: '<path d="M12 21c3.6 0 6-2.4 6-5.6 0-3.8-3.2-5.6-3.7-9.4C11.6 8 10 10.4 10.4 13c-1.3-.6-1.9-1.9-2-3C6.8 11.3 6 13.2 6 15.4 6 18.6 8.4 21 12 21Z"/>',
  };
  window.M1ICON = Object.fromEntries(Object.entries(P).map(([k, v]) => [k, `<svg viewBox="0 0 24 24" width="22" height="22" fill="none" stroke="currentColor" stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${v}</svg>`]));
})();
