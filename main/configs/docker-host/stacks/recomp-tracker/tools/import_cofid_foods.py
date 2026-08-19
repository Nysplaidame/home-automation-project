"""Curated import of common generic foods from UK CoFID 2021.

Download the official workbook from GOV.UK, run this script without --apply to
review additions, then use --apply to add only missing food names to a running
Recomp Tracker. Values are per 100g edible portion and retain CoFID metadata.
"""

import argparse
import json
import re
import sys
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pandas as pd


SOURCE = "UK CoFID 2021"

# Generic foods only: each description makes preparation state explicit. Do not
# substitute branded products for these entries; add a separate library item
# from that product's nutrition label instead.
FOODS = {
    "Legumes and plant proteins": [
        "Baked beans, canned in tomato sauce",
        "Beans, butter, canned, re-heated, drained",
        "Beans, cannellini, canned, re-heated, drained",
        "Beans, chick peas, canned, re-heated, drained",
        "Beans, edamame, frozen, boiled in unsalted water",
        "Beans, haricot, canned, re-heated, drained",
        "Beans, red kidney, canned in water, re-heated, drained",
        "Lentils, green and brown, whole, dried, boiled in unsalted water",
        "Lentils, red, split, dried, boiled in unsalted water",
        "Peas, split, dried, boiled in unsalted water",
        "Tempeh",
        "Tofu, soya bean, steamed",
        "Beans, aduki, whole, dried, boiled in unsalted water",
        "Beans, blackeye, whole, dried, boiled in unsalted water",
        "Beans, broad, whole, boiled in unsalted water",
        "Beans, butter, dried, boiled in unsalted water",
        "Beans, chick peas, Kabuli, whole, dried, boiled in unsalted water",
        "Beans, green, raw",
        "Beans, haricot, whole, dried, boiled in unsalted water",
        "Beans, mung, dahl, dried, boiled in unsalted water",
        "Beans, mung, whole, dried, boiled in unsalted water",
        "Beans, pinto, dried, boiled in unsalted water",
        "Beans, red kidney, dried, boiled in unsalted water",
        "Beans, runner, boiled in unsalted water",
        "Beans, soya, dried, boiled in unsalted water",
    ],
    "Vegetables": [
        "Asparagus, steamed",
        "Aubergine, raw",
        "Beans, green, boiled in unsalted water",
        "Beetroot, cooked in unsalted water",
        "Brussels sprouts, boiled in unsalted water",
        "Cabbage, green, boiled in unsalted water",
        "Cabbage, red, raw",
        "Carrots, old, boiled in unsalted water",
        "Carrots, old, raw",
        "Cauliflower, boiled in unsalted water",
        "Cauliflower, raw",
        "Celery, raw",
        "Courgette, raw",
        "Cucumber, raw, flesh and skin",
        "Leeks, boiled in unsalted water",
        "Lettuce, average, raw",
        "Mushrooms, white, raw",
        "Onions, raw",
        "Peppers, capsicum, green, raw",
        "Pepper, capsicum, red, raw",
        "Spinach, baby, raw",
        "Sweet potato, flesh only, boiled in unsalted water",
        "Sweetcorn kernels, canned in water, drained",
        "Swede, flesh only, boiled in unsalted water",
        "Tomatoes, canned, whole contents",
        "Tomatoes, standard, raw",
        "Artichoke, globe, base of leaves and heart, boiled in unsalted water",
        "Broccoli, purple sprouting, boiled in unsalted water",
        "Chard, Swiss, boiled in unsalted water",
        "Chard, Swiss, raw",
        "Curly kale, boiled in unsalted water",
        "Curly kale, raw",
        "Garlic, raw",
        "Ginger, fresh",
        "Leeks, raw",
        "Mushrooms, oyster, raw",
        "Okra, boiled in unsalted water",
        "Okra, raw",
        "Pak choi, steamed",
        "Parsnip, boiled in unsalted water",
        "Parsnip, raw",
        "Peas, frozen, boiled in unsalted water",
        "Radish, red, flesh and skin, raw",
        "Rocket, raw",
        "Spinach, mature, raw",
        "Spring onions, bulbs and tops, raw",
        "Squash, butternut, baked",
        "Tomatoes, cherry, raw",
        "Turnip, boiled in unsalted water",
        "Watercress, raw",
        "Yam, flesh only, boiled in unsalted water",
    ],
    "Fruit and berries": [
        "Apples, eating, raw, flesh and skin",
        "Apricots, raw, flesh and skin",
        "Avocado, Hass, flesh only",
        "Blackberries, raw",
        "Blueberries",
        "Cherries, flesh and skin, raw",
        "Cranberries",
        "Grapefruit, flesh only, raw",
        "Grapes, red",
        "Kiwi fruit, flesh only, raw",
        "Mangoes, ripe, flesh only, raw",
        "Melon, watermelon, flesh only",
        "Oranges, flesh only",
        "Peaches, raw, flesh and skin",
        "Pears, raw, flesh and skin",
        "Pineapple, flesh only, raw",
        "Plums, dessert, flesh and skin, raw",
        "Raspberries, raw",
        "Strawberries, raw",
        "Apples, eating, dried",
        "Blackcurrants, raw",
        "Dates, dried, flesh and skin",
        "Figs, whole green fruit, raw",
        "Figs, whole fruit, dried",
        "Lemons, peeled, flesh only",
        "Limes, flesh only",
        "Nectarines, flesh and skin, raw",
        "Papaya, flesh only, raw",
        "Passion fruit, flesh and pips",
        "Pomegranate, flesh and pips",
        "Raisins, dried",
        "Redcurrants, raw",
        "Sultanas",
        "Whitecurrants, raw",
    ],
    "Meat and eggs": [
        "Bacon rashers, back, fat trimmed, grilled",
        "Beef, mince, raw, extra lean",
        "Beef, mince, extra lean, stewed",
        "Beef, rump steak, grilled, lean only",
        "Beef, sirloin steak, grilled medium-rare, lean",
        "Chicken, breast, grilled without skin, meat only",
        "Chicken, drumsticks, roasted, meat only",
        "Chicken, thighs, casseroled, meat only, diced",
        "Duck, roasted, meat only",
        "Eggs, chicken, whole, boiled",
        "Ham, gammon joint, boiled",
        "Lamb, leg joint, roasted, lean",
        "Lamb, loin chops, grilled, lean",
        "Pork, fillet medallions, grilled lean",
        "Pork, loin steaks, grilled, lean",
        "Pork, mince, raw",
        "Sausages, pork, chilled, grilled",
        "Turkey, breast, fillet, grilled, meat only",
        "Beef, braising steak, braised, lean only",
        "Beef, fillet steak, grilled, lean",
        "Beef, mince, raw",
        "Chicken, breast, casseroled, meat only",
        "Chicken, breast, grilled with skin, meat only",
        "Chicken, thighs, casseroled, meat and skin",
        "Lamb, mince, raw",
        "Pork, loin medallions, raw, lean",
        "Pork, loin steaks, raw, lean",
        "Rabbit, stewed, meat only",
        "Turkey, dark meat, roasted",
        "Turkey, light meat, roasted",
        "Turkey, mince, stewed",
        "Veal, escalope, raw",
        "Venison, meat only, raw",
    ],
    "Fish and seafood": [
        "Cod, flesh only, baked",
        "Cod, flesh only, raw",
        "Haddock, flesh only, grilled",
        "Hake, flesh only, grilled",
        "Mackerel, flesh only, grilled",
        "Mussels, purchased cooked",
        "Plaice, flesh only, baked",
        "Pollock, Alaskan, flesh only, baked",
        "Prawns, king, purchased cooked",
        "Salmon, farmed, flesh only, baked",
        "Sardines, canned in tomato sauce, whole contents",
        "Trout, rainbow, flesh only, baked",
        "Tuna, canned in brine, drained",
        "Anchovies, canned in oil, drained",
        "Bass, sea, flesh only, baked",
        "Bream, Sea, raw",
        "Crab, white meat, purchased cooked",
        "Herring, flesh only, grilled",
        "Lobster, boiled",
        "Mussels, raw",
        "Prawns, king, grilled from raw",
        "Salmon, farmed, flesh only, raw",
        "Salmon, pink, canned in brine, drained",
        "Salmon, smoked (cold-smoked)",
        "Salmon, wild, baked",
        "Sardines, canned in brine, drained",
        "Sardines, canned in olive oil, drained",
        "Scallops, steamed",
        "Squid, raw",
        "Tilapia, raw",
        "Tuna, canned in sunflower oil, drained",
    ],
    "Dairy and cheese": [
        "Cheese, Brie, with outer rind removed",
        "Cheese, Camembert",
        "Cheese, Cheddar type, '30% less fat'",
        "Cheese, Cheddar, English",
        "Cheese, cottage, plain",
        "Cheese, cottage, plain, reduced fat",
        "Cheese, Feta",
        "Cheese, Halloumi",
        "Cheese, Mozzarella, fresh",
        "Cheese, Parmesan, fresh",
        "Cheese, Quark",
        "Cheese, Ricotta",
        "Cheese, spreadable, full fat, soft, white",
        "Milk, 1% fat, pasteurised",
        "Milk, semi-skimmed, pasteurised, average",
        "Milk, skimmed, pasteurised, average",
        "Milk, whole, pasteurised, average",
        "Yogurt, low fat, plain",
        "Butter, salted",
        "Cheese, Caerphilly",
        "Cheese, Danish blue",
        "Cheese, Double Gloucester",
        "Cheese, Edam",
        "Cheese, Emmental",
        "Cheese, Gouda",
        "Cheese, Gruyere",
        "Cheese, Paneer",
        "Cheese, Red Leicester",
        "Cheese, Stilton, blue",
        "Cheese, Wensleydale",
        "Milk, goats, pasteurised",
        "Yogurt, Greek style, fruit",
        "Yogurt, Greek style, plain",
    ],
    "Nuts and seeds": [
        "Almonds, whole kernels",
        "Brazil nuts, kernel only",
        "Cashew nuts, kernel only, plain",
        "Hazelnuts, kernel only",
        "Macadamia nuts, salted",
        "Peanuts, dry roasted",
        "Pecan nuts, kernel only",
        "Pistachio nuts, kernel only, roasted and salted",
        "Pumpkin seeds",
        "Sunflower seeds",
        "Walnuts, kernel only",
        "Almonds, flaked and ground",
        "Almonds, toasted",
        "Cashew nuts, kernel only, roasted and salted",
        "Coconut, desiccated",
        "Coconut, flesh only, fresh",
        "Peanut butter, smooth",
        "Peanuts, kernel only, plain, unsalted",
        "Sesame seeds",
    ],
    "Staples and grains": [
        "Barley, pearl, boiled",
        "Bread, white, average",
        "Pasta, white, dried, boiled in unsalted water",
        "Pasta, wholewheat, spaghetti, dried, boiled in unsalted water",
        "Porridge oats, unfortified",
        "Quinoa, raw",
        "Rice, brown, basmati, boiled in unsalted water",
        "Rice, white, basmati, boiled in unsalted water",
        "Rice, white, long grain, boiled in unsalted water",
        "Wheat, bulgur, raw",
        "Bagels, plain",
        "Bread, brown, average",
        "Bread, ciabatta",
        "Bread, pitta, white",
        "Bread, seeded",
        "Breakfast cereal, bran flakes, fortified",
        "Breakfast cereal, cornflakes, fortified",
        "Breakfast cereal, wheat biscuits, Weetabix type, fortified",
        "Buckwheat, groats",
        "Couscous, plain, cooked",
        "Muesli, Swiss style, no added sugar or salt, unfortified",
        "Noodles, egg, fine, dried, boiled in unsalted water",
        "Noodles, rice, fine, dried, boiled in unsalted water",
        "Pasta, white, spaghetti, dried, boiled in unsalted water",
        "Pasta, white, twists, fusilli, dried, boiled in salted water",
        "Polenta, hydrated, raw",
        "Porridge oats, unfortified, cooked, made up with semi-skimmed milk",
        "Rice, brown, wholegrain, boiled in unsalted water",
        "Rice, Thai fragrant, boiled in unsalted water",
        "Rice, ready-cooked, \"plain\", re-heated",
        "Tortilla, wheat, soft",
    ],
}


