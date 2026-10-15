import json, random, collections as C

m = json.load(open("data/meals_tagged.json", encoding="utf-8"))
ENUMS = {"effort": {"quick", "medium", "long"}, "budget": {"low", "medium", "high"},
         "spicy": {"none", "mild", "medium", "hot"}, "protein": {"low", "medium", "high"},
         "flavor": {"bland", "balanced", "bold"}}

bad = [x["name"] for x in m if any(x.get(k) not in v for k, v in ENUMS.items())
       or not isinstance(x.get("one_pot"), bool) or not isinstance(x.get("snack"), bool) or not x.get("mood")]
print(len(m), "dishes,", len(bad), "invalid:", bad)

for f in ["effort", "budget", "spicy", "protein", "flavor", "one_pot", "snack", "strict_veg", "has_egg"]:
    print(f, dict(C.Counter(x.get(f) for x in m)))
print("mood", dict(C.Counter(t for x in m for t in x.get("mood", []))))

print("\n-- review these tag groups --")
for label, f in [("hot", lambda x: x["spicy"] == "hot"), ("high protein", lambda x: x["protein"] == "high"), ("snack", lambda x: x["snack"])]:
    print(label, ":", [x["name"] for x in m if f(x)])

print("\n-- random sample --")
random.seed(1)
for x in random.sample(m, min(20, len(m))):
    print(f"{x['name']} -> {x['mood']} | {x['effort']} | {x['budget']} | one_pot={x['one_pot']} | {x['spicy']} {x['protein']} {x['flavor']} snack={x['snack']}")