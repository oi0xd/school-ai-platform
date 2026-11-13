# -*- coding: utf-8 -*-
import pymupdf
import pytesseract
from PIL import Image
import io
import time

# مسار برنامج Tesseract (تأكد أنه صحيح)
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

PDF_FILE = "data/book.pdf"
OUT_FILE = "data/book_text_ocr.txt"

print("⏳ جاري فتح ملف الـ PDF...")
doc = pymupdf.open(PDF_FILE)
total_pages = len(doc)
print(f"📚 عدد الصفحات: {total_pages}")
print("⚠️ قد تستغرق هذه العملية وقتاً طويلاً، يرجى الانتظار...\n")

pages_text = []
start_time = time.time()

for i in range(total_pages):
    page = doc[i]
    
    # تحويل الصفحة إلى صورة بدقة 300 DPI (ضروري لوضوح العربية)
    pix = page.get_pixmap(dpi=300)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    
    # قراءة النص بالعربية
    text = pytesseract.image_to_string(img, lang="ara")
    
    pages_text.append(f"--- صفحة {i+1} ---\n{text}")
    
    # طباعة التقدم كل 5 صفحات
    if (i + 1) % 5 == 0 or (i + 1) == total_pages:
        elapsed = int(time.time() - start_time)
        print(f"✅ تمت قراءة {i+1}/{total_pages} صفحة (الوقت المنقضي: {elapsed} ثانية)")

# حفظ النص الكامل
with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write("\n\n".join(pages_text))

print(f"\n🎉 اكتمل! النص محفوظ في {OUT_FILE}")