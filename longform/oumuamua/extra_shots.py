#!/usr/bin/env python3
"""Denis 07.11: «больше сцен разных» → every beat that reused a shot gets its own new frame.
Run after chapters.py (it rewrites levels/c2..c8.json). Idempotent."""
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
SPACE_NEG = "landscape, ground, horizon, mountains, desert, planet surface, terrain, boat, sea, water"
S, N = "space", "scene"
NEW = {  # beat id: (kind, prompt)
    "c0b03": (N, "two astronomers at night leaning over a desk with printed orbit diagrams and a glowing monitor, one pointing at a curved line, tense, dark observatory office"),
    "c0b06": (S, "an elongated dark rock moving away from the bright sun, the sun glowing behind it, its long shadow stretching into space, stars"),
    "c1b05": (S, "an elongated cigar shaped reddish asteroid and next to it a flat disc shaped asteroid, both floating in black outer space side by side, comparison, stars"),
    "c1b06": (N, "a tall skyscraper standing at night with an elongated dark asteroid of the same size hovering beside it in the sky, sense of scale, surreal painting"),
    "c1b09": (S, "a dark elongated asteroid with a faint glowing arrow of motion pushing it away from the sun, invisible force, stars, mysterious"),
    "c1b10": (S, "a comet nucleus with bright white gas jets erupting from cracks in its icy surface, sunlight, black space"),
    "c1b14": (S, "a collage-like scene in space: a translucent iceberg, a silver solar sail and a dark rock floating together in black outer space, stars"),
    "c2b02": (S, "planets moving on elliptical orbits around a bright sun, glowing orbit rings, small comets on long looping orbits, black space"),
    "c2b05": (S, "a dark asteroid streaking past the sun at enormous speed, motion streaks of light, black space, dramatic"),
    "c2b09": (S, "a tiny barely visible dark object against a field of countless stars, almost invisible, deep space, mysterious"),
    "c2b11": (N, "a computer screen in a dark observatory showing a series of star field images with one dot circled, astronomer silhouette, night"),
    "c2b12": (S, "a small dark object passing very close to the blazing sun inside the orbit of a small grey planet, solar flares, black space"),
    "c2b14": (S, "stars of the galaxy slowly moving, long glowing star trails across deep space, time passing, majestic"),
    "c2b15": (S, "a dying red giant star in deep space, faded planets around it, an icy fragment drifting away from it, melancholic"),
    "c2b16": (N, "an old astronomer's notebook on a desk with handwritten symbols and a sketch of a curved trajectory, lamp light, no readable text"),
    "c2b17": (S, "a lone glowing object leading a path of light through the stars, first of its kind, majestic, deep space"),
    "c3b03": (N, "a graph of light curve drawn as a glowing line on a dark screen, peaks and valleys, astronomer hand pointing, night, no readable text"),
    "c3b06": (S, "an extremely long thin asteroid like a cigar, many times longer than wide, floating in black outer space, sunlight along its length"),
    "c3b09": (N, "an artist painting an elongated red asteroid on a canvas in a dim studio at night, easel, brushes, warm lamp"),
    "c3b11": (S, "a large asteroid shattering after an impact in a young star system, fragments and dust flying, young star glowing behind"),
    "c3b12": (S, "a reddish icy body at the cold edge of the solar system bombarded by faint streaks of cosmic rays, black space"),
    "c3b15": (S, "an elongated dark asteroid floating above a tiny earth for scale, black outer space, stars"),
    "c3b16": (S, "a small dark tumbling asteroid surrounded by question marks of faint starlight, mysterious, black space"),
    "c4b05": (S, "a dark elongated asteroid with its predicted path and its real path diverging as two glowing lines, black space, stars"),
    "c4b07": (N, "a printed scientific journal lying on a desk next to a coffee cup and glasses, morning light, no readable text"),
    "c4b09": (S, "a classic comet with a glowing coma and long blue tail near the sun, stars"),
    "c4b11": (N, "a large telescope instrument with spectrograph and cables in a cold observatory, scientists looking at empty readings on screens, blue light"),
    "c4b13": (S, "a dark asteroid spinning steadily in black outer space with circular motion trails showing smooth rotation, stars"),
    "c4b16": (S, "beams of golden sunlight striking a dark object in black space like a gentle push, light rays, majestic"),
    "c5b03": (S, "a small real solar sail spacecraft with four triangular silver sails unfolding in black outer space above the earth"),
    "c5b05": (S, "a precisely engineered thin metallic structure drifting in deep space, alien technology, faint glow, stars"),
    "c5b07": (S, "a sleek ancient alien probe approaching a bright yellow sun in deep space, mysterious, stars"),
    "c5b10": (N, "a radio telescope control room at night with silent monitors showing flat noise lines, empty chair, quiet"),
    "c5b12": (N, "a professor writing a book at night at a desk full of papers in a book-lined study, lamp, determined"),
    "c5b15": (S, "a powerful laser beam from earth pushing a tiny probe with a light sail toward distant stars, science fiction, black space"),
    "c5b17": (S, "a silver solar sail and a dark natural rock floating opposite each other in black outer space, a choice, stars"),
    "c6b02": (S, "a translucent blue ice block in black outer space with faint invisible shimmering vapor leaving it, sunlight, stars"),
    "c6b04": (S, "a translucent iceberg slowly evaporating into nothing in deep space under the light of many stars, fading"),
    "c6b08": (S, "a flat bright nitrogen ice slab in black outer space with a faint transparent vapor jet pushing it, sunlight, stars"),
    "c6b09": (S, "many white ice fragments scattered through the galaxy between stars, deep space, vast"),
    "c6b11": (S, "a delicate fluffy dust clump breaking apart slowly in sunlight, black outer space, stars"),
    "c6b15": (S, "a dark asteroid moving slightly off its path with a barely visible shimmer behind it, black space, subtle"),
    "c6b17": (S, "the solar system with the sun in the center seen from far away, waiting, a faint new object approaching from the dark, stars"),
    "c7b02": (N, "an amateur astronomer man in a warm jacket next to his homemade telescope at night in a small observatory, starry sky"),
    "c7b04": (S, "a comet with a bright fuzzy coma and long curved tail against stars, deep space, beautiful"),
    "c7b05": (S, "two different interstellar visitors in space: a dark tailless cigar rock and a bright fuzzy comet, side by side, stars"),
    "c7b10": (S, "a comet with a glowing coma and tail with a faint mysterious light inside it, black space, intrigue"),
    "c7b12": (N, "a giant telescope camera with a huge lens inside an observatory, engineers in clean suits, dramatic light"),
    "c7b16": (S, "a spacecraft flying close to a dark interstellar rock, its lights illuminating the surface, black space, stars"),
    "c8b04": (N, "a hand holding a printed photograph of a star field with a tiny dot, warm lamp, close-up, no readable text"),
    "c8b06": (S, "countless faint dark objects drifting between distant stars, an invisible river of travelers, deep space"),
    "c8b12": (N, "a white observatory dome on a volcano summit at sunrise above the clouds, golden light, hopeful"),
    "c8b14": (S, "the pale blue earth seen from deep space with a tiny visitor passing by, vast darkness, stars, contemplative"),
}
for c in ["c0", "c1", "c2", "c3", "c4", "c5", "c6", "c7", "c8"]:
    p = HERE / "levels" / f"{c}.json"; j = json.loads(p.read_text(encoding="utf-8"))
    ids = {s["id"] for s in j["shots"]}
    for k, b in enumerate(j["beats"]):
        if b["id"] not in NEW: continue
        kind, prompt = NEW[b["id"]]; sid = f"{c}_x{b['id'][-2:]}"
        if sid not in ids:
            s = {"id": sid, "seed": 2000 + int(c[1]) * 100 + int(b["id"][-2:]), "prompt": prompt, "layers": ["dust"]}
            if kind == S: s["neg"] = SPACE_NEG
            j["shots"].append(s); ids.add(sid)
        b["shot"] = sid
    p.write_text(json.dumps(j, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
print("new shots", len(NEW))
