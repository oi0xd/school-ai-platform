# -*- coding: utf-8 -*-
import json
import re
import numpy as np
import os
import requests
from dotenv import load_dotenv

# تحميل المتغيرات البيئية من ملف .env
load_dotenv()
os.environ.setdefault("HF_HOME", "/tmp/huggingface")
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
import onnxruntime as ort
from huggingface_hub import hf_hub_download
from tokenizers import Tokenizer

app = FastAPI(title="منصة المواد الذكية")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# قراءة المتغيرات البيئية بأمان
PROXY_URL   = os.getenv("PROXY_URL", "https://mahdi.higivv77vv.workers.dev")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

TOP_K          = 5
SEMANTIC_W     = 0.7
KEYWORD_W      = 0.3
BOOST          = 0.15 
REFUSAL_THRESH = 0.15 
NEIGHBOR_WINDOW = 1

STOP_WORDS = {
    "ما", "هو", "هي", "هل", "من", "في", "على", "عن", "الى", "الي", "إلى",
    "تعريف", "اشرح", "وضح", "اذكر", "ماذا", "كيف", "لماذا", "ال",
    "و", "او", "أو", "ثم", "هذا", "هذه", "ذلك", "تلك", "بما", "لما",
    "ب", "ل", "يوجد", "توجد", "الموجود", "الموجودة",
}

print("⏳ جاري تحميل النموذج والذاكرة...")
class ONNXEmbedder:
    def __init__(self, repo_id="oi0xd/rag-embed-onnx"):
        print("⏳ تحميل نموذج ONNX...")
        model_path = hf_hub_download(repo_id=repo_id, filename="model.onnx")
        tokenizer_path = hf_hub_download(repo_id=repo_id, filename="tokenizer.json")
        
        self.session = ort.InferenceSession(model_path, providers=["CPUExecutionProvider"])
        self.tokenizer = Tokenizer.from_file(tokenizer_path)
        self.tokenizer.enable_truncation(max_length=128)
        self.tokenizer.enable_padding()

    def encode(self, texts):
        encodings = self.tokenizer.encode_batch(texts)
        input_ids = np.array([e.ids for e in encodings], dtype=np.int64)
        attention_mask = np.array([e.attention_mask for e in encodings], dtype=np.int64)
        token_type_ids = np.array([e.type_ids for e in encodings], dtype=np.int64)
        
        inputs = {"input_ids": input_ids, "attention_mask": attention_mask, "token_type_ids": token_type_ids}
        input_names = [i.name for i in self.session.get_inputs()]
        inputs = {k: v for k, v in inputs.items() if k in input_names}

        outputs = self.session.run(None, inputs)[0]
        
        mask = np.expand_dims(attention_mask, -1).astype(np.float32)
        summed = np.sum(outputs * mask, axis=1)
        counted = np.clip(np.sum(mask, axis=1), 1e-9, None)
        embeddings = summed / counted

        embeddings = embeddings / np.clip(np.linalg.norm(embeddings, axis=1, keepdims=True), 1e-9, None)
        return embeddings

EMBED_MODEL = ONNXEmbedder("oi0xd/rag-embed-onnx")

# قاموس لتخزين بيانات كل مادة
SUBJECTS = {}

def load_subject(name, chunks_file, emb_file):
    try:
        with open(chunks_file, "r", encoding="utf-8") as f:
            chunks = json.load(f)
        embeddings = np.load(emb_file)
        
        norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
        norms[norms == 0] = 1
        embeddings_n = embeddings / norms
        
        SUBJECTS[name] = {"chunks": chunks, "embeddings_n": embeddings_n}
        print(f"✅ تم تحميل مادة: {name} ({len(chunks)} قطعة)")
    except Exception as e:
        print(f"⚠️ تعذر تحميل مادة {name}: {e}")

# تحميل المواد الأربعة
load_subject("physics", "chunks_physics.json", "embeddings_physics.npy")
load_subject("maintenance", "chunks_maintenance.json", "embeddings_maintenance.npy")
load_subject("networks", "chunks_networks.json", "embeddings_networks.npy")
load_subject("applications", "chunks_applications.json", "embeddings_applications.npy")

# أسماء المواد بالعربية (للاستخدام في الـ Prompt)
SUBJECT_NAMES_AR = {
    "physics": "الطبيعيات",
    "maintenance": "صيانة الحاسوب",
    "networks": "شبكات الحاسوب",
    "applications": "التطبيقات"
}

def semantic_scores(query: str, embeddings_n: np.ndarray) -> np.ndarray:
    q = EMBED_MODEL.encode([query])[0].astype(np.float32)
    q = q / (np.linalg.norm(q) + 1e-9)
    return embeddings_n @ q

