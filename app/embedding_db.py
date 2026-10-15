import json
import chromadb  # pyright: ignore[reportMissingImports]
from sentence_transformers import SentenceTransformer  # pyright: ignore[reportMissingImports]

with open(r"data\meals_tagged.json", encoding="utf-8") as f:
    meals = json.load(f)
model = SentenceTransformer("BAAI/bge-small-en-v1.5")

client = chromadb.PersistentClient(path="chroma_db")
col = client.get_or_create_collection("meals",metadata = {"hnsw:space":"cosine"})

docs = [f"{m['name']}. {m['country']} {m['category']} dish. Mood: {', '.join(m['mood'])}. Effort: {m['effort']}. Budget: {m['budget']}. Ingredients: {', '.join(i['name'] for i in m['ingredients'])}" for m in meals]
metas = [{"name": m["name"], "country": m["country"], "category": m["category"], "mood": ",".join(m["mood"]), "effort": m["effort"], "budget": m["budget"], "one_pot": m["one_pot"], "strict_veg": m["strict_veg"]} for m in meals]

col.upsert(
    ids=[m["id"] for m in meals],
    documents=docs,
    metadatas=metas,
    embeddings=model.encode(docs, normalize_embeddings=True).tolist()
)

q = "Represent this sentence for searching relevant passages: I need a dish which is quick but include chicken and has to be suitable for a celebration."
res = col.query(
    query_embeddings=model.encode([q], normalize_embeddings=True).tolist(),
    n_results=5,
    where={"effort": {"$in": ["quick", "medium"]}},
    include=["metadatas", "distances"]
)

for md in res["metadatas"][0]:
    print(md["name"], "|", md["mood"], md["effort"], md["budget"])