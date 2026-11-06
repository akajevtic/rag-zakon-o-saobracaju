import json
import time
import numpy as np
import faiss
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("intfloat/multilingual-e5-small")

for ime in ("A", "B"):
    with open(f"fragmenti_{ime}.json", encoding="utf-8") as f:
        fragmenti = json.load(f)

    tekstovi = ["passage: " + fr["tekst"] for fr in fragmenti]

    pocetak = time.time()
    vektori = model.encode(tekstovi, normalize_embeddings=True, show_progress_bar=True)
    vektori = np.asarray(vektori, dtype="float32")
    print(f"{ime}: {vektori.shape[0]} vektora dimenzije {vektori.shape[1]}, embedding trajao {time.time() - pocetak:.1f} s")

    dim = vektori.shape[1]
    if ime == "A":
        indeks = faiss.IndexFlatL2(dim)
    else:
        indeks = faiss.IndexHNSWFlat(dim,32)
    indeks.add(vektori)

    faiss.write_index(indeks, f"indeks_{ime}.faiss")
    print(f"{ime}: u indeksu {indeks.ntotal} vektora, sacuvano u indeks_{ime}.faiss\n")

