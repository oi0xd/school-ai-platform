import os
import requests
from dotenv import load_dotenv

load_dotenv()

ACCOUNT_ID = os.getenv("CLOUDFLARE_ACCOUNT_ID", "")
API_TOKEN = os.getenv("CLOUDFLARE_API_TOKEN", "")
WORKER_NAME = os.getenv("WORKER_NAME", "mahdi")
GROQ_KEY = os.getenv("GROQ_API_KEY", "")

# كود Groq بالمفتاح الجديد
worker_code = f"""
const GROQ_KEY = "{GROQ_KEY}";
const MODELS = ["openai/gpt-oss-120b", "openai/gpt-oss-20b"];

export default {{
  async fetch(request) {{
    const cors = {{ "Access-Control-Allow-Origin": "*", "Access-Control-Allow-Methods": "POST, OPTIONS", "Access-Control-Allow-Headers": "Content-Type" }};
    if (request.method === "OPTIONS") return new Response(null, {{ headers: cors }});
    if (request.method !== "POST") return new Response("Method Not Allowed", {{ status: 405, headers: cors }});
    try {{
      const body = await request.json();
      const prompt = body && body.prompt;
      if (!prompt) return new Response(JSON.stringify({{ error: "missing prompt" }}), {{ status: 400, headers: {{ ...cors, "Content-Type": "application/json" }} }});
      
      let lastErr = null;
      for (const model of MODELS) {{
        try {{
          const gRes = await fetch("https://api.groq.com/openai/v1/chat/completions", {{
            method: "POST",
            headers: {{ "Content-Type": "application/json", "Authorization": "Bearer " + GROQ_KEY }},
            body: JSON.stringify({{ model: model, messages: [{{ role: "user", content: prompt }}], temperature: 0.5, max_tokens: 1500 }})
          }});
          const data = await gRes.json();
          if (gRes.ok && data.choices && data.choices[0].message.content) {{
            return new Response(JSON.stringify({{ text: data.choices[0].message.content }}), {{ headers: {{ ...cors, "Content-Type": "application/json" }} }});
          }}
          lastErr = {{ status: gRes.status, detail: data }};
        }} catch (e) {{ lastErr = e.message; }}
      }}
      return new Response(JSON.stringify({{ error: "all_failed", last: lastErr }}), {{ status: 200, headers: {{ ...cors, "Content-Type": "application/json" }} }});
    }} catch (e) {{
      return new Response(JSON.stringify({{ error: e.message }}), {{ status: 500, headers: {{ ...cors, "Content-Type": "application/json" }} }});
    }}
  }}
}};
"""

print("⏳ جاري رفع المفتاح الجديد إلى Cloudflare...")
url = f"https://api.cloudflare.com/client/v4/accounts/{ACCOUNT_ID}/workers/scripts/{WORKER_NAME}"
headers = {"Authorization": f"Bearer {API_TOKEN}"}
files = {
    'metadata': (None, '{"main_module":"worker.js","compatibility_date":"2025-01-01"}', 'application/json'),
    'worker.js': ('worker.js', worker_code, 'application/javascript+module')
}
response = requests.put(url, headers=headers, files=files)

if response.status_code == 200:
    print("✅ تم تفعيل Groq الجديد في Cloudflare بنجاح!")
else:
    print("❌ خطأ:", response.text)
