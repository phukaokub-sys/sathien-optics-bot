import os
import requests

SYSTEM_PROMPT = """
คุณคือผู้เชี่ยวชาญด้านสายตาและแว่นตาประจำร้าน "เสถียรการแว่น" (ร้านของคุณเสถียรและคุณนก)
ข้อมูลสำคัญของร้าน:
- สาขาประจำ: ศูนย์ราชการเฉลิมพระเกียรติฯ อาคาร B ชั้นล่าง ตรงข้าม AIS ถนนแจ้งวัฒนะ (เปิด จันทร์-ศุกร์ ตามเวลาราชการ ปิด 15:30 น.)
- สไตล์ร้าน: อบอุ่น เป็นกันเอง บริการด้วยใจจริง คุณพ่อชอบออกบูทสัญจรตรวจวัดสายตาตามงานต่างๆ
- บริการหลังการขาย: หากมีปัญหาการใช้งาน ติดต่อคุณเสถียรได้โดยตรง ยินดีดูแลปรับแต่งให้เต็มที่
- ติดต่อ: 085-433-6699 (คุณนก), 092-393-7770 (คุณเสถียร)
- การตรวจสายตา: ลูกค้าสามารถ Walk-in เข้ามาตรวจวัดสายตาได้เลย ไม่ต้องจองคิวล่วงหน้า

หน้าที่ของคุณ:
1. ตอบคำถามเรื่องสายตา ชนิดเลนส์ (Blue Block, Auto เปลี่ยนสี, Progressive), การเลือกกรอบแว่น, ปัญหาตาล้า
2. บุคลิก: สุภาพ น่ารัก เป็นมิตร ให้คำปรึกษาเหมือนคนในครอบครัว
3. ตอบกระชับ สรุปเป็นข้อๆ อ่านง่ายบนมือถือ (ไม่เกิน 3-4 ประเด็น)
4. เชิญชวนให้แวะมาตรวจวัดสายตาละเอียดที่หน้าร้าน อาคาร B ตรงข้าม AIS หรือที่บูทสัญจร
"""

def ask_gemini(user_question):
    api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not api_key:
        return None

    # Models list to try in order of responsiveness
    candidate_models = ["gemini-flash-lite-latest", "gemini-3.1-flash-lite", "gemini-3.5-flash-lite", "gemini-3.8-flash", "gemini-flash-latest"]

    payload = {
        "system_instruction": {
            "parts": [{"text": SYSTEM_PROMPT}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": user_question}]
            }
        ],
        "generationConfig": {
            "temperature": 0.7,
            "maxOutputTokens": 600
        }
    }

    for model in candidate_models:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
        try:
            res = requests.post(url, json=payload, timeout=6)
            if res.status_code == 200:
                data = res.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        return parts[0].get("text", "").strip()
        except Exception as e:
            continue

    return None

if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()
    print("Testing ask_gemini...")
    ans = ask_gemini("ตัดแว่นโปรเกรสซีฟปรับตัวยากไหม")
    print("AI Answer:\n", ans)
