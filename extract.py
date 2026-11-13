import fitz
import os

print("⏳ جاري فتح الملف واستخراج النص...")

# اسم ملف الـ PDF الذي سنضعه لاحقاً
pdf_path = "data/book.pdf"

try:
    doc = fitz.open(pdf_path)
    full_text = ""
    
    for page_num in range(len(doc)):
        page = doc.load_page(page_num)
        text = page.get_text("text")
        full_text += f"\n--- صفحة {page_num + 1} ---\n" + text
        
    output_path = "data/book_text.txt"
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(full_text)
        
    print(f"✅ تمت العملية بنجاح! النص موجود في {output_path}")
    
except Exception as e:
    print(f"❌ حدث خطأ: {e}")
    print("تأكد من أن ملف الـ PDF موجود في مجلد data وأن اسمه book.pdf")