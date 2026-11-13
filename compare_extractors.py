# -*- coding: utf-8 -*-
import pymupdf
import os

PDF_FILE = "data/book.pdf"
PAGE_NUM = 13  # صفحة 14 (لأن العد يبدأ من 0)

print("⏳ جاري فحص الصفحة...")

if not os.path.exists(PDF_FILE):
    print(f"❌ لم يتم العثور على الملف {PDF_FILE}")
else:
    doc = pymupdf.open(PDF_FILE)
    page = doc[PAGE_NUM]
    
    # الطريقة 1: النص العادي
    pymupdf_text = page.get_text("text")
    
    # الطريقة 2: استخدام rawdict (تحكم أدق)
    raw_dict = page.get_text("rawdict")
    
    print("=" * 60)
    print("طريقة 1 (text):")
    print("=" * 60)
    print(pymupdf_text[:1500])
    
    print("\n" + "=" * 60)
    print("طريقة 2 (rawdict) - أول 500 حرف:")
    print("=" * 60)
    # استخراج النص من القاموس المعقد
    raw_text = ""
    for block in raw_dict.get("blocks", []):
        if "lines" in block:
            for line in block["lines"]:
                for span in line["spans"]:
                    raw_text += span["text"]
    
    print(raw_text[:500])