var __create = Object.create;
var __defProp = Object.defineProperty;
var __getOwnPropDesc = Object.getOwnPropertyDescriptor;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __getProtoOf = Object.getPrototypeOf;
var __hasOwnProp = Object.prototype.hasOwnProperty;
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};
var __copyProps = (to, from, except, desc) => {
  if (from && typeof from === "object" || typeof from === "function") {
    for (let key of __getOwnPropNames(from))
      if (!__hasOwnProp.call(to, key) && key !== except)
        __defProp(to, key, { get: () => from[key], enumerable: !(desc = __getOwnPropDesc(from, key)) || desc.enumerable });
  }
  return to;
};
var __toESM = (mod, isNodeMode, target) => (target = mod != null ? __create(__getProtoOf(mod)) : {}, __copyProps(
  // If the importer is in node compatibility mode or this is not an ESM
  // file that has been converted to a CommonJS file using a Babel-
  // compatible transform (i.e. "__esModule" has not been set), then set
  // "default" to the CommonJS "module.exports" for node compatibility.
  isNodeMode || !mod || !mod.__esModule ? __defProp(target, "default", { value: mod, enumerable: true }) : target,
  mod
));
var __toCommonJS = (mod) => __copyProps(__defProp({}, "__esModule", { value: true }), mod);

