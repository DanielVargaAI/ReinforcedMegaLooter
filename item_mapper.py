"""
map item (snipped) IDs (image id) to item types (ordered index in item-list) and rarities
as long as the items.json is uptodate, this always creates a correct mapping
"""
import os
import json

# for every item in items.json, map its ID to its type and rarity
with open("items.json", "r") as f:
    items_data = json.load(f)
item_mapper = {}

for item in items_data.keys():
    old_id = int(item)
    for rarity in range(0, 9):
        new_id = old_id + rarity * 45 + 8 * 45 * (old_id // 45)
        if items_data[item]["name"] == "Unknown Item":
            actual_rarity = 0
        elif "Essential" in items_data[item]["set"]:
            actual_rarity = 9
        else:
            actual_rarity = rarity
        item_mapper[new_id] = {
            "type": old_id if items_data[item]["name"] != "Unknown Item" else 191,
            "rarity": actual_rarity
        }

# sort item_mapper by keys
item_mapper = dict(sorted(item_mapper.items()))

# redo all keys of item_mapper to be an ongoing index starting from 0
item_mapper_indexed = {}
for index, key in enumerate(item_mapper.keys()):
    item_mapper_indexed[index] = item_mapper[key]
item_mapper = item_mapper_indexed

# save item_mapper to item_mapper.json
with open("item_mapper.json", "w") as f:
    json.dump(item_mapper, f, indent=4)
