import time
import numpy as np
from sentence_transformers import CrossEncoder
from unifer import PITANJA, K, sadrzi_clan, model, ucitaj, pitaj_llm

KANDIDATA = 20
MAX_CLANOVA = 3
MAX_ZNAKOVA_CLANA = 4000

reranker = CrossEncoder("cross-encoder/mmarco-mMiniLMv2-L12-H384-v1")
fragmenti,index = ucitaj("B")

ceo_clan = {}
for fr in fragmenti:
    naslov, _, telo = fr["tekst"].partition("\n")
    ceo_clan[naslov] = ceo_clan.get(naslov, "") + telo.strip() + "\n"

for pitanje, tacan_clan in PITANJA:
    print("=" * 80)
    print(f"PITANJE: {pitanje} (Tacan: {tacan_clan})")

    pocetak = time.perf_counter()
    vektor = model.encode(["query: " + pitanje], normalize_embeddings=True)
    _, pozicije = index.search(vektor, KANDIDATA)
    kandidati = [fragmenti[p] for p in pozicije[0]]

    ocene = reranker.predict([(pitanje, fr["tekst"]) for fr in kandidati])
    pronadjeni = [kandidati[i] for i in np.argsort(-ocene)[:K]]
    ms = (time.perf_counter() - pocetak) * 1000

    print(f"\n Pristup C: {ms:.1f} ms")
    rang = None
    for mesto, fr in enumerate(pronadjeni, start=1):
        pogodak = sadrzi_clan(fr, tacan_clan)
        if pogodak and rang is None:
            rang = mesto
        oznaka = "   TACAN" if pogodak else ""
        print(f"    {mesto}. {fr['clanovi'][0]}{oznaka}")
    print(f" RANG tacnog clana: {rang if rang else f'nije u prvih {K}'}")

    naslovi = list(dict.fromkeys(fr['clanovi'][0] for fr in pronadjeni))[:MAX_CLANOVA]
    celi_clanovi = [{"tekst": n + "\n" + ceo_clan[n][:MAX_ZNAKOVA_CLANA]} for n in naslovi]
    print(f" LLM-u saljemo cele clanove: {', '.join(naslovi)}")

    pocetak = time.perf_counter()
    odgovor = pitaj_llm(pitanje, celi_clanovi)
    print(f" LLM odgovor: ({time.perf_counter() - pocetak:.2f} s): \n {odgovor}")
