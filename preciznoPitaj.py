import time
from unifer import model, K, ucitaj, pitaj_llm

fragmenti, index = ucitaj("B")

print(f"Postavi pitanje o Zakonu i bezbednosti saobracaja (izlazi se sa kraj)")

while True:
    pitanje = input("\nPitanje: ").strip()
    if pitanje.lower() == "kraj":
        break
    if not pitanje:
        continue

    pocetak = time.perf_counter()
    vektor = model.encode(["query: " + pitanje], normalize_embeddings=True)
    _, pozicije = index.search(vektor, K)
    pronadjeni = [fragmenti[p] for p in pozicije[0]]
    odgovor = pitaj_llm(pitanje, pronadjeni)

    print(f"Odgovor: {odgovor}")
    print(f"Izvori: {', '.join(fr['clanovi'][0] for fr in pronadjeni)}")
    print(f"Vreme: {time.perf_counter() - pocetak:.2f} s")