def normalize_ar(text: str) -> str:
    text = re.sub(r"[\u064B-\u0652\u0670\u0640]", "", text)
    text = re.sub(r"[\u0622\u0623\u0625]", "\u0627", text)
    text = text.replace("\u0629", "\u0647")
    text = text.replace("\u0649", "\u064A")
    text = re.sub(r"\s+", " ", text)
    return text.strip()

def tokenize(text: str) -> set:
    text = normalize_ar(text)
    words = re.findall(r"[\u0621-\u064A]+", text) 
    result = set()
    for w in words:
        if w in STOP_WORDS: continue
        if w.startswith("ال") and len(w) > 4: w = w[2:]
        if len(w) > 2: result.add(w)
    return result

def query_variants(query: str) -> set:
    q_words = tokenize(query)
    variants = set()
    for w in q_words:
        variants.add(w)
        if len(w) >= 4:
            variants.add(w.replace("ئ", "ي"))
            variants.add(w.replace("ئ", "ى"))
            variants.add(w.replace("ئ", "ا"))
    return variants

def keyword_scores(query: str, chunks: list) -> np.ndarray:
    q_variants = query_variants(query)
    if not q_variants: return np.zeros(len(chunks))

    normalized_chunks = [normalize_ar(ch) for ch in chunks]
    scores = np.zeros(len(chunks))
    
    for i, ch_norm in enumerate(normalized_chunks):
        hits = 0
        for qw in q_variants:
            if re.search(r"\b" + re.escape(qw) + r"\b", ch_norm) or (len(qw) >= 4 and qw in ch_norm):
                hits += 1
        if hits > 0: scores[i] = hits / len(q_variants)

    if scores.max() > 0: scores = scores / scores.max()
    return scores

def hybrid_retrieve(query: str, subject_data: dict):
    chunks = subject_data["chunks"]
    embeddings_n = subject_data["embeddings_n"]
    
    sem = semantic_scores(query, embeddings_n)
    kw  = keyword_scores(query, chunks)
    hybrid = SEMANTIC_W * sem + KEYWORD_W * kw
    hybrid = hybrid + BOOST * (kw > 0)

    top_idx = np.argsort(hybrid)[::-1][:TOP_K]
    return [
        {"index": int(i), "score": float(hybrid[i])}
        for i in top_idx
    ]

def expand_with_neighbors(results: list, chunks: list) -> list:
    expanded = set()
    for r in results:
        i = r["index"]
        for j in range(i - NEIGHBOR_WINDOW, i + NEIGHBOR_WINDOW + 1):
            if 0 <= j < len(chunks):
                expanded.add(j)
    core = {r["index"] for r in results}
    return [{"index": j, "is_core": j in core, "text": chunks[j]} for j in sorted(expanded)]

def ask_llm(query: str, context_blocks: list, subject_name: str) -> str:
    context_text = "\n\n".join(
        ("★ " if b["is_core"] else "  ") + f"[مقطع {b['index']}]\n{b['text']}"
        for b in context_blocks
    )

    system_prompt = (
        f"أنت مساعد علمي متخصص في مادة ({subject_name}). أجب من السياق المرفق فقط.\n"
        "1. إذا طلب الطالب (تعريف) ولم تجد جملة صريحة، فاستنتج التعريف من الخواص المذكورة.\n"
        "2. إذا لم تجد أي معلومة ذات صلة، اكتب: لا يوجد في المنهج\n\n"
        f"السياق:\n{context_text}"
    )

    resp = requests.post(
        PROXY_URL,
        headers={"Content-Type": "application/json"},
        json={"prompt": f"{system_prompt}\n\nالسؤال: {query}"},
        timeout=120,
    )
    resp.raise_for_status()
    return resp.json()["text"]

class AskRequest(BaseModel):
    question: str
    subject: str = "physics"

@app.post("/ask")
def ask(req: AskRequest):
    query = req.question.strip()
    if not query: return {"error": "لا يوجد سؤال"}

    if req.subject not in SUBJECTS:
        return {"answer": "المادة المطلوبة غير متوفرة حالياً.", "context_used": []}

    subject_data = SUBJECTS[req.subject]
    subject_name_ar = SUBJECT_NAMES_AR.get(req.subject, req.subject)

    results = hybrid_retrieve(query, subject_data)
    best_score = results[0]["score"] if results else 0.0

    if best_score < REFUSAL_THRESH:
        return {"answer": "لا يوجد في المنهج", "context_used": []}

    blocks = expand_with_neighbors(results, subject_data["chunks"])
    answer = ask_llm(query, blocks, subject_name_ar)

    return {"answer": answer, "context_used": blocks}

@app.get("/")
def read_root():
    return FileResponse("index.html")