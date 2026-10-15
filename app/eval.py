import csv
import chromadb # pyright: ignore[reportMissingImports]
from sentence_transformers import SentenceTransformer # pyright: ignore[reportMissingImports]

RUN_NAME = "baseline_v2"   # change per experiment, e.g. "no_prefix"
USE_PREFIX = True
PREFIX = "Represent this sentence for searching relevant passages: "

QUERIES = [
    "cozy meal for a rainy day, low effort, I'm tired",
    "spicy dinner in under 30 minutes",
    "light lunch, nothing heavy, something soupy",
    "impress guests on the weekend",
    "something with rice but high protein and healthy",
    "don't have much ingredient so some thing with less ingredient but tasty not blend",
    "really not in a mood for lot of plates to clean so i guess one pot receipe with rice or chicken",
    "strict vegetarian comfort food",
    "I have eggs, rice, tamato,peas and onions, what can I make",
    "warm soup for a cold or sick day",
    "high-protein dinner without eggs",
    "quick snack for late night",
    "something Italian",
    "celebration dish, I got an interview call",
    "I'm bored of my usual food, surprise me",
    "i have spegethi, tamato and cheese what can i make",
]

model = SentenceTransformer("BAAI/bge-small-en-v1.5")
col = chromadb.PersistentClient(path="chroma_db").get_collection("meals")

with open(f"eval_{RUN_NAME}.csv", "w", newline="", encoding="utf-8") as f:
    w = csv.writer(f)
    w.writerow(["query", "rank", "distance", "name", "mood", "effort", "budget", "one_pot", "strict_veg", "score"," reason"])
    for q in QUERIES:
        qt = (PREFIX if USE_PREFIX else "") + q
        res = col.query(
            query_embeddings=model.encode([qt], normalize_embeddings=True).tolist(),
            n_results=5,
            include=["metadatas", "distances"],
        )
        for i, (md, d) in enumerate(zip(res["metadatas"][0], res["distances"][0]), 1):
            w.writerow([q, i, round(d, 3), md["name"], md["mood"], md["effort"], md["budget"], md["one_pot"], md["strict_veg"], ""])
print("saved", f"eval_{RUN_NAME}.csv")