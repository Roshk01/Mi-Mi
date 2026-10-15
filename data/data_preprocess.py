import json, os, time
from urllib.request import urlopen, Request
from urllib.error import HTTPError

try:
    from dotenv import load_dotenv
except ModuleNotFoundError:
    def load_dotenv(*args, **kwargs):
        return False

load_dotenv()

N = None  # test size; set to None to tag everything
MODEL = "qwen/qwen3.8-27b"
SRC, OUT = "data/meals_final.json", "data/meals_tagged.json"
MOODS = ["comfort", "stress-relief", "rainy-day", "healthy", "light", "celebration"]
ENUMS = {"effort": {"quick", "medium", "long"}, "budget": {"low", "medium", "high"},
         "spicy": {"none", "mild", "medium", "hot"}, "protein": {"low", "medium", "high"},
         "flavor": {"bland", "balanced", "bold"}}
FIELDS = ["mood", "effort", "budget", "one_pot", "spicy", "protein", "flavor", "snack"]

def valid(t):
    return (all(t.get(k) in v for k, v in ENUMS.items())
            and isinstance(t.get("one_pot"), bool) and isinstance(t.get("snack"), bool)
            and isinstance(t.get("mood"), list) and 1 <= len(t["mood"]) <= 3
            and all(x in MOODS for x in t["mood"]))

def tag(m):
    prompt = f"""Tag this dish. Reply with JSON only: {{"mood": [1-3 from {MOODS}], "effort": "quick|medium|long", "budget": "low|medium|high", "one_pot": true/false, "spicy": "none|mild|medium|hot", "protein": "low|medium|high", "flavor": "bland|balanced|bold", "snack": true/false}}
effort: quick = under 20 min, medium = 20-45 min, long = over 45 min. budget = typical home-cooking ingredient cost. one_pot = cooked in a single pot/pan.
protein = high only if meat, fish, egg, paneer, tofu, lentils or beans are a main ingredient. snack = true only for small bites eaten between meals.
Dish: {m['name']} ({m['country']}, {m['category']})
Ingredients: {', '.join(i['name'] for i in m['ingredients'])}
Steps: {m['steps'][:600]}"""
    body = json.dumps({"model": MODEL, "temperature": 0, "response_format": {"type": "json_object"},
                       "messages": [{"role": "user", "content": prompt}]}).encode()
    req = Request("https://api.groq.com/openai/v1/chat/completions", body,
                  {"Authorization": f"Bearer {os.environ['groq_api']}", "Content-Type": "application/json", "User-Agent": "meal-tagger/1.0"})
    for _ in range(6):
        try:
            with urlopen(req, timeout=30) as r:
                t = json.loads(json.load(r)["choices"][0]["message"]["content"])
            if valid(t):
                return t
            print("  invalid tags, retrying")
        except HTTPError as e:
            if e.code != 429: raise
            wait = float(e.headers.get("retry-after", 20)) + 1
            print(f"  429, waiting {wait:.0f}s"); time.sleep(wait)
    return None

meals = json.load(open(SRC, encoding="utf-8"))
if os.path.exists(OUT):  # keep tags you already checked
    old = {m["id"]: m for m in json.load(open(OUT, encoding="utf-8"))}
    for m in meals:
        for k in FIELDS:
            if k in old.get(m["id"], {}): m[k] = old[m["id"]][k]

todo = [m for m in meals if not all(k in m for k in FIELDS)]
if N: todo = todo[:N]
print(len(meals) - len(todo), "done,", len(todo), "to go")

for k, m in enumerate(todo, 1):
    t = tag(m)
    if not t:
        print("gave up on", m["name"], "- rerun later"); continue
    for f in FIELDS: m.setdefault(f, t[f])  # only fills missing fields
    json.dump(meals, open(OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
    print(f"{k}/{len(todo)} {m['name']} | {m['mood']} {m['effort']} {m['budget']} {m['one_pot']} | {m['spicy']} {m['protein']} {m['flavor']} snack={m['snack']}")
    time.sleep(5)