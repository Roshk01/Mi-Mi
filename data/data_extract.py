import json, os, random
from urllib.request import urlopen
from urllib.parse import quote

BASE = "https://www.themealdb.com/api/json/v1/1"
OUT = "data/meals_final.json"
CATS = ["Chicken", "Seafood", "Vegetarian", "Side", "Lamb", "Breakfast", "Pasta"]
SOUP_WORDS = ["soup", "chowder", "broth", "bisque"]
CAP = 40
random.seed(42)

MEAT = ["chicken", "beef", "lamb", "pork", "bacon", "ham", "sausage", "mutton", "turkey", "duck", "gelatin"]
FISH = ["fish", "salmon", "tuna", "prawn", "shrimp", "anchov", "cod", "squid", "mussel", "clam", "crab", "oyster", "sardine", "haddock", "mackerel", "trout", "worcestershire"]
EXCLUDE = {
    "beef": ["beef", "veal"], "crab": ["crab"], "jellyfish": ["jellyfish"],
    "shellfish": ["clam", "mussel", "oyster", "scallop", "cockle", "whelk", "periwinkle", "abalone", "conch"],
    "sourdough": ["sourdough"], "raw fish": ["sushi", "sashimi", "ceviche"],
}
SWEET = ["sugar", "syrup", "honey", "chocolate", "maple", "jam", "nutella", "cinnamon", "banana", "blueberr", "strawberr", "vanilla", "custard"]
KEEP_SAVORY = {"Smoked Haddock Kedgeree", "Breakfast Potatoes"}

def get_json(url):
    with urlopen(url, timeout=10) as r:
        return json.load(r)

def clean(m):
    ings = [{"name": m[f"strIngredient{n}"].strip().lower(), "qty": (m.get(f"strMeasure{n}") or "").strip()}
            for n in range(1, 21) if (m.get(f"strIngredient{n}") or "").strip()]
    names = " ".join(i["name"] for i in ings) + " " + m["strMeal"].lower()
    has_meat = any(w in names for w in MEAT)
    has_fish = any(w in names for w in FISH)
    why = [k for k, ws in EXCLUDE.items() if any(w in names for w in ws)]
    if m["strCategory"] == "Breakfast" and m["strMeal"] not in KEEP_SAVORY and any(w in names for w in SWEET):
        why.append("sweet breakfast")
    return {
        "id": m["idMeal"], "name": m["strMeal"], "category": m["strCategory"], "country": m["strArea"],
        "tags": [t for t in (m["strTags"] or "").split(",") if t],
        "ingredients": ings, "steps": m["strInstructions"], "image": m["strMealThumb"],
        "has_meat": has_meat, "has_fish": has_fish, "has_egg": "egg" in names,
        "strict_veg": not (has_meat or has_fish), "excluded_reasons": why,
    }

ids = {}
for c in CATS:
    items = get_json(f"{BASE}/filter.php?c={c}")["meals"] or []
    for m in random.sample(items, min(CAP, len(items))):
        ids[m["idMeal"]] = None

raw = {i: get_json(f"{BASE}/lookup.php?i={i}")["meals"][0] for i in ids}
for kw in SOUP_WORDS:
    for m in get_json(f"{BASE}/search.php?s={quote(kw)}")["meals"] or []:
        raw[m["idMeal"]] = m

meals = [clean(m) for m in raw.values()]
final = [m for m in meals if not m["excluded_reasons"]]
os.makedirs("data", exist_ok=True)
json.dump(final, open(OUT, "w", encoding="utf-8"), indent=2, ensure_ascii=False)
print(len(raw), "fetched,", len(meals) - len(final), "excluded,", len(final), "final")