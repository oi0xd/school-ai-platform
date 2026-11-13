from main import keyword_scores, CHUNKS, query_variants
import numpy as np

query = "ما هو تعريف الموائع؟"
print(f"🔍 كلمات البحث المولدة: {query_variants(query)}\n")

scores = keyword_scores(query)

# نطبع أفضل 5 قطع بناءً على البحث بالكلمات المفتاحية فقط
top_idx = np.argsort(scores)[::-1][:5]
print("🎯 أفضل 5 قطع بالبحث المفتاحي:")
for i in top_idx:
    if scores[i] > 0:
        print(f"\n--- القطعة {i} (النتيجة: {scores[i]}) ---")
        print(CHUNKS[i][:200] + "...")