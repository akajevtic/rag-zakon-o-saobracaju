#Prva verzija
#Radi bez dodatne prezinosti

import json
import os
import time
import faiss
from groq import Groq
from sentence_transformers import SentenceTransformer

K = 5

model = SentenceTransformer("intfloat/multilingual-e5-small")
client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# koristimo samo pristup B, jer je bio bolji u evaluaciji
with open("fragmenti_B.json", encoding="utf-8") as f:
    fragmenti = json.load(f)
indeks = faiss.read_index("indeks_B.faiss")

UPUTSTVO = (
    "Ti si asistent za Zakon o bezbednosti saobraćaja na putevima Republike Srbije. "
    "Odgovaraj isključivo na osnovu datih fragmenata zakona, ne koristi svoje znanje. "
    "Navedi broj člana na koji se oslanjaš. "
    "Ako odgovor nije u fragmentima, reci da ga ne možeš naći u datom tekstu. "
    "Odgovori kratko, u najviše 3 rečenice."
)


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

print(f"Postavi pitanje o Zakonu Bezbednosti saobracaja (izlazi se sa kraj)")
while True:
    pitanje = input("\nPitanje: ").strip()
    if pitanje.lower() == "kraj":
        break
    if not pitanje:
        continue

    pocetak = time.perf_counter()
    vektor = model.encode(["query: " + pitanje], normalize_embeddings=True)
    _, pozicije = indeks.search(vektor,K)
    pronadjeni = [fragmenti[p] for p in pozicije[0]]
    odgovor = pitaj_llm(pitanje, pronadjeni)

    print(f"\nOdgovor: {odgovor}")
    print(f"Izvori: {', '.join(fr['clanovi'][0] for fr in pronadjeni)}")
    print(f"Vreme: {time.perf_counter() - pocetak:.2f}s")