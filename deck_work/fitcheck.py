import json, sys
from PIL import ImageFont
sys.stdout.reconfigure(encoding="utf-8")
F = {("Calibri",0):"calibri.ttf",("Calibri",1):"calibrib.ttf",("Cambria",0):"cambria.ttc",("Cambria",1):"cambriab.ttf",
     ("Courier New",0):"cour.ttf",("Courier New",1):"courbd.ttf",("Cambria Math",0):"cambria.ttc",("Cambria Math",1):"cambriab.ttf"}
cache = {}
def font(name, bold, size):
    k = (name, int(bold), size)
    if k not in cache:
        cache[k] = ImageFont.truetype("C:/Windows/Fonts/" + F.get((name, int(bold)), "calibri.ttf"), size * 10)
    return cache[k]
bad = 0
for e in json.load(open("fitlog.json", encoding="utf-8")):
    if not e.get("size"): continue
    f = font(e["font"], e["bold"], e["size"])
    width = (e["w"] - (0.25 if e.get("bulleted") else 0)) * 72 * 10  # points*10
    lines = 0
    for para in e["text"].split("\n"):
        cur = ""; n = 1
        for word in para.split(" "):
            t = (cur + " " + word).strip()
            if f.getlength(t) > width and cur:
                n += 1; cur = word
            else: cur = t
        lines += n
    need = lines * e["size"] * 1.2 / 72 + (lines - 1) * e.get("spaceAfter", 0) / 72
    if need > e["h"] + 0.02:
        bad += 1
        print(f"slide {e['slide']:2d}: needs {need:.2f}in, box {e['h']}in ({lines} lines @ {e['size']}pt): {e['text'][:70]!r}")
print("overflows:", bad)
