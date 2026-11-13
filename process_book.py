import pymupdf
import pytesseract
from PIL import Image
import io
import re
import sys

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

if len(sys.argv) < 2:
    print("⚠️ يرجى تحديد اسم الملف. مثال: python process_book.py networks")
    sys.exit()

book_name = sys.argv[1]
PDF_FILE = f"data/{book_name}.pdf"
OUT_FILE = f"data/{book_name}_text_clean.txt"

print(f"⏳ جاري استخراج النص من {PDF_FILE} بالـ OCR...")
doc = pymupdf.open(PDF_FILE)
pages_text = []

for i, page in enumerate(doc):
    pix = page.get_pixmap(dpi=300)
    img = Image.open(io.BytesIO(pix.tobytes("png")))
    text = pytesseract.image_to_string(img, lang="ara")
    pages_text.append(text)
    print(f"✅ صفحة {i+1}/{len(doc)}")

full_text = "\n\n".join(pages_text)

print("⏳ جاري تنظيف النص...")
def clean(text: str) -> str:
    text = re.sub(r"[^\u0600-\u06FF\u0020-\u007E\n،؛؟.()\-]", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text

cleaned_text = clean(full_text)
with open(OUT_FILE, "w", encoding="utf-8") as f:
    f.write(cleaned_text)

print(f"🎉 اكتمل! تم إنشاء: {OUT_FILE}")