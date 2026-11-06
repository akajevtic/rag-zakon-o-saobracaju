import time 
from unifer import PITANJA, K, model, ucitaj,sadrzi_clan,pitaj_llm

PONAVLJANJA = 1000

fragmenti, indexi = {}, {}
for ime in ("A","B"):
    fragmenti[ime], indexi[ime] = ucitaj(ime)

for pitanje,tacan_clan in PITANJA:
    print("=" * 80)
    print(f"Pitanje: {pitanje} (Tacan: {tacan_clan})")

    pocetak = time.perf_counter()
    vektor = model.encode(["query: " + pitanje],normalize_embeddings=True)
    print(f"Embedding pitanja: {(time.perf_counter() - pocetak) * 1000:.1f} ms")

    for ime in ("A","B"):
        pocetak = time.perf_counter()
        for _ in range(PONAVLJANJA):
            rastojanja, pozicije = indexi[ime].search(vektor, K)
        ms = (time.perf_counter() - pocetak) * 1000 / PONAVLJANJA

        print(f"\n Pristup {ime} (pretraga {ms:.3f}) ms")
        rang = None
        for mesto, (r, p) in enumerate(zip(rastojanja[0], pozicije[0]),start=1):
            fr = fragmenti[ime][p]
            pogodak = sadrzi_clan(fr, tacan_clan)
            if pogodak and rang is None:
                rang = mesto
            oznaka ="   Tacan" if pogodak else ""
            print(f" {mesto}.rastojanje {r:.3f} {', '.join(fr['clanovi'])} {oznaka}")
        print(f" Rang tacnog clana: {rang if rang else f'nije u prvih {K}'}")

        pronadjeni = [fragmenti[ime][p] for p in pozicije[0]]
        pocetak = time.perf_counter()
        odgovor = pitaj_llm(pitanje, pronadjeni)
        print(f" LLM odgovor ({time.perf_counter() - pocetak:.2f} s):\n {odgovor}")