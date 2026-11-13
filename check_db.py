import json

print("⏳ جاري فحص الذاكرة (chunks.json)...")
with open("chunks.json", "r", encoding="utf-8") as f:
    chunks = json.load(f)

found = False
for i, c in enumerate(chunks):
    if "الموائ" in c or "الضغط" in c:
        print(f"\n✅ وُجدت الكلمة في القطعة رقم {i}:")
        print(c[:300] + "...\n")
        found = True
        break # نكتفي بأول نتيجة

if not found:
    print("\n❌ لم يتم العثور على 'الموائع' أو 'الضغط' في الذاكرة! يبدو أن صفحة 30 لم يتم استخراجها بشكل صحيح.")