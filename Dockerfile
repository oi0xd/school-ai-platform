FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# المنصة تحدد المنفذ عبر متغير البيئة PORT
ENV PORT=7860
EXPOSE 7860

# قراءة المنفذ من متغير البيئة
CMD ["sh", "-c", "uvicorn main:app --host 0.0.0.0 --port ${PORT}"]
