import requests

print("⏳ جاري إرسال السؤال إلى الخادم...")

# رابط الخادم المحلي
url = "http://127.0.0.1:8000/ask"

# السؤال الذي نريد اختباره
payload = {
    "question": "ما هو تعريف الموائع؟"
}

try:
    # إرسال الطلب
    response = requests.post(url, json=payload)
    
    print(f"✅ رمز الحالة: {response.status_code}")
    print("📝 رد الخادم:")
    print(response.json())

except Exception as e:
    print(f"❌ حدث خطأ: {e}")