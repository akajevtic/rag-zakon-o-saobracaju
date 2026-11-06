#Prva verzija
#Radi bez dodatne prezinosti

import json 
import os
import time
import faiss
from groq import Groq
from sentence_transformers import SentenceTransformer

PITANJA = [
    ("Koja je dozvoljena koncentracija alkohola u krvi vozača?", "Član 187"),
    ("Da li vozač sa probnom dozvolom sme da vozi noću?", "Član 182"),
    ("Da li moram da imam zimske gume?", "Član 131"),
]

k = 5
PONAVLJANJA = 1000

model = SentenceTransformer("intfloat/multilingual-e5-small")

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

UPUTSTVO = (
    "Ti si asistent za Zakon o bezbednosti saobraćaja na putevima Republike Srbije. "
    "Odgovaraj iskljucivo na osnovu datih fragmenata zakona, ne koristi svoje znanje. "
    "Navedi broj člana na koji se pozivaš, "
    "Ako odgovor nije u fragmentima, reci da ga ne možeš naći u datom tekstu. "
    "Odgovori kratko, u najviše 3 rečenice. "
)

def pitaj_llm(pitanje,pronadjeni):
    kontekst = "\n\n".join(f"[{i}] {fr['tekst']}" for i, fr in enumerate(pronadjeni, start=1))
    odgovor = client.chat.completions.create(
        model = "openai/gpt-oss-120b",
        temperature=0,
        messages=[
            {"role": "system", "content": UPUTSTVO},
            {"role": "user", "content": f"Fragmenti zakona: \n{kontekst}\n\nPItanje: {pitanje}"},
        ],
    )
    return odgovor.choices[0].message.content


fragmenti, indeksi = {}, {}

for ime in ("A","B"):
    with open(f"fragmenti_{ime}.json",encoding="utf-8") as f:
        fragmenti[ime] = json.load(f)
    indeksi[ime] = faiss.read_index(f"indeks_{ime}.faiss")

def sadrzi_clan(fragment,clan):
    return clan in [c.rstrip("*") for c in fragment["clanovi"]]


for pitanje, tacan_clan in PITANJA:
    print("=" * 80)
    print(f"PITANJA: {pitanje} (tačan: {tacan_clan} )")

    pocetak = time.perf_counter()
    vektor = model.encode(["query: " + pitanje], normalize_embeddings=True)
    print(f"Embedding pitanje: {(time.perf_counter() - pocetak) * 1000:.1f} ms")

    for ime in ("A", "B"):
        pocetak = time.perf_counter()
        for _ in range(PONAVLJANJA):
            rastojanja, pozicije = indeksi[ime].search(vektor,k)
        ms = (time.perf_counter() - pocetak) * 1000 / PONAVLJANJA

        print(f"\n Pristup {ime} (pretraga {ms:.3f} ms):")
        rang = None
        for mesto, (r, p) in enumerate(zip(rastojanja[0],pozicije[0]), start = 1):
            fr = fragmenti[ime][p]
            pogodak = sadrzi_clan(fr, tacan_clan)
            if pogodak and rang is None:
                rang = mesto
            oznaka = "    Tacan" if pogodak else ""
            print(f" {mesto}, rastojanje {r:.3f} {', '.join(fr['clanovi'])} {oznaka}")
        print(f" Rang tacnog clana: {rang if rang else f'nije u prvih {k}'}")

        pronadjeni = [fragmenti[ime][p] for p in pozicije[0]]
        pocetak = time.perf_counter()
        odgovor = pitaj_llm(pitanje, pronadjeni)
        print(f"LLM odgovor: ({time.perf_counter() - pocetak:.2f} s):\n {odgovor}")

