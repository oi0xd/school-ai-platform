FROM python:3.10-slim

WORKDIR /app

# تهيئة مسار الكاش لـ Hugging Face لتفادي مشاكل الصلاحيات في Spaces
ENV HF_HOME=/tmp/huggingface
ENV TRANSFORMERS_CACHE=/tmp/huggingface

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod -R 777 /app

EXPOSE 7860

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
