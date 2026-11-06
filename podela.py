import json

with open("zakon.txt", encoding="utf-8") as f:
    redovi = [r for r in f.read().split("\n") if r]

clanovi = []
for red in redovi:
    if red.startswith("Član "):
        clanovi.append((red,[]))
    else:
        clanovi[-1][1].append(red)

reci  = []
for naslov, pasusi in clanovi:
    for rec in " ".join([naslov] + pasusi).split():
        reci.append((rec,naslov))

VELICINA, PREKLAPANJE = 80,20
fragmenti_A = []
for start in range(0,len(reci), VELICINA - PREKLAPANJE):
    deo = reci[start:start + VELICINA]
    fragmenti_A.append({
        "tekst": " ".join(r for r, _ in deo),
        "clanovi": list(dict.fromkeys(c for _, c in deo)),
    })

MAX_ZNAKOVA = 500
fragmenti_B = []
for naslov, pasusi in clanovi:
    trenutni = ""
    for pasus in pasusi:
        if trenutni and len(trenutni) + len(pasus) > MAX_ZNAKOVA:
            fragmenti_B.append({"tekst": naslov + "\n" + trenutni, "clanovi": [naslov]})
            trenutni = ""
        trenutni += pasus + "\n"
    fragmenti_B.append({"tekst": naslov + "\n" + trenutni.strip(), "clanovi": [naslov]})

with open("fragmenti_A.json", "w", encoding="utf-8") as f:
    json.dump(fragmenti_A, f, ensure_ascii=False, indent=1)
with open("fragmenti_B.json", "w", encoding="utf-8") as f:
    json.dump(fragmenti_B, f, ensure_ascii=False, indent=1)

for ime, fr in (("A", fragmenti_A), ("B",fragmenti_B)):
    duzine = [len(x["tekst"]) for x in fr]
    print(f"Pristup {ime}: {len(fr)} fragmenata, prosek {sum(duzine) // len(duzine)} znakova, "
            f"najkraci {min(duzine)}, najduzi {max(duzine)}")
    
assert len(clanovi) == 362
assert all(f["clanovi"] for f in fragmenti_A + fragmenti_B)
