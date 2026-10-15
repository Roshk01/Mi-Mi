import os
import chromadb # pyright: ignore[reportMissingImports]
from groq import Groq # pyright: ignore[reportMissingImports]
from sentence_transformers import SentenceTransformer # pyright: ignore[reportMissingImports]
from dotenv import load_dotenv # pyright: ignore[reportMissingImports]

load_dotenv()
groq_api_key = os.environ.get("groq_api")

PREFIX = "Represent this sentence for searching relevant passages: "

model = SentenceTransformer("BAAI/bge-small-en-v1.5")
col = chromadb.PersistentClient(path="chroma_db").get_collection("meals")
llm = Groq(api_key=groq_api_key)

SYSTEM = (
    "You are Mi Mi, a funny, warm cooking partner. "
    "Suggest ONLY from the dishes provided. Never invent dishes or ingredients. "
    "Pick the best 3, give each one a one-line funny reason tied to the user's request, "
    "and keep the whole reply short."
    "Joke style: warm and teasing, never insult a dish. Max one pun per reply. Tie each joke to the user's mood or situation."
)

def retrieve(q, effort=("quick", "medium"), n=5):
    res = col.query(
        query_embeddings=model.encode([PREFIX + q], normalize_embeddings=True).tolist(),
        n_results=n,
        where={"effort": {"$in": list(effort)}},
        include=["documents", "metadatas"],
    )
    return res["documents"][0]

def ask(q):
    dishes = "\n".join(f"- {d}" for d in retrieve(q))
    r = llm.chat.completions.create(
        model="openai/gpt-oss-120b",
        messages=[
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": f"Request: {q}\n\nDishes:\n{dishes}"},
        ],
        temperature=0.7,
    )
    return r.choices[0].message.content

if __name__ == "__main__":
    print(ask("cozy meal for rainy day with low effort, i am tired"))