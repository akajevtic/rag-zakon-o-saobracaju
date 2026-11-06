import os
from groq import Groq
from sentence_transformers import SentenceTransformer
import faiss

print("faiss:", faiss.__version__)
print("Groq kljuc postoji:", os.getenv("GROQ_API_KEY") is not None)

model = SentenceTransformer("intfloat/multilingual-e5-small")
print("Dimenzija vektora:", model.get_sentence_embedding_dimension())

client = Groq(api_key=os.getenv("GROQ_API_KEY"))
odgovor = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    messages=[{"role": "user", "content": "Da li vozac sme da vozi pod dejstom alkohola"}],
)
print("LLM:", odgovor.choices[0].message.content)