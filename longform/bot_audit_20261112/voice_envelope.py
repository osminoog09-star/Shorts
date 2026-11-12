"""Derive a 30 fps mouth-opening envelope from the studio narration WAV."""
from pathlib import Path
import argparse
import numpy as np
import soundfile as sf


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("narration", type=Path)
    parser.add_argument("work_dir", type=Path)
    args = parser.parse_args()
    audio, rate = sf.read(args.narration, dtype="float32")
    if audio.ndim != 1 or rate % 30:
        parser.error("expected mono narration with a sample rate divisible by 30")
    step = rate // 30
    blocks = np.pad(audio, (0, (-len(audio)) % step)).reshape(-1, step)
    rms = np.sqrt((blocks * blocks).mean(axis=1))
    smoothed = np.convolve(rms, [.23, .54, .23], mode="same")
    levels = np.clip((smoothed - .008) / .13, 0, 1)
    (levels * 255).astype("u1").tofile(args.work_dir / "voice_envelope.u8")


if __name__ == "__main__":
    main()
