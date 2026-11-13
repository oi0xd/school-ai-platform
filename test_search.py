import json

with open("chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

for i in range(40, 46):
    print(f"========== القطعة {i} ==========")
    print(chunks[i])
    print("\n")