# RAG sistem nad Zakonom o bezbednosti saobraćaja na putevima

Projekat br. 1b iz predmeta Napredne baze podataka (RAF, 2026/2027).

Sistem odgovara na pitanja o **Zakonu o bezbednosti saobraćaja na putevima Republike Srbije**. Iz zakona pronalazi relevantne delove teksta preko vektorskog indeksa (FAISS), a odgovor na osnovu njih generiše jezički model `openai/gpt-oss-120b` preko Groq platforme.

Porede se tri pristupa:

| Pristup | Podela teksta | Indeks | Dodatno |
|---|---|---|---|
| **A** | fiksna dužina, 80 reči sa preklapanjem od 20 | `IndexFlatL2` (tačna pretraga) | – |
| **B** | po članovima i pasusima (do 500 znakova, svaki fragment počinje naslovom „Član N“) | `IndexHNSWFlat` (graf, približna pretraga) | – |
| **C** | kao B | kao B | reranking (cross-encoder) + hijerarhijsko dohvatanje celih članova |

## Baza znanja

- Izvor: [paragraf.rs](https://www.paragraf.rs/propisi/zakon_o_bezbednosti_saobracaja_na_putevima.html), osnovni tekst zakona bez naknadnih izmena i dopuna
- 362 člana, oko 480 KB teksta
- Pristup A: 1188 fragmenata, pristup B: 1214 fragmenata

## Modeli

| Namena | Model |
|---|---|
| Embedding | `intfloat/multilingual-e5-small`: višejezični model (uključujući srpski), 384 dimenzije, radi lokalno |
| Reranking (pristup C) | `cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`: višejezični cross-encoder, radi lokalno |
| Generisanje odgovora | `openai/gpt-oss-120b` preko Groq API-ja |

## Instalacija

Potreban je Python 3.10 ili noviji.

```bash
pip install sentence-transformers faiss-cpu groq numpy
```

Groq API ključ (besplatan na [console.groq.com](https://console.groq.com)) se čuva kao promenljiva okruženja, a ne u kodu:

```bash
setx GROQ_API_KEY "api_key"
```

Posle `setx` treba otvoriti novi terminal.

## Pokretanje

Koraci 1–3 se pokreću jednom i prave fajlove sa podacima. Ti fajlovi su već priloženi, pa se može odmah preći na korak 4.

| Korak | Komanda | Rezultat |
|---|---|---|
| 1. Preuzimanje zakona | `python preuzmi_zakon.py` | `zakon.txt` |
| 2. Podela na fragmente | `python podela.py` | `fragmenti_A.json`, `fragmenti_B.json` |
| 3. Embedding i indeksi | `python indexi.py` | `indeks_A.faiss`, `indeks_B.faiss` |
| 4. Evaluacija A i B | `python preciznaEvaluacija.py` | rang tačnog člana, vremena i LLM odgovori za 3 pitanja |
| 5. Evaluacija C | `python c_pristup.py` | isto, za pristup C |
| 6. Interaktivna pitanja (B) | `python preciznoPitaj.py` | korisnik kuca pitanje, izlaz sa `kraj` |
| 7. Interaktivna pitanja (C) | `python preciznoPitajC.py` | isto, sa reranking-om i hijerarhijskim dohvatanjem (tačnije, oko 1 s sporije) |

Pri prvom pokretanju modeli se preuzimaju sa Hugging Face-a (embedding oko 470 MB, reranker oko 470 MB).

## Struktura

| Fajl | Opis |
|---|---|
| `preuzmi_zakon.py` | preuzima HTML sa paragraf.rs i izvlači tekst članova |
| `podela.py` | deli zakon na fragmente za pristupe A i B |
| `indexi.py` | pravi embeddinge i FAISS indekse |
| `unifer.py` | zajednički kod: pitanja, model, učitavanje indeksa, poziv LLM-a |
| `preciznaEvaluacija.py` | evaluacija pristupa A i B |
| `c_pristup.py` | evaluacija pristupa C (reranking + hijerarhijsko dohvatanje) |
| `preciznoPitaj.py` | interaktivni režim (pristup B) |
| `preciznoPitajC.py` | interaktivni režim (pristup C) |
| `evaluacija.py`, `pitaj.py` | prva verzija istih programa, pre izdvajanja zajedničkog koda u `unifer.py` |
| `test_setup.py` | provera da su biblioteke i Groq ključ ispravno podešeni |

## Evaluacija

Za svako od tri pitanja unapred je ručno određen član zakona u kom se nalazi odgovor:

| Pitanje | Član |
|---|---|
| Koja je dozvoljena koncentracija alkohola u krvi vozača? | Član 187 |
| Da li vozač sa probnom dozvolom sme da vozi noću? | Član 182 |
| Da li moram da imam zimske gume? | Član 131 |

Meri se na kom mestu u prvih 5 rezultata se pojavljuje tačan član, vreme pretrage i vreme odgovora LLM-a. Rezultati i analiza su u izveštaju.