// shorts/laeko_host_demo/Narrator2.tsx
var Narrator2_exports = {};
__export(Narrator2_exports, {
  Narrator2: () => Narrator2
});
module.exports = __toCommonJS(Narrator2_exports);
var import_react = __toESM(require("react"));
var SKIN = "#f3c9a9";
var SKIN_HI = "#fde3cf";
var SKIN_SH = "#d99f80";
var SKIN_DK = "#b97b5f";
var HAIR = "#1a1720";
var TEE = "#17171c";
var RIM_L = "#4fd1ff";
var RIM_R = "#ff5ad1";
var POSES = {
  rest: { L: [-300, 170], R: [300, 170], hl: "fist", hr: "fist" },
  type: { L: [-210, -60], R: [210, -60], hl: "fist", hr: "fist" },
  talk: { L: [-300, 170], R: [268, -250], hl: "fist", hr: "open" },
  deadpan: { L: [-300, 170], R: [300, 170], hl: "fist", hr: "fist" },
  point: { L: [-300, 170], R: [225, -905], hl: "fist", hr: "point" },
  facepalm: { L: [-300, 170], R: [34, -722], hl: "fist", hr: "open" },
  shock: { L: [-168, -812], R: [168, -812], hl: "open", hr: "open" },
  shrug: { L: [-292, -175], R: [292, -175], hl: "palm", hr: "palm" },
  laugh: { L: [-70, -220], R: [268, -250], hl: "open", hr: "open" }
};
var backOut = (x) => {
  const c1 = 1.5;
  const c3 = c1 + 1;
  return 1 + c3 * Math.pow(x - 1, 3) + c1 * Math.pow(x - 1, 2);
};
var Hand = ({ type, side }) => {
  const fingers = [
    { x: -21, l: type === "open" || type === "palm" ? 46 : 18 },
    { x: -7, l: type === "point" ? 74 : type === "open" || type === "palm" ? 54 : 20 },
    { x: 7, l: type === "open" || type === "palm" ? 52 : 20 },
    { x: 20, l: type === "open" || type === "palm" ? 42 : 17 }
  ];
  return /* @__PURE__ */ import_react.default.createElement("g", null, fingers.map((fg, i) => /* @__PURE__ */ import_react.default.createElement("g", { key: i }, /* @__PURE__ */ import_react.default.createElement("rect", { x: fg.x - 8, y: 40, width: 16, height: fg.l + 8, rx: 8, fill: SKIN, stroke: SKIN_DK, strokeWidth: 2.5 }), /* @__PURE__ */ import_react.default.createElement("rect", { x: fg.x - 4, y: 44 + fg.l - 6, width: 8, height: 7, rx: 3.5, fill: SKIN_HI, opacity: 0.7 }))), /* @__PURE__ */ import_react.default.createElement("rect", { x: -31, y: 2, width: 62, height: 54, rx: 24, fill: SKIN, stroke: SKIN_DK, strokeWidth: 2.5 }), /* @__PURE__ */ import_react.default.createElement("path", { d: "M-22,14 Q0,6 22,14", stroke: SKIN_HI, strokeWidth: 6, fill: "none", opacity: 0.6, strokeLinecap: "round" }), /* @__PURE__ */ import_react.default.createElement("g", { transform: `translate(${-side * 26},18) rotate(${side * (type === "fist" ? 70 : 42)})` }, /* @__PURE__ */ import_react.default.createElement("rect", { x: -8, y: 0, width: 17, height: type === "fist" ? 32 : 44, rx: 8.5, fill: SKIN, stroke: SKIN_DK, strokeWidth: 2.5 })));
};
var Arm = ({ sh, hand, side, ht, t }) => {
  const dx = hand[0] - sh[0];
  const dy = hand[1] - sh[1];
  const len = Math.hypot(dx, dy) || 1;
  const bend = Math.max(0, 380 - len) * 0.55 + 28;
  let px = -dy / len;
  let py = dx / len;
  if (px * side < 0) {
    px = -px;
    py = -py;
  }
  const el = [(sh[0] + hand[0]) / 2 + px * bend, (sh[1] + hand[1]) / 2 + py * bend];
  const fx = hand[0] - el[0];
  const fy = hand[1] - el[1];
  const fl = Math.hypot(fx, fy) || 1;
  const nx = -fy / fl;
  const ny = fx / fl;
  const fore = `M${el[0] + nx * 30},${el[1] + ny * 30} L${hand[0] + nx * 23},${hand[1] + ny * 23} L${hand[0] - nx * 23},${hand[1] - ny * 23} L${el[0] - nx * 30},${el[1] - ny * 30} Z`;
  const ang = Math.atan2(fy, fx) * 180 / Math.PI - 90;
  const sleeveEnd = [sh[0] + (el[0] - sh[0]) * 0.78, sh[1] + (el[1] - sh[1]) * 0.78];
  const upLen = Math.hypot(el[0] - sh[0], el[1] - sh[1]) || 1;
  const ux = -(el[1] - sh[1]) / upLen;
  const uy = (el[0] - sh[0]) / upLen;
  return /* @__PURE__ */ import_react.default.createElement("g", null, /* @__PURE__ */ import_react.default.createElement("path", { d: `M${sleeveEnd[0]},${sleeveEnd[1]} L${el[0]},${el[1]}`, stroke: SKIN, strokeWidth: 60, strokeLinecap: "round" }), /* @__PURE__ */ import_react.default.createElement("path", { d: fore, fill: SKIN, stroke: SKIN, strokeWidth: 10, strokeLinejoin: "round" }), /* @__PURE__ */ import_react.default.createElement("path", { d: `M${el[0] - nx * 22},${el[1] - ny * 22} L${hand[0] - nx * 16},${hand[1] - ny * 16}`, stroke: SKIN_SH, strokeWidth: 14, strokeLinecap: "round", opacity: 0.55 }), /* @__PURE__ */ import_react.default.createElement("path", { d: `M${el[0] + nx * 18},${el[1] + ny * 18} L${hand[0] + nx * 12},${hand[1] + ny * 12}`, stroke: SKIN_HI, strokeWidth: 6, strokeLinecap: "round", opacity: 0.5 }), /* @__PURE__ */ import_react.default.createElement("path", { d: `M${sh[0]},${sh[1]} L${sleeveEnd[0]},${sleeveEnd[1]}`, stroke: TEE, strokeWidth: 92, strokeLinecap: "round" }), /* @__PURE__ */ import_react.default.createElement("path", { d: `M${sh[0] + ux * side * 22},${sh[1] + uy * side * 22} L${sleeveEnd[0] + ux * side * 22},${sleeveEnd[1] + uy * side * 22}`, stroke: "#2b2b34", strokeWidth: 16, strokeLinecap: "round", opacity: 0.8 }), /* @__PURE__ */ import_react.default.createElement("path", { d: `M${sh[0] - ux * side * 40},${sh[1] - uy * side * 40} L${sleeveEnd[0] - ux * side * 40},${sleeveEnd[1] - uy * side * 40}`, stroke: side < 0 ? RIM_L : RIM_R, strokeWidth: 5, strokeLinecap: "round", opacity: 0.55 }), /* @__PURE__ */ import_react.default.createElement("g", { transform: `translate(${hand[0]},${hand[1]}) rotate(${ang + Math.sin(t * 0.2) * 2})` }, /* @__PURE__ */ import_react.default.createElement(Hand, { type: ht, side })));
};
var Narrator2 = ({ t, x, y, s = 1, pose, prev = pose, k = 1, mouth = 0, look = "cam", box }) => {
  const e = k < 1 ? backOut(Math.max(0, k)) : 1;
  const P = POSES[pose];
  const P0 = POSES[prev];
  const lerp = (a, b) => a + (b - a) * e;
  const gest = pose === "talk" ? mouth * 38 + Math.sin(t * 0.17) * 14 : pose === "laugh" ? Math.sin(t * 0.9) * 10 : 0;
  const L = [lerp(P0.L[0], P.L[0]), lerp(P0.L[1], P.L[1])];
  const R = [lerp(P0.R[0], P.R[0]) + gest * 0.5, lerp(P0.R[1], P.R[1]) - gest];
  const hl = k < 0.5 ? P0.hl : P.hl;
  const hr = k < 0.5 ? P0.hr : P.hr;
  const shrugUp = pose === "shrug" ? -26 * Math.min(1, e) : 0;
  const breathe = Math.sin(t * 0.075) * 5;
  const shake = pose === "laugh" ? Math.sin(t * 1.3) * 5 : pose === "shock" ? Math.sin(t * 2.3) * 2.5 : 0;
  const nod = mouth * 4 * Math.sin(t * 0.55);
  const tiltBase = pose === "shrug" ? -7 : pose === "deadpan" ? 3 : pose === "facepalm" ? 6 : pose === "laugh" ? -5 : 0;
  const tilt = tiltBase + Math.sin(t * 0.045) * 2 + nod;
  const headY = -mouth * 5 + (pose === "shock" ? -10 : 0);
  const shL = [-238, -420 + shrugUp];
  const shR = [238, -420 + shrugUp];
  const bp = t % 103;
  const blinkLid = bp < 2 ? bp / 2 : bp < 4 ? 1 - (bp - 2) / 2 : 0;
  const sac = Math.floor(t / 37);
  const sx = look === "down" ? 0 : (sac * 7919 % 7 - 3) * 1.6;
  const sy = look === "down" ? 12 : (sac * 104729 % 5 - 2) * 1.2;
  const baseLid = pose === "deadpan" ? 0.45 : pose === "facepalm" ? 0.3 : 0;
  const lid = Math.min(1, baseLid + blinkLid * (1 - baseLid));
  const laughEyes = pose === "laugh";
  const big = pose === "shock" ? 1.14 : 1;
  const browUp = pose === "shock" ? -28 : pose === "shrug" ? -16 : pose === "point" ? -8 : pose === "deadpan" ? 6 : 0;
  const browIn = pose === "facepalm" || pose === "shrug" ? 10 : pose === "deadpan" ? -6 : 0;
  const browTalk = pose === "talk" ? -mouth * 7 : 0;
  const m = Math.max(mouth, pose === "shock" ? 0.75 : 0);
  const mw = 26 + m * 6 + Math.sin(t * 0.9) * m * 5;
  const mh = 3 + m * 26;
  const Eye = (cx, side) => {
    const ey = -712;
    const wdt = 34 * big;
    const top = ey - 20 * big;
    const bot = ey + 15 * big;
    const id = `ec${side}`;
    if (laughEyes) {
      return /* @__PURE__ */ import_react.default.createElement("g", null, /* @__PURE__ */ import_react.default.createElement("path", { d: `M${cx - 30},${ey + 4} Q${cx},${ey - 22} ${cx + 30},${ey + 4}`, stroke: HAIR, strokeWidth: 8, fill: "none", strokeLinecap: "round" }), /* @__PURE__ */ import_react.default.createElement("path", { d: `M${cx + side * 30},${ey + 4} l${side * 10},-6`, stroke: HAIR, strokeWidth: 5, strokeLinecap: "round" }));
    }
    const sclera = `M${cx - wdt},${ey} C${cx - wdt * 0.6},${top - 4} ${cx + wdt * 0.6},${top - 4} ${cx + wdt},${ey - 3} C${cx + wdt * 0.6},${bot + 2} ${cx - wdt * 0.6},${bot + 2} ${cx - wdt},${ey} Z`;
    const lidY = top - 4 + (bot + 4 - (top - 4)) * lid;
    return /* @__PURE__ */ import_react.default.createElement("g", null, /* @__PURE__ */ import_react.default.createElement("defs", null, /* @__PURE__ */ import_react.default.createElement("clipPath", { id }, /* @__PURE__ */ import_react.default.createElement("path", { d: sclera })), /* @__PURE__ */ import_react.default.createElement("radialGradient", { id: `ir${side}`, cx: "0.5", cy: "0.6", r: "0.6" }, /* @__PURE__ */ import_react.default.createElement("stop", { offset: "0", stopColor: "#c98a4a" }), /* @__PURE__ */ import_react.default.createElement("stop", { offset: "0.55", stopColor: "#7a4a26" }), /* @__PURE__ */ import_react.default.createElement("stop", { offset: "1", stopColor: "#3a2214" }))), /* @__PURE__ */ import_react.default.createElement("path", { d: sclera, fill: "#fbf7f4" }), /* @__PURE__ */ import_react.default.createElement("g", { clipPath: `url(#${id})` }, /* @__PURE__ */ import_react.default.createElement("rect", { x: cx - 40, y: top - 10, width: 80, height: 12, fill: "#d9c4bb", opacity: 0.7 }), /* @__PURE__ */ import_react.default.createElement("circle", { cx: cx + sx + side * 1.5, cy: ey + sy - 1, r: pose === "shock" ? 14 : 18, fill: `url(#ir${side})` }), /* @__PURE__ */ import_react.default.createElement("circle", { cx: cx + sx + side * 1.5, cy: ey + sy - 1, r: pose === "shock" ? 14 : 18, fill: "none", stroke: "#2a160c", strokeWidth: 2.5 }), /* @__PURE__ */ import_react.default.createElement("circle", { cx: cx + sx + side * 1.5, cy: ey + sy - 1, r: pose === "shock" ? 5 : 8.5, fill: "#0d0907" }), /* @__PURE__ */ import_react.default.createElement("circle", { cx: cx + sx + side * 1.5 + 6, cy: ey + sy - 8, r: 5, fill: "#fff" }), /* @__PURE__ */ import_react.default.createElement("circle", { cx: cx + sx + side * 1.5 - 5, cy: ey + sy + 6, r: 2.2, fill: "#fff", opacity: 0.8 }), lid > 0.01 && /* @__PURE__ */ import_react.default.createElement("path", { d: `M${cx - 45},${top - 12} L${cx + 45},${top - 12} L${cx + 45},${lidY} Q${cx},${lidY + 6} ${cx - 45},${lidY} Z`, fill: SKIN })), /* @__PURE__ */ import_react.default.createElement(
      "path",
      {
        d: `M${cx - wdt - 2},${ey + 1 + (lidY - top + 4) * 0.5} C${cx - wdt * 0.6},${lidY - 3} ${cx + wdt * 0.6},${lidY - 3} ${cx + wdt + 2},${ey - 3 + (lidY - top + 4) * 0.5}`,
        stroke: HAIR,
        strokeWidth: 7,
        fill: "none",
        strokeLinecap: "round"
      }
    ), /* @__PURE__ */ import_react.default.createElement("path", { d: `M${cx + side * (wdt + 1)},${ey - 3 + (lidY - top + 4) * 0.5} l${side * 9},-7`, stroke: HAIR, strokeWidth: 4.5, strokeLinecap: "round" }), /* @__PURE__ */ import_react.default.createElement("path", { d: `M${cx - wdt * 0.7},${bot + 1} Q${cx},${bot + 5} ${cx + wdt * 0.7},${bot + 1}`, stroke: SKIN_DK, strokeWidth: 2.5, fill: "none", opacity: 0.7 }), /* @__PURE__ */ import_react.default.createElement("path", { d: `M${cx - wdt * 0.8},${top - 10 + browUp * 0.3} Q${cx},${top - 18 + browUp * 0.3} ${cx + wdt * 0.8},${top - 10 + browUp * 0.3}`, stroke: SKIN_DK, strokeWidth: 2.5, fill: "none", opacity: 0.45 }));
  };
  const Brow = (side) => {
    const by = -770 + browUp + browTalk;
    const inner = by - browIn;
    const outer = by + 4;
    const xi = side * 18;
    const xo = side * 82;
    return /* @__PURE__ */ import_react.default.createElement(
      "path",
      {
        d: `M${xi},${inner + 6} Q${(xi + xo) / 2},${Math.min(inner, outer) - 12} ${xo},${outer} Q${(xi + xo) / 2},${Math.min(inner, outer) - 2} ${xi},${inner + 14} Z`,
        fill: HAIR
      }
    );
  };
  const Mouth = () => {
    const my = -608;
    if (pose === "laugh") {
      return /* @__PURE__ */ import_react.default.createElement("g", null, /* @__PURE__ */ import_react.default.createElement("path", { d: `M-38,${my - 8} Q0,${my - 2} 38,${my - 8} Q32,${my + 44} 0,${my + 48} Q-32,${my + 44} -38,${my - 8} Z`, fill: "#5a1d22" }), /* @__PURE__ */ import_react.default.createElement("path", { d: `M-30,${my - 5} Q0,${my} 30,${my - 5} L28,${my + 6} Q0,${my + 10} -28,${my + 6} Z`, fill: "#fff" }), /* @__PURE__ */ import_react.default.createElement("ellipse", { cx: 0, cy: my + 34, rx: 18, ry: 9, fill: "#d0646a" }));
    }
    if (m < 0.08) {
      if (pose === "deadpan" || pose === "facepalm") return /* @__PURE__ */ import_react.default.createElement("path", { d: `M-24,${my} Q0,${my + 3} 24,${my - 2}`, stroke: "#9a4e43", strokeWidth: 6, fill: "none", strokeLinecap: "round" });
      if (pose === "point" || pose === "shrug") return /* @__PURE__ */ import_react.default.createElement("path", { d: `M-26,${my - 2} Q2,${my + 10} 26,${my - 8}`, stroke: "#9a4e43", strokeWidth: 6, fill: "none", strokeLinecap: "round" });
      return /* @__PURE__ */ import_react.default.createElement("g", null, /* @__PURE__ */ import_react.default.createElement("path", { d: `M-24,${my} Q0,${my + 8} 24,${my}`, stroke: "#9a4e43", strokeWidth: 6, fill: "none", strokeLinecap: "round" }), /* @__PURE__ */ import_react.default.createElement("path", { d: `M-12,${my + 14} Q0,${my + 18} 12,${my + 14}`, stroke: SKIN_HI, strokeWidth: 4, fill: "none", strokeLinecap: "round", opacity: 0.7 }));
    }
    return /* @__PURE__ */ import_react.default.createElement("g", null, /* @__PURE__ */ import_react.default.createElement("path", { d: `M${-mw},${my} Q0,${my - 6} ${mw},${my} Q${mw * 0.8},${my + mh * 1.2} 0,${my + mh * 1.25} Q${-mw * 0.8},${my + mh * 1.2} ${-mw},${my} Z`, fill: "#5a1d22" }), mh > 9 && /* @__PURE__ */ import_react.default.createElement("path", { d: `M${-mw * 0.78},${my + 1} Q0,${my - 2} ${mw * 0.78},${my + 1} L${mw * 0.7},${my + 7} Q0,${my + 9} ${-mw * 0.7},${my + 7} Z`, fill: "#fff" }), mh > 14 && /* @__PURE__ */ import_react.default.createElement("ellipse", { cx: 0, cy: my + mh * 0.95, rx: mw * 0.5, ry: mh * 0.28, fill: "#d0646a" }), /* @__PURE__ */ import_react.default.createElement("path", { d: `M${-mw * 0.6},${my + mh * 1.25 + 6} Q0,${my + mh * 1.25 + 11} ${mw * 0.6},${my + mh * 1.25 + 6}`, stroke: SKIN_HI, strokeWidth: 4, fill: "none", strokeLinecap: "round", opacity: 0.7 }));
  };
  const fringe = [
    [-110, -850, -128, -748, 46],
    [-80, -880, -96, -770, 52],
    [-40, -900, -52, -790, 58],
    [2, -905, -6, -800, 58],
    [44, -900, 48, -792, 56],
    [82, -880, 98, -772, 52],
    [112, -850, 128, -752, 44]
  ];
  const sway = (i) => Math.sin(t * 0.06 + i * 0.9) * 1.8 - tilt * 0.25;
  const headAbove = pose === "facepalm" || pose === "shock";
  return /* @__PURE__ */ import_react.default.createElement("g", { transform: `translate(${x + shake},${y + breathe * 0.4}) scale(${s})` }, /* @__PURE__ */ import_react.default.createElement("defs", null, /* @__PURE__ */ import_react.default.createElement("linearGradient", { id: "n2tee", x1: "0", y1: "0", x2: "1", y2: "1" }, /* @__PURE__ */ import_react.default.createElement("stop", { offset: "0", stopColor: "#2a2a33" }), /* @__PURE__ */ import_react.default.createElement("stop", { offset: "0.5", stopColor: TEE }), /* @__PURE__ */ import_react.default.createElement("stop", { offset: "1", stopColor: "#09090c" })), /* @__PURE__ */ import_react.default.createElement("radialGradient", { id: "n2face", cx: "0.38", cy: "0.36", r: "0.75" }, /* @__PURE__ */ import_react.default.createElement("stop", { offset: "0", stopColor: SKIN_HI }), /* @__PURE__ */ import_react.default.createElement("stop", { offset: "0.55", stopColor: SKIN }), /* @__PURE__ */ import_react.default.createElement("stop", { offset: "1", stopColor: SKIN_SH })), /* @__PURE__ */ import_react.default.createElement("linearGradient", { id: "n2neck", x1: "0", y1: "0", x2: "0", y2: "1" }, /* @__PURE__ */ import_react.default.createElement("stop", { offset: "0", stopColor: SKIN_DK }), /* @__PURE__ */ import_react.default.createElement("stop", { offset: "0.45", stopColor: SKIN_SH }), /* @__PURE__ */ import_react.default.createElement("stop", { offset: "1", stopColor: SKIN })), /* @__PURE__ */ import_react.default.createElement("linearGradient", { id: "n2hair", x1: "0", y1: "0", x2: "0", y2: "1" }, /* @__PURE__ */ import_react.default.createElement("stop", { offset: "0", stopColor: "#2c2638" }), /* @__PURE__ */ import_react.default.createElement("stop", { offset: "1", stopColor: "#100e14" })), /* @__PURE__ */ import_react.default.createElement("clipPath", { id: "n2faceClip" }, /* @__PURE__ */ import_react.default.createElement("path", { d: "M-118,-745 C-121,-850 -64,-895 0,-895 C64,-895 121,-850 118,-745 C116,-680 98,-628 62,-596 C40,-577 18,-568 0,-567 C-18,-568 -40,-577 -62,-596 C-98,-628 -116,-680 -118,-745 Z" })), /* @__PURE__ */ import_react.default.createElement("filter", { id: "n2blur", x: "-20%", y: "-20%", width: "140%", height: "140%" }, /* @__PURE__ */ import_react.default.createElement("feGaussianBlur", { stdDeviation: "6" }))), /* @__PURE__ */ import_react.default.createElement("g", { transform: `translate(0,${headY}) rotate(${tilt}, 0, -600)` }, /* @__PURE__ */ import_react.default.createElement("path", { d: "M-138,-720 C-158,-880 -80,-948 6,-944 C98,-940 160,-874 138,-720 C136,-680 128,-650 118,-640 L-118,-640 C-128,-650 -136,-680 -138,-720 Z", fill: "url(#n2hair)" })), /* @__PURE__ */ import_react.default.createElement(
    "path",
    {
      d: `M-310,60 L-298,-300 C-286,${-404 + shrugUp} -238,${-446 + shrugUp} -152,${-468 + shrugUp} L-62,${-484 + shrugUp} L62,${-484 + shrugUp} L152,${-468 + shrugUp} C238,${-446 + shrugUp} 286,${-404 + shrugUp} 298,-300 L310,60 Z`,
      fill: "url(#n2tee)"
    }
  ), /* @__PURE__ */ import_react.default.createElement("path", { d: "M-200,-330 C-150,-300 -120,-240 -110,-160", stroke: "#26262f", strokeWidth: 8, fill: "none", strokeLinecap: "round", opacity: 0.8 }), /* @__PURE__ */ import_react.default.createElement("path", { d: "M200,-330 C150,-300 130,-250 124,-170", stroke: "#0a0a0d", strokeWidth: 10, fill: "none", strokeLinecap: "round", opacity: 0.7 }), /* @__PURE__ */ import_react.default.createElement("path", { d: "M-60,-120 C-20,-100 30,-104 70,-130", stroke: "#26262f", strokeWidth: 6, fill: "none", strokeLinecap: "round", opacity: 0.6 }), /* @__PURE__ */ import_react.default.createElement("path", { d: `M-300,-60 L-294,-300 C-284,${-400 + shrugUp} -240,${-440 + shrugUp} -160,${-464 + shrugUp}`, stroke: RIM_L, strokeWidth: 6, fill: "none", opacity: 0.6, strokeLinecap: "round" }), /* @__PURE__ */ import_react.default.createElement("path", { d: `M300,-60 L294,-300 C284,${-400 + shrugUp} 240,${-440 + shrugUp} 160,${-464 + shrugUp}`, stroke: RIM_R, strokeWidth: 6, fill: "none", opacity: 0.5, strokeLinecap: "round" }), /* @__PURE__ */ import_react.default.createElement("g", { transform: "translate(-120,-300)" }, /* @__PURE__ */ import_react.default.createElement("text", { x: 0, y: 0, textAnchor: "middle", fontFamily: "'DejaVu Sans Mono', monospace", fontWeight: 700, fontSize: 40, fill: RIM_L, opacity: 0.35, filter: "url(#n2blur)" }, "</>"), /* @__PURE__ */ import_react.default.createElement("text", { x: 0, y: 0, textAnchor: "middle", fontFamily: "'DejaVu Sans Mono', monospace", fontWeight: 700, fontSize: 40, fill: "#9fe8ff", opacity: 0.85 }, "</>")), /* @__PURE__ */ import_react.default.createElement("g", { transform: `translate(0,${headY * 0.4})` }, /* @__PURE__ */ import_react.default.createElement("path", { d: "M-52,-612 L-50,-470 C-22,-450 22,-450 50,-470 L52,-612 Z", fill: "url(#n2neck)" }), /* @__PURE__ */ import_react.default.createElement("path", { d: "M-30,-500 Q0,-490 30,-500", stroke: SKIN_DK, strokeWidth: 4, fill: "none", opacity: 0.4 })), /* @__PURE__ */ import_react.default.createElement("path", { d: `M-70,${-480 + shrugUp} C-44,-436 44,-436 70,${-480 + shrugUp}`, stroke: "#2e2e38", strokeWidth: 14, fill: "none", strokeLinecap: "round" }), /* @__PURE__ */ import_react.default.createElement("path", { d: `M-70,${-480 + shrugUp} C-44,-436 44,-436 70,${-480 + shrugUp}`, stroke: "#3c3c48", strokeWidth: 3, fill: "none", strokeDasharray: "3 6" }), /* @__PURE__ */ import_react.default.createElement("path", { d: "M-122,-494 C-116,-410 116,-410 122,-494", stroke: "#232733", strokeWidth: 24, fill: "none", strokeLinecap: "round" }), /* @__PURE__ */ import_react.default.createElement("path", { d: "M-118,-490 C-110,-420 110,-420 118,-490", stroke: "#3a4152", strokeWidth: 5, fill: "none", opacity: 0.8 }), [-1, 1].map((sd) => /* @__PURE__ */ import_react.default.createElement("g", { key: sd, transform: `translate(${sd * 122},-488) rotate(${sd * -12})` }, /* @__PURE__ */ import_react.default.createElement("ellipse", { rx: 40, ry: 48, fill: "#262b38" }), /* @__PURE__ */ import_react.default.createElement("ellipse", { rx: 40, ry: 48, fill: "none", stroke: "#3d4559", strokeWidth: 4 }), /* @__PURE__ */ import_react.default.createElement("ellipse", { rx: 24, ry: 31, fill: "#141821" }), /* @__PURE__ */ import_react.default.createElement("ellipse", { rx: 24, ry: 31, fill: "none", stroke: sd < 0 ? RIM_L : RIM_R, strokeWidth: 5, opacity: 0.9 }), /* @__PURE__ */ import_react.default.createElement("ellipse", { cx: -12, cy: -22, rx: 10, ry: 6, fill: "#fff", opacity: 0.25 }))), !headAbove && /* @__PURE__ */ import_react.default.createElement(Arm, { sh: shL, hand: L, side: -1, ht: hl, t }), !headAbove && /* @__PURE__ */ import_react.default.createElement(Arm, { sh: shR, hand: R, side: 1, ht: hr, t }), /* @__PURE__ */ import_react.default.createElement("g", { transform: `translate(0,${headY}) rotate(${tilt}, 0, -600)` }, [-1, 1].map((sd) => /* @__PURE__ */ import_react.default.createElement("g", { key: sd }, /* @__PURE__ */ import_react.default.createElement("ellipse", { cx: sd * 121, cy: -716, rx: 21, ry: 38, fill: SKIN_SH }), /* @__PURE__ */ import_react.default.createElement("path", { d: `M${sd * 116},-740 Q${sd * 132},-716 ${sd * 118},-690`, stroke: SKIN_DK, strokeWidth: 5, fill: "none", opacity: 0.6 }))), /* @__PURE__ */ import_react.default.createElement("path", { d: "M-118,-745 C-121,-850 -64,-895 0,-895 C64,-895 121,-850 118,-745 C116,-680 98,-628 62,-596 C40,-577 18,-568 0,-567 C-18,-568 -40,-577 -62,-596 C-98,-628 -116,-680 -118,-745 Z", fill: "url(#n2face)" }), /* @__PURE__ */ import_react.default.createElement("g", { clipPath: "url(#n2faceClip)" }, /* @__PURE__ */ import_react.default.createElement("ellipse", { cx: 0, cy: -842, rx: 150, ry: 46, fill: SKIN_DK, opacity: 0.32, filter: "url(#n2blur)" }), /* @__PURE__ */ import_react.default.createElement("path", { d: "M70,-600 C100,-630 118,-680 122,-760 L140,-760 L140,-560 L60,-560 Z", fill: SKIN_DK, opacity: 0.22, filter: "url(#n2blur)" }), /* @__PURE__ */ import_react.default.createElement("ellipse", { cx: -118, cy: -720, rx: 10, ry: 110, fill: RIM_L, opacity: 0.35, filter: "url(#n2blur)" }), /* @__PURE__ */ import_react.default.createElement("ellipse", { cx: 118, cy: -720, rx: 10, ry: 110, fill: RIM_R, opacity: 0.3, filter: "url(#n2blur)" })), /* @__PURE__ */ import_react.default.createElement("ellipse", { cx: -72, cy: -652, rx: 24, ry: 13, fill: "#ff8f86", opacity: pose === "laugh" || pose === "shock" ? 0.45 : 0.25 }), /* @__PURE__ */ import_react.default.createElement("ellipse", { cx: 72, cy: -652, rx: 24, ry: 13, fill: "#ff8f86", opacity: pose === "laugh" || pose === "shock" ? 0.45 : 0.25 }), Brow(-1), Brow(1), Eye(-48, -1), Eye(48, 1), /* @__PURE__ */ import_react.default.createElement("path", { d: "M8,-700 Q14,-670 4,-652", stroke: SKIN_DK, strokeWidth: 4, fill: "none", strokeLinecap: "round", opacity: 0.6 }), /* @__PURE__ */ import_react.default.createElement("ellipse", { cx: -2, cy: -650, rx: 13, ry: 8, fill: SKIN_SH, opacity: 0.7 }), /* @__PURE__ */ import_react.default.createElement("ellipse", { cx: -6, cy: -656, rx: 5, ry: 3, fill: SKIN_HI }), Mouth(), /* @__PURE__ */ import_react.default.createElement("path", { d: "M-134,-730 C-150,-872 -74,-940 8,-934 C96,-928 154,-866 134,-730 C124,-800 90,-850 0,-858 C-86,-852 -124,-804 -134,-730 Z", fill: "url(#n2hair)" }), fringe.map(([rx, ry, tx, ty, wd], i) => {
    const a = sway(i);
    return /* @__PURE__ */ import_react.default.createElement("g", { key: i, transform: `rotate(${a}, ${rx}, ${ry})` }, /* @__PURE__ */ import_react.default.createElement("path", { d: `M${rx - wd / 2},${ry} Q${(rx + tx) / 2 - wd * 0.35},${(ry + ty) / 2} ${tx},${ty} Q${(rx + tx) / 2 + wd * 0.35},${(ry + ty) / 2} ${rx + wd / 2},${ry} Z`, fill: "url(#n2hair)" }), /* @__PURE__ */ import_react.default.createElement("path", { d: `M${rx - wd * 0.1},${ry + 10} Q${(rx + tx) / 2 - 4},${(ry + ty) / 2} ${tx + (rx < 0 ? 6 : -6)},${ty - 22}`, stroke: "#4a4160", strokeWidth: 4, fill: "none", strokeLinecap: "round", opacity: 0.7 }));
  }), /* @__PURE__ */ import_react.default.createElement("path", { d: "M-78,-900 C-30,-924 40,-922 86,-896", stroke: "#6b5f86", strokeWidth: 9, fill: "none", strokeLinecap: "round", opacity: 0.55 }), /* @__PURE__ */ import_react.default.createElement("path", { d: "M-60,-908 C-20,-924 30,-922 64,-906", stroke: "#cbbff0", strokeWidth: 3, fill: "none", strokeLinecap: "round", opacity: 0.5 }), /* @__PURE__ */ import_react.default.createElement("path", { d: "M-134,-730 L-130,-676 L-116,-736 Z M134,-730 L130,-676 L116,-736 Z", fill: HAIR })), box && box.o > 0 && /* @__PURE__ */ import_react.default.createElement("g", { opacity: box.o, transform: `translate(0,${headY + box.y}) rotate(${tilt * 0.6 + box.rot}, 0, -780) scale(1,${1 + mouth * 0.03})` }, /* @__PURE__ */ import_react.default.createElement("path", { d: "M-168,-972 L168,-972 L176,-626 L-176,-626 Z", fill: "#c8935a", stroke: "#8a5a2c", strokeWidth: 6, strokeLinejoin: "round" }), /* @__PURE__ */ import_react.default.createElement("path", { d: "M-168,-972 L-120,-1010 L208,-1010 L168,-972 Z", fill: "#dcae78", stroke: "#8a5a2c", strokeWidth: 5, strokeLinejoin: "round" }), /* @__PURE__ */ import_react.default.createElement("path", { d: "M168,-972 L208,-1010 L214,-668 L176,-626 Z", fill: "#a8743e", stroke: "#8a5a2c", strokeWidth: 5, strokeLinejoin: "round" }), /* @__PURE__ */ import_react.default.createElement("rect", { x: -30, y: -972, width: 60, height: 346, fill: "#e8c890", opacity: 0.55 }), /* @__PURE__ */ import_react.default.createElement("circle", { cx: -62, cy: -820, r: 20, fill: "#151515" }), /* @__PURE__ */ import_react.default.createElement("circle", { cx: 62, cy: -820, r: 20, fill: "#151515" }), /* @__PURE__ */ import_react.default.createElement("circle", { cx: -56, cy: -826, r: 6, fill: "#fff" }), /* @__PURE__ */ import_react.default.createElement("circle", { cx: 68, cy: -826, r: 6, fill: "#fff" }), /* @__PURE__ */ import_react.default.createElement("path", { d: mouth > 0.1 ? `M-50,-735 L50,-735 L40,${-735 + mouth * 40} L-40,${-735 + mouth * 40} Z` : "M-50,-735 L50,-735", stroke: "#151515", strokeWidth: 8, fill: "#151515", strokeLinejoin: "round" }), /* @__PURE__ */ import_react.default.createElement("text", { x: -110, y: -900, fontFamily: "'DejaVu Sans Mono', monospace", fontWeight: 700, fontSize: 34, fill: "#5a3a18", transform: "rotate(-8,-110,-900)" }, "AI"), /* @__PURE__ */ import_react.default.createElement("path", { d: "M-150,-700 l40,-10 M110,-920 l30,8", stroke: "#8a5a2c", strokeWidth: 4, opacity: 0.6 })), headAbove && /* @__PURE__ */ import_react.default.createElement(Arm, { sh: shL, hand: L, side: -1, ht: hl, t }), headAbove && /* @__PURE__ */ import_react.default.createElement(Arm, { sh: shR, hand: R, side: 1, ht: hr, t }));
};
// Annotate the CommonJS export names for ESM import in node:
0 && (module.exports = {
  Narrator2
});
