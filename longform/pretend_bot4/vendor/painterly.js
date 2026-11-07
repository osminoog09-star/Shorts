// Painterly pass (Claude, 07.11.2026): turns a 3D render into an illustrated look — anisotropic-ish Kuwahara (oil strokes),
// Sobel ink outlines, canvas grain, painterly grade. Used for the long "Film-Mult" S10-D25 (drawn 2.5D look over living 3D).
import * as THREE from 'three';
export const PainterlyShader = {
  uniforms: { tDiffuse: { value: null }, res: { value: new THREE.Vector2(1080, 1920) }, radius: { value: 5 }, ink: { value: .55 }, grain: { value: .06 }, time: { value: 0 }, warmth: { value: .12 } },
  vertexShader: `varying vec2 vUv; void main(){ vUv = uv; gl_Position = projectionMatrix * modelViewMatrix * vec4(position, 1.); }`,
  fragmentShader: `
    varying vec2 vUv; uniform sampler2D tDiffuse; uniform vec2 res; uniform float radius, ink, grain, time, warmth;
    float h(vec2 p){ return fract(sin(dot(p, vec2(127.1, 311.7))) * 43758.5453); }
    float n(vec2 p){ vec2 i = floor(p), f = fract(p); f = f*f*(3.-2.*f); return mix(mix(h(i), h(i+vec2(1,0)), f.x), mix(h(i+vec2(0,1)), h(i+vec2(1,1)), f.x), f.y); }
    vec3 tex(vec2 uv){ return texture2D(tDiffuse, uv).rgb; }
    void main(){
      vec2 px = 1. / res;
      // stroke direction from a slow noise field → strokes are not axis-aligned
      float a = n(vUv * res / 90.) * 6.2831; mat2 R = mat2(cos(a), -sin(a), sin(a), cos(a));
      vec3 m[4]; vec3 s[4];
      for (int k = 0; k < 4; k++) { m[k] = vec3(0.); s[k] = vec3(0.); }
      const int RR = 5; float cnt = float((RR + 1) * (RR + 1));
      for (int j = 0; j <= RR; j++) for (int i = 0; i <= RR; i++) {
        vec2 o = vec2(float(i), float(j)) * radius / float(RR);
        vec3 c0 = tex(vUv + R * vec2(-o.x, -o.y) * px), c1 = tex(vUv + R * vec2(o.x, -o.y) * px), c2 = tex(vUv + R * vec2(o.x, o.y) * px), c3 = tex(vUv + R * vec2(-o.x, o.y) * px);
        m[0] += c0; s[0] += c0*c0; m[1] += c1; s[1] += c1*c1; m[2] += c2; s[2] += c2*c2; m[3] += c3; s[3] += c3*c3;
      }
      float best = 1e9; vec3 col = tex(vUv);
      for (int k = 0; k < 4; k++) { vec3 mu = m[k] / cnt; vec3 v = abs(s[k] / cnt - mu*mu); float sg = v.r + v.g + v.b; if (sg < best) { best = sg; col = mu; } }
      // ink outlines (luma Sobel on the original)
      float l00 = dot(tex(vUv + px*vec2(-1,-1)), vec3(.3,.59,.11)), l10 = dot(tex(vUv + px*vec2(0,-1)), vec3(.3,.59,.11)), l20 = dot(tex(vUv + px*vec2(1,-1)), vec3(.3,.59,.11));
      float l01 = dot(tex(vUv + px*vec2(-1,0)), vec3(.3,.59,.11)), l21 = dot(tex(vUv + px*vec2(1,0)), vec3(.3,.59,.11));
      float l02 = dot(tex(vUv + px*vec2(-1,1)), vec3(.3,.59,.11)), l12 = dot(tex(vUv + px*vec2(0,1)), vec3(.3,.59,.11)), l22 = dot(tex(vUv + px*vec2(1,1)), vec3(.3,.59,.11));
      float gx = -l00 - 2.*l01 - l02 + l20 + 2.*l21 + l22, gy = -l00 - 2.*l10 - l20 + l02 + 2.*l12 + l22;
      float e = smoothstep(.05, .25, length(vec2(gx, gy)) / (.2 + dot(col, vec3(.3,.59,.11))));
      col *= 1. - ink * e * .85;
      // soft posterize: flatter colour planes like a painted illustration
      col = mix(col, floor(col * 9. + .5) / 9., .35);
      // painterly grade: lift shadows to warm umber, slightly desaturate highlights, canvas grain
      float L = dot(col, vec3(.3,.59,.11));
      col = mix(col, col * vec3(1.08, 1.0, .9), warmth); col = mix(vec3(L), col, .92);
      col += (n(vUv * res / 2.2) - .5) * grain * (.6 + L) + (n(vUv * res / 14. + 7.) - .5) * grain * .5;
      gl_FragColor = vec4(col, 1.);
    }`
};
