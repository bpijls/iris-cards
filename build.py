#!/usr/bin/env python3
"""Select 24 Iris cards, generate flower art via vonk, emit data.json + images."""
import base64, csv, json, os, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
IMGDIR = os.path.join(HERE, "images")
os.makedirs(IMGDIR, exist_ok=True)

def load_env(path):
    if not os.path.exists(path):
        return
    for line in open(path):
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

load_env(os.path.join(HERE, ".env"))

VONK_BASE_URL = os.environ["VONK_BASE_URL"]
VONK = f"{VONK_BASE_URL}/images/generations"
KEY = os.environ["VONK_API_KEY"]

# --- load + subset ---------------------------------------------------------
rows = list(csv.DictReader(open(os.path.join(HERE, "iris_raw.csv"))))
by_species = {}
for r in rows:
    by_species.setdefault(r["species"], []).append(r)

PICK = [0, 7, 14, 21, 28, 35, 42, 49]  # 8 per species, spread by sepal length
cards = []
for sp, items in by_species.items():
    items.sort(key=lambda r: (float(r["sepal_length"]), float(r["petal_length"])))
    for i, idx in enumerate(PICK):
        r = items[idx]
        cards.append({
            "id": f"{sp}-{i+1:02d}",
            "species": sp,
            "sepal_length": float(r["sepal_length"]),
            "sepal_width": float(r["sepal_width"]),
            "petal_length": float(r["petal_length"]),
            "petal_width": float(r["petal_width"]),
        })

PALETTE = {
    "setosa": "deep violet and blue-purple petals with a yellow-white throat",
    "versicolor": "blue and lavender petals with purple veining and a yellow signal patch",
    "virginica": "large royal-purple and violet-blue petals with delicate white veins",
}

def gen_image(card):
    out = os.path.join(IMGDIR, card["id"] + ".png")
    if os.path.exists(out) and os.path.getsize(out) > 1000:
        return
    sp = card["species"]
    prompt = (
        f"Botanical watercolour illustration of a single Iris {sp} flower in bloom, "
        f"{PALETTE[sp]}, slender green stem and leaves, centered, "
        f"soft even lighting, plain pale cream background, vintage scientific plate style, "
        f"highly detailed, no text, no border"
    )
    body = json.dumps({"model": "image", "prompt": prompt, "n": 1, "size": "1024x1024"}).encode()
    req = urllib.request.Request(VONK, data=body,
        headers={"Authorization": f"Bearer {KEY}", "Content-Type": "application/json"})
    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=300) as resp:
                data = json.load(resp)
            b64 = data["data"][0]["b64_json"]
            open(out, "wb").write(base64.b64decode(b64))
            print("  ok", card["id"])
            return
        except Exception as e:
            print("  retry", card["id"], e)
            time.sleep(3)
    print("  FAILED", card["id"])

if __name__ == "__main__":
    only = sys.argv[1] if len(sys.argv) > 1 else None
    for c in cards:
        if only and only != "all" and c["species"] != only:
            continue
        print("gen", c["id"])
        gen_image(c)
    json.dump({"cards": cards}, open(os.path.join(HERE, "data.json"), "w"), indent=2)
    open(os.path.join(HERE, "data.js"), "w").write(
        "window.IRIS_DATA = " + json.dumps({"cards": cards}) + ";")
    print("wrote data.json / data.js with", len(cards), "cards")
