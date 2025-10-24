"""
read items.json
collect all values
save values with same order but new ids to items.json
"""
import json
import os
with open("items.json", "r") as f:
    items_data = json.load(f)
all_values = list(items_data.values())
new_items = {}
for i in range(len(all_values)):
    new_item = all_values[i]
    new_items[i] = new_item
with open("items.json", "w") as f:
    json.dump(new_items, f, indent=4)
