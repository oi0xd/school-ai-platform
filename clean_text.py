# -*- coding: utf-8 -*-
import re

def clean(text: str) -> str:
    # إزالة الرموز الغريبة التي قد يلتقطها الـ OCR بالخطأ
    text = re.sub(r"[^\u0600-\u06FF\u0020-\u007E\n،؛؟.()\-]", "", text)
    # إزالة المسافات الزائدة داخل السطر
    text = re.sub(r"[ \t]+", " ", text)
    # إزالة الأسطر الفارغة المتكررة
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text

print("⏳ جاري تنظيف نص الـ OCR...")

# نقرأ من ملف الـ OCR
with open("data/book_text_ocr.txt", "r", encoding="utf-8") as f:
    raw_text = f.read()

cleaned_text = clean(raw_text)

# نحفظ في الملف النظيف الذي سيقرأه memory.py
with open("data/book_text_clean.txt", "w", encoding="utf-8") as f:
    f.write(cleaned_text)

print("✅ تم حفظ النص المنظف في data/book_text_clean.txt")