def canonical(value):
    return re.sub(r"\s+", " ", str(value).strip().lower())


def number(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("workbook")
    parser.add_argument("--url", default="http://192.168.20.102:8420")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    table = pd.read_excel(args.workbook, sheet_name="1.3 Proximates", skiprows=[1, 2])
    table["_key"] = table["Food Name"].map(canonical)
    lookup = table.set_index("_key", drop=False)
    with urlopen(args.url.rstrip("/") + "/api/kv/food-library", timeout=15) as response:
        record = json.load(response)
    foods = json.loads(record["value"])
    items = foods.setdefault("items", [])
    existing = {canonical(item.get("name")) for item in items}

    additions, missing, skipped = [], [], []
    for category, names in FOODS.items():
        for source_name in names:
            key = canonical(source_name)
            if key not in lookup.index:
                missing.append(source_name)
                continue
            row = lookup.loc[key]
            if canonical(row["Food Name"]) in existing:
                skipped.append(row["Food Name"])
                continue
            additions.append({
                "id": "cofid-2021-" + str(row["Food Code"]).replace(" ", "").lower(),
                "name": row["Food Name"],
                "calories": number(row["Energy (kcal) (kcal)"]),
                "protein": number(row["Protein (g)"]),
                "carbs": number(row["Carbohydrate (g)"]),
                "fat": number(row["Fat (g)"]),
                "archived": False,
                "category": category,
                "source": SOURCE,
                "sourceFoodCode": str(row["Food Code"]),
                "sourceFoodName": row["Food Name"],
            })
            existing.add(canonical(row["Food Name"]))

    report = {"existing": len(items), "additions": len(additions), "skipped": skipped, "missing": missing}
    print(json.dumps(report, indent=2))
    if missing:
        sys.exit("Refusing to apply: review missing CoFID source names first.")
    if not args.apply:
        return
    items.extend(additions)
    payload = json.dumps({"value": json.dumps(foods), "expectedVersion": record["version"]}).encode("utf-8")
    request = Request(args.url.rstrip("/") + "/api/kv/food-library", data=payload, method="PUT", headers={"Content-Type": "application/json"})
    try:
        with urlopen(request, timeout=20):
            pass
    except HTTPError as error:
        raise SystemExit("Food library was not changed: HTTP {}. Refresh and retry if another device edited it.".format(error.code)) from error
    print("Applied {} food-library additions.".format(len(additions)))


if __name__ == "__main__":
    main()
