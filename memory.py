import json
import numpy as np
from sentence_transformers import SentenceTransformer

print("⏳ جاري تحميل نموذج الذكاء الاصطناعي...")
model = SentenceTransformer('sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2')

def build_memory(subject_name, input_txt, output_chunks, output_emb):
    print(f"\n⏳ جاري معالجة مادة: {subject_name}...")
    try:
        with open(input_txt, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(f"❌ لم يتم العثور على الملف: {input_txt}. تخطي...")
        return

    CHUNK_SIZE = 800
    OVERLAP = 200
    chunks = []
    start = 0
    n = len(text)
    while start < n:
        end = min(start + CHUNK_SIZE, n)
        chunk = text[start:end].strip()
        if len(chunk) > 50:
            chunks.append(chunk)
        if end >= n: break
        start = end - OVERLAP

    print(f"✅ تم تقطيع {subject_name} إلى {len(chunks)} قطعة.")
    embeddings = model.encode(chunks, show_progress_bar=True)

    np.save(output_emb, embeddings)
    with open(output_chunks, "w", encoding="utf-8") as f:
        json.dump(chunks, f, ensure_ascii=False)

    print(f"🎉 تم بناء ذاكرة {subject_name} بنجاح!")

if __name__ == "__main__":
    build_memory("الطبيعيات", "data/book_text_clean.txt", "chunks_physics.json", "embeddings_physics.npy")
    build_memory("الصيانة", "data/maintenance_text_clean.txt", "chunks_maintenance.json", "embeddings_maintenance.npy")
    build_memory("الشبكات", "data/networks_text_clean.txt", "chunks_networks.json", "embeddings_networks.npy")
    build_memory("التطبيقات", "data/applications_text_clean.txt", "chunks_applications.json", "embeddings_applications.npy")