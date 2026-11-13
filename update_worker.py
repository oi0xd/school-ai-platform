import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")
WORKER_NAME = os.getenv("WORKER_NAME", "mahdi")
GEMINI_KEY = os.getenv("GEMINI_KEY", "")

# الكود الجديد للـ Worker (يعتمد على Gemini)
worker_code = f"""
const GEMINI_KEY = "{GEMINI_KEY}";

export default {{
  async fetch(request) {{
    const cors = {{
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "POST, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type"
    }};
    if (request.method === "OPTIONS") return new Response(null, {{ headers: cors }});
    if (request.method !== "POST") return new Response("Method Not Allowed", {{ status: 405, headers: cors }});
    
    try {{
      const body = await request.json();
      const prompt = body && body.prompt;
      if (!prompt) return new Response(JSON.stringify({{ error: "missing prompt" }}), {{ status: 400, headers: {{ ...cors, "Content-Type": "application/json" }} }});
      
      const url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent";
      
      const gRes = await fetch(url, {{
        method: "POST",
        headers: {{ "Content-Type": "application/json", "x-goog-api-key": GEMINI_KEY }},
        body: JSON.stringify({{
          contents: [{{ parts: [{{ text: prompt }}] }}],
          generationConfig: {{ temperature: 0.5, maxOutputTokens: 1500 }}
        }})
      }});
      
      const data = await gRes.json();
      
      if (!gRes.ok) {{
        return new Response(JSON.stringify({{ error: "google_error", status: gRes.status, detail: data }}), {{ status: 200, headers: {{ ...cors, "Content-Type": "application/json" }} }});
      }}
      
      const text = data.candidates && data.candidates[0] && data.candidates[0].content && data.candidates[0].content.parts && data.candidates[0].content.parts[0].text;
      
      return new Response(JSON.stringify({{ text: text || "رد فارغ" }}), {{ headers: {{ ...cors, "Content-Type": "application/json" }} }});
      
    }} catch (e) {{
      return new Response(JSON.stringify({{ error: e.message }}), {{ status: 500, headers: {{ ...cors, "Content-Type": "application/json" }} }});
    }}
  }}
}};
"""

print("⏳ جاري تحديث Cloudflare Worker...")

# نستخدم واجهة برمجة التطبيقات (API) الخاصة بـ Cloudflare لرفع الكود
url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/workers/scripts/{WORKER_NAME}"

headers = {
    "Authorization": f"Bearer {API_TOKEN}",
}

# تجهيز البيانات للإرسال
files = {
    'metadata': (None, '{"main_module":"worker.js","compatibility_date":"2025-01-01"}', 'application/json'),
    'worker.js': ('worker.js', worker_code, 'application/javascript+module')
}

response = requests.put(url, headers=headers, files=files)

if response.status_code == 200:
    print("✅ تم تحديث البروكسي بنجاح! أصبح جاهزاً للاتصال بجوجل.")
else:
    print("❌ حدث خطأ أثناء التحديث:", response.text)
