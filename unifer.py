## Zajednicki fajl za preziznaEvaluacija.py preciznoPitaj.py i c_pristup.py

import json
import os
import faiss
from groq import Groq
from sentence_transformers import SentenceTransformer

# (pitanje, clan u kome je odgovor) - clan smo nasli rucno u zakon.txt
PITANJA = [
    ("Koja je dozvoljena koncentracija alkohola u krvi vozača?", "Član 187"),
    ("Da li vozač sa probnom dozvolom sme da vozi noću?", "Član 182"),
    ("Da li moram da imam zimske gume?", "Član 131"),
]
K = 5   # koliko fragmenata vracamo i saljemo LLM-u

model = SentenceTransformer("intfloat/multilingual-e5-small")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

UPUTSTVO = (
    "Ti si asistent za Zakon o bezbednosti saobraćaja na putevima Republike Srbije. "
    "Odgovaraj isključivo na osnovu datih fragmenata zakona, ne koristi svoje znanje. "
    "Navedi broj člana na koji se oslanjaš. "
    "Ako odgovor nije u fragmentima, reci da ga ne možeš naći u datom tekstu. "
    "Odgovori kratko, u najviše 3 rečenice."
)


def ucitaj(ime):
    """Vraca (fragmenti, indeks) za pristup "A" ili "B"."""
    with open(f"fragmenti_{ime}.json", encoding="utf-8") as f:
        fragmenti = json.load(f)
    return fragmenti, faiss.read_index(f"indeks_{ime}.faiss")


def sadrzi_clan(fragment, clan):
    # neki naslovi u zakonu imaju zvezdice ("Član 279**"), pa ih skidamo pre poredjenja
    return clan in [c.rstrip("*") for c in fragment["clanovi"]]


def pitaj_llm(pitanje, pronadjeni):
    kontekst = "\n\n".join(f"[{i}] {fr['tekst']}" for i, fr in enumerate(pronadjeni, start=1))
    odgovor = client.chat.completions.create(
        model="openai/gpt-oss-120b",
        temperature=0,
        messages=[
            {"role": "system", "content": UPUTSTVO},
            {"role": "user", "content": f"Fragmenti zakona:\n{kontekst}\n\nPitanje: {pitanje}"},
        ],
    )
    return odgovor.choices[0].message.content