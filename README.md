# Mi Mi: Your Personal Cooking Partner

A funny cooking partner that knows you. Tell it your mood, time, budget or the ingredients you have, and it suggests dishes from **your own curated dataset**. It is built as a RAG pipeline (embeddings + vector DB + LLM) that stays grounded in real dishes instead of inventing them.

## The problem

Deciding what to cook is tiring. Food apps are endless scrolls, generic chatbots forget what you like, and the result is instant noodles again.

## What makes it different

- **Your dishes, your rules:** a personal exclusion list (beef, crab, shellfish, sourdough, sweet breakfasts, raw fish) is applied before anything is indexed.
- **Grounded answers:** the LLM only talks about dishes the retriever found, never invented ones.
- **Tagged for how you actually decide:** mood, effort, budget, one-pot, spice level, protein, flavor, snack.
- **Evaluated, not eyeballed:** a fixed 16-query test set with hand scoring, so every change is measured against a baseline.

## How it works

```
question
  -> bge-small-en-v1.5 embeds the question
  -> ChromaDB finds the closest dishes
  -> Groq LLM writes a short, funny, grounded reply as Mi Mi
```

## Tech stack

| Part | Tool |
|---|---|
| Language | Python |
| Recipe source | TheMealDB API |
| Tagging | Groq LLM, JSON output validated against fixed value lists |
| Embeddings | `sentence-transformers`, `BAAI/bge-small-en-v1.5` |
| Vector DB | ChromaDB (persistent, cosine distance) |
| Answer layer | Groq, `openai/gpt-oss-120b` |
| Evaluation | `pandas`, hand-scored CSVs |

## Data pipeline

| File | Job |
|---|---|
| `data_extract.py` | Pulls recipes from TheMealDB (chicken, seafood, vegetarian, sides, lamb, breakfast, pasta, plus soups by name). Collapses the 20 ingredient fields into one list, computes diet flags (meat, fish, egg, strict veg) from ingredients because the source's "Vegetarian" label is unreliable, and removes dishes with excluded foods. |
| `data_preprocessing.py` | Tags every dish with Groq: `mood`, `effort`, `budget`, `one_pot`, `spicy`, `protein`, `flavor`, `snack`. Validates every tag, retries on rate limits, resumes where it stopped, and never overwrites tags you already checked. |
| `data_analyse.py` | Validates the tagged data, prints tag counts and a random sample for spot-checking. |
| `embedding_db.py` | Embeds every dish and stores it in ChromaDB with tags as filterable metadata. |
| `query.py` | Retrieves the closest dishes and asks Groq to answer as Mi Mi. |
| `eval.py` | Runs the fixed test queries and saves the top 5 per query to CSV for scoring. |

## Setup

```bash
git clone https://github.com/Roshk01/<repo-name>.git
cd <repo-name>
pip install chromadb sentence-transformers groq python-dotenv pandas
```

Create a `.env` file with your Groq key:

```
GROQ_API_KEY=your_key_here
```

## Run

```bash
python data_extract.py && python data_preprocessing.py && python data_analyse.py
python embedding_db.py
python query.py
```

## Evaluation

A fixed set of 16 queries (mood, effort, budget, pantry ingredients, cuisine, diet, "surprise me"). For each query I mark how many of the top 5 results I would actually cook, and note why each miss happened.

**Baseline: 3.94 / 5** (63 of 80 results usable). The misses came from:

- effort and one-pot rules ignored by pure semantic search
- pantry queries ("I have spaghetti, tomato and cheese") returning dishes that don't use those ingredients
- no snack dishes in the data yet
- "surprise me" cannot be answered by similarity search

Every enhancement is rerun on the same queries and kept only if the score improves.

## Roadmap

- [x] Data extraction, cleaning, diet flags and exclusions
- [x] LLM tagging with validation (mood, effort, budget, one-pot, spice, protein, flavor, snack)
- [x] Vector DB and retrieval baseline
- [x] Groq answer layer with the Mi Mi personality
- [x] Evaluation set and baseline score
- [ ] Query-to-filters: turn "one pot, quick, no eggs" into hard filters
- [ ] Pantry matching with ingredient swaps (never a completely different dish)
- [ ] Surprise mode
- [ ] Streamlit board to add dishes, auto-tag them and keep a cooking log (date, rating, note)
- [ ] Agent features: signature-dish reminders, weekend planner with grocery list
- [ ] Voice mode: speech-to-text, spoken replies, step-by-step cooking mode with timers
- [ ] Optional ML layer: personality fine-tune or a preference model trained on my ratings
