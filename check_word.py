import pymupdf

print("⏳ جاري البحث عن كلمة 'الموائع' في ملف PDF...")
doc = pymupdf.open("data/book.pdf")
found = False

for i, page in enumerate(doc):
    t = page.get_text("text")
    if "الموائع" in t or "الموائـ" in t:
        print(f"✅ وُجدت 'الموائع' في الصفحة {i+1}")
        found = True

if not found:
    print("❌ لم يتم العثور على الكلمة. ربما الكلمة مشوهة في الـ PDF الأصلي.")