"""Place quiet, synthesized Foley accents at the staged V4 actions."""
from pathlib import Path
import argparse
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt

# Absolute times refer to the unchanged Bot Audit timeline.
EVENTS = [
    (109.70, "wheel", .91), (112.06, "paper", .32),
    (165.86, "paper", .41), (246.05, "paper", .34),
    (353.03, "wheel", .79), (467.65, "beep", .17),
    (502.68, "latch", .20), (617.18, "beep", .16),
    (726.17, "paper", .24), (735.13, "paper", .35),
    (796.99, "water", .65), (837.32, "latch", .22),
    (944.91, "beep", .22), (1003.0, "beep", .17),
    (1062.47, "wheel", .92), (1257.43, "paper", .31),
    (1274.97, "paper", .46),
]

def render_event(kind, duration, sample_rate, rng):
    n = round(duration * sample_rate)
    t = np.arange(n, dtype="float64") / sample_rate
    noise = rng.standard_normal(n)
    if kind == "beep":
        audio = np.sin(2 * np.pi * 591 * t) + .24 * np.sin(2 * np.pi * 947 * t)
        decay = 15
    elif kind == "latch":
        audio = .7 * np.sin(2 * np.pi * 142 * t) + .2 * noise
        decay = 24
    else:
        low, high = {"wheel": (65, 370), "paper": (560, 3900), "water": (640, 2400)}[kind]
        audio = sosfilt(butter(2, (low, high), btype="bandpass", fs=sample_rate, output="sos"), noise)
        audio *= 0.62 + 0.38 * np.sin(2 * np.pi * (16 if kind == "water" else 8) * t) ** 2
        decay = 3 if kind in ("wheel", "water") else 7
    envelope = np.minimum(1, t / .014) * np.minimum(1, (duration - t) / .035) * np.exp(-decay * t)
    audio *= envelope
    return audio * (.013 / max(np.max(np.abs(audio)), .001))

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    audio, rate = sf.read(args.source, dtype="float32")
    assert audio.ndim == 1
    foley = np.zeros_like(audio)
    rng = np.random.default_rng(20261112)
    for time, kind, duration in EVENTS:
        accent = render_event(kind, duration, rate, rng)
        start = round(time * rate)
        foley[start:start + len(accent)] += accent
    mixed = audio + foley
    assert len(mixed) == len(audio)
    assert np.max(np.abs(mixed)) < .995
    sf.write(args.output, mixed, rate, subtype="PCM_24")
    print(f"Foley: {len(EVENTS)} accents, max {20*np.log10(np.max(np.abs(foley))):.1f} dBFS, {len(audio)/rate:.3f}s")

if __name__ == "__main__":
    main()
