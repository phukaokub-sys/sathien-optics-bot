import os
import json
import re
from functools import wraps
from datetime import timedelta
from dotenv import load_dotenv
from flask import Flask, request, abort, render_template, redirect, url_for, jsonify, send_file, session

from linebot.v3 import WebhookHandler
from linebot.v3.exceptions import InvalidSignatureError
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
    MessagingApi,
    ReplyMessageRequest,
    PushMessageRequest,
    TextMessage,
    FlexMessage,
    FlexContainer
)
from linebot.v3.webhooks import (
    MessageEvent,
    TextMessageContent,
    FollowEvent
)

import database
from ai_advisor import ask_gemini

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "sathien_secret_key_2026_optics_super_secure")
app.permanent_session_lifetime = timedelta(days=30)
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "sathien2026").strip()

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get("admin_logged_in"):
            return redirect(url_for("admin_login", next=request.url))
        return f(*args, **kwargs)
    return decorated_function

# Initialize database
database.init_db()

CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET", "").strip()
CHANNEL_ACCESS_TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", "").strip()

handler = WebhookHandler(CHANNEL_SECRET)

def get_messaging_api():
    token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", CHANNEL_ACCESS_TOKEN).strip()
    config = Configuration(access_token=token)
    api_client = ApiClient(config)
    return MessagingApi(api_client)

# ==========================================
# FLEX MESSAGE BUILDERS (Labels <= 20 Chars)
# ==========================================

def get_store_location_flex():
    bubble_json = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#059669",
            "contents": [
                {"type": "text", "text": "🏢 เสถียรการแว่น (ร้านหลัก)", "weight": "bold", "color": "#D1FAE5", "size": "md"},
                {"type": "text", "text": "ศูนย์ราชการ อาคาร B", "weight": "bold", "color": "#FFFFFF", "size": "xl", "margin": "xs"}
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "xs",
                    "contents": [
                        {"type": "text", "text": "📍 พิกัดร้านในอาคาร:", "size": "sm", "color": "#059669", "weight": "bold"},
                        {"type": "text", "text": "ชั้นล่าง (ตรงข้าม AIS)", "size": "md", "weight": "bold", "color": "#111111"},
                        {"type": "text", "text": "ศูนย์ราชการเฉลิมพระเกียรติฯ อาคาร B ถ.แจ้งวัฒนะ", "size": "xs", "color": "#555555", "wrap": True}
                    ]
                },
                {"type": "separator"},
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "xs",
                    "contents": [
                        {"type": "text", "text": "⏰ เวลาทำการ:", "size": "sm", "color": "#059669", "weight": "bold"},
                        {"type": "text", "text": "จันทร์ - ศุกร์ ตามเวลาราชการ", "size": "sm", "color": "#333333"},
                        {"type": "text", "text": "(ทางร้านปิดทำการเวลา 15:30 น.)", "size": "sm", "color": "#E11D48", "weight": "bold"}
                    ]
                },
                {"type": "separator"},
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "xs",
                    "contents": [
                        {"type": "text", "text": "📞 เบอร์ติดต่อ:", "size": "sm", "color": "#059669", "weight": "bold"},
                        {"type": "text", "text": "• 085-433-6699 (คุณนก)", "size": "sm", "color": "#111111"},
                        {"type": "text", "text": "• 092-393-7770 (คุณเสถียร)", "size": "sm", "color": "#111111"}
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#059669",
                    "action": {
                        "type": "uri",
                        "label": "🗺️ เปิด Google Maps",
                        "uri": "https://maps.app.goo.gl/RWCdTXF3HJiSskis9"
                    }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "action": {
                        "type": "uri",
                        "label": "📞 โทรหาคุณนก",
                        "uri": "tel:0854336699"
                    }
                }
            ]
        }
    }
    return FlexMessage(alt_text="แผนที่ร้าน เสถียรการแว่น ศูนย์ราชการ อาคาร B", contents=FlexContainer.from_json(json.dumps(bubble_json)))


def get_booth_location_flex():
    schedules = database.get_active_schedules()
    schedule_boxes = []

    if schedules:
        for s in schedules:
            schedule_boxes.append({
                "type": "box",
                "layout": "vertical",
                "backgroundColor": "#FFF7ED",
                "cornerRadius": "md",
                "paddingAll": "md",
                "borderColor": "#FDBA74",
                "borderWidth": "light",
                "contents": [
                    {"type": "text", "text": f"📅 {s['date_range']}", "size": "sm", "weight": "bold", "color": "#EA580C"},
                    {"type": "text", "text": s['location'], "size": "sm", "weight": "bold", "color": "#1E293B", "wrap": True, "margin": "xs"},
                    {"type": "text", "text": s['note'] if s['note'] else "บริการตรวจวัดสายตาและตัดประกอบแว่น", "size": "xs", "color": "#64748B", "wrap": True, "margin": "xs"}
                ]
            })
    else:
        schedule_boxes.append({
            "type": "text",
            "text": "ช่วงนี้คุณพ่อประจำอยู่ที่ร้านหลัก ศูนย์ราชการ อาคาร B ครับ",
            "size": "sm",
            "color": "#475569"
        })

    bubble_json = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#EA580C",
            "contents": [
                {"type": "text", "text": "🎪 เสถียรการแว่น สัญจร", "weight": "bold", "color": "#FFEDD5", "size": "md"},
                {"type": "text", "text": "พิกัดออกบูทของคุณพ่อ", "weight": "bold", "color": "#FFFFFF", "size": "xl", "margin": "xs"}
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {"type": "text", "text": "ตารางออกบูทตรวจวัดสายตาและตัดแว่น:", "size": "xs", "color": "#888888", "weight": "bold"},
                *schedule_boxes,
                {"type": "text", "text": "📞 โทรเช็กพิกัดหน้างานได้โดยตรงเลยครับ", "size": "xs", "color": "#EA580C", "weight": "bold"}
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#EA580C",
                    "action": {
                        "type": "uri",
                        "label": "📞 โทรหาคุณเสถียร",
                        "uri": "tel:0923937770"
                    }
                }
            ]
        }
    }
    return FlexMessage(alt_text="พิกัดออกบูท เสถียรการแว่น", contents=FlexContainer.from_json(json.dumps(bubble_json)))


BASE_URL = os.getenv("BASE_URL", "https://sathien-optics-bot.onrender.com").rstrip("/")

def get_tracking_flex(order=None, user_id=""):
    if order:
        status_color = "#10B981" if "เสร็จ" in order['status'] or "จัดส่ง" in order['status'] else "#F59E0B"
        bubble_json = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": "#2563EB",
                "contents": [
                    {"type": "text", "text": "📦 ข้อมูลออเดอร์แว่นตา", "weight": "bold", "color": "#DBEAFE", "size": "md"},
                    {"type": "text", "text": order['order_no'], "weight": "bold", "color": "#FFFFFF", "size": "lg", "margin": "xs"}
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "md",
                "contents": [
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "ชื่อผู้รับ:", "size": "xs", "color": "#888888"},
                            {"type": "text", "text": order['customer_name'], "size": "sm", "weight": "bold", "color": "#111111"}
                        ]
                    },
                    {
                        "type": "box",
                        "layout": "vertical",
                        "contents": [
                            {"type": "text", "text": "สถานะปัจจุบัน:", "size": "xs", "color": "#888888"},
                            {"type": "text", "text": order['status'], "size": "md", "weight": "bold", "color": status_color}
                        ]
                    },
                    *(
                        [{
                            "type": "box",
                            "layout": "vertical",
                            "contents": [
                                {"type": "text", "text": "เลขพัสดุ Flash Express:", "size": "xs", "color": "#888888"},
                                {"type": "text", "text": order['tracking_no'], "size": "sm", "weight": "bold", "color": "#2563EB"}
                            ]
                        }] if order.get('tracking_no') else []
                    ),
                    {"type": "separator"},
                    {"type": "text", "text": f"ที่อยู่จัดส่ง: {order['address']}", "size": "xs", "color": "#666666", "wrap": True}
                ]
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "contents": [
                    {
                        "type": "button",
                        "style": "secondary",
                        "action": {
                            "type": "uri",
                            "label": "📞 โทรหาคุณนก",
                            "uri": "tel:0854336699"
                        }
                    }
                ]
            }
        }
        return FlexMessage(alt_text=f"สถานะออเดอร์ {order['order_no']}", contents=FlexContainer.from_json(json.dumps(bubble_json)))

    # Default order tracking menu
    address_url = f"{BASE_URL}/form/address"
    if user_id:
        address_url += f"?userId={user_id}"

    bubble_json = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#2563EB",
            "contents": [
                {"type": "text", "text": "🚚 จัดส่งแว่นตาถึงบ้าน", "weight": "bold", "color": "#DBEAFE", "size": "md"},
                {"type": "text", "text": "ติดตามแว่น / กรอกที่อยู่", "weight": "bold", "color": "#FFFFFF", "size": "xl", "margin": "xs"}
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "1. แตะปุ่ม 'กรอกที่อยู่จัดส่ง' ด้านล่าง เพื่อให้ร้านจัดส่งแว่นให้ถึงบ้านฟรีครับ",
                    "size": "sm",
                    "color": "#334155",
                    "wrap": True
                },
                {"type": "separator"},
                {
                    "type": "text",
                    "text": "2. หากต้องการเช็กสถานะ เพียงพิมพ์ 'เบอร์โทรศัพท์' ของคุณในแชทนี้ ระบบจะดึงสถานะให้ทันทีครับ 👓",
                    "size": "sm",
                    "color": "#2563EB",
                    "weight": "bold",
                    "wrap": True
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#2563EB",
                    "action": {
                        "type": "uri",
                        "label": "📝 กรอกที่อยู่จัดส่ง",
                        "uri": address_url
                    }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "action": {
                        "type": "uri",
                        "label": "📞 โทรหาคุณนก",
                        "uri": "tel:0854336699"
                    }
                }
            ]
        }
    }
    return FlexMessage(alt_text="ติดตามแว่นตาและพัสดุ เสถียรการแว่น", contents=FlexContainer.from_json(json.dumps(bubble_json)))


# BASE_URL is defined above as os.getenv("BASE_URL", "https://sathien-optics-bot.onrender.com")

def build_prescription_bubble(rx, base_url=BASE_URL):
    p_name = rx.get("patient_name") or rx.get("customer_name") or "คุณลูกค้า"
    relation = rx.get("relation") or "เจ้าของบัญชี"
    exam_date = rx.get("exam_date") or "-"
    sph_r = rx.get("sph_r") or "-"
    cyl_r = rx.get("cyl_r") or "-"
    axis_r = rx.get("axis_r") or "-"
    add_r = rx.get("add_r") or "-"
    sph_l = rx.get("sph_l") or "-"
    cyl_l = rx.get("cyl_l") or "-"
    axis_l = rx.get("axis_l") or "-"
    add_l = rx.get("add_l") or "-"
    pd = rx.get("pd") or "-"
    notes = rx.get("notes") or ""
    image_url = rx.get("image_url") or ""

    r_details = f"สั้น/ยาว: {sph_r} | เอียง: {cyl_r}"
    if axis_r and axis_r != "-":
        r_details += f" | องศา: {axis_r}°"
    if add_r and add_r != "-":
        r_details += f" | ADD: {add_r}"

    l_details = f"สั้น/ยาว: {sph_l} | เอียง: {cyl_l}"
    if axis_l and axis_l != "-":
        l_details += f" | องศา: {axis_l}°"
    if add_l and add_l != "-":
        l_details += f" | ADD: {add_l}"

    bubble = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#6D28D9",
            "paddingAll": "lg",
            "contents": [
                {"type": "text", "text": f"👓 สมาชิก: {relation}", "weight": "bold", "size": "xs", "color": "#DDD6FE"},
                {"type": "text", "text": f"{p_name}", "weight": "bold", "size": "xl", "color": "#FFFFFF", "margin": "xs"},
                {"type": "text", "text": f"📅 ตรวจวัดเมื่อ: {exam_date}", "size": "xs", "color": "#EDE9FE", "margin": "xs"}
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#F8FAFC",
                    "cornerRadius": "md",
                    "paddingAll": "md",
                    "contents": [
                        {"type": "text", "text": "👁️ ตาขวา (R / OD)", "weight": "bold", "size": "sm", "color": "#1E293B"},
                        {"type": "text", "text": r_details, "size": "xs", "color": "#475569", "margin": "xs", "wrap": True},
                        {"type": "separator", "margin": "sm"},
                        {"type": "text", "text": "👁️ ตาซ้าย (L / OS)", "weight": "bold", "size": "sm", "color": "#1E293B", "margin": "sm"},
                        {"type": "text", "text": l_details, "size": "xs", "color": "#475569", "margin": "xs", "wrap": True},
                        {"type": "separator", "margin": "sm"},
                        {"type": "text", "text": f"📏 ระยะตาดำ (PD): {pd}", "weight": "bold", "size": "xs", "color": "#0284C7", "margin": "sm"}
                    ]
                }
            ]
        }
    }

    if notes:
        bubble["body"]["contents"].append({
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#FAF5FF",
            "cornerRadius": "md",
            "paddingAll": "sm",
            "contents": [
                {"type": "text", "text": f"📝 หมายเหตุเลนส์: {notes}", "size": "xs", "color": "#6D28D9", "wrap": True}
            ]
        })

    if image_url and image_url.startswith("http"):
        bubble["hero"] = {
            "type": "image",
            "url": image_url,
            "size": "full",
            "aspectRatio": "16:9",
            "aspectMode": "cover",
            "action": {
                "type": "uri",
                "label": "ดูสลิปเต็ม",
                "uri": image_url
            }
        }

    footer_buttons = []
    if image_url and image_url.startswith("http"):
        footer_buttons.append({
            "type": "button",
            "style": "secondary",
            "height": "sm",
            "action": {
                "type": "uri",
                "label": "🔎 ดูรูปสลิปเต็ม",
                "uri": image_url
            }
        })

    consult_text = f"สนใจตัดแว่นของ {p_name}"[:20]
    footer_buttons.append({
        "type": "button",
        "style": "primary",
        "color": "#7C3AED",
        "height": "sm",
        "action": {
            "type": "message",
            "label": "💬 ปรึกษาตัดแว่นซ้ำ",
            "text": consult_text
        }
    })
    footer_buttons.append({
        "type": "button",
        "style": "link",
        "height": "sm",
        "action": {
            "type": "uri",
            "label": "📞 โทรหาคุณเสถียร",
            "uri": "tel:0923937770"
        }
    })

    bubble["footer"] = {
        "type": "box",
        "layout": "vertical",
        "spacing": "sm",
        "contents": footer_buttons
    }

    return bubble

def get_promotion_flex():
    promos = database.get_active_promotions()
    if not promos:
        return TextMessage(text="โปรโมชั่นตัดแว่นพิเศษ เสถียรการแว่น:\n• กรอบพร้อมเลนส์เริ่มต้น 990.-\n• เลนส์กรองแสงบลู 1,490.-\n• เลนส์เปลี่ยนสี Auto 1,990.-\n• เลนส์โปรเกรสซีฟ 3,500.-\n\nสอบถามเพิ่มเติมโทร: 085-433-6699 (คุณนก) หรือ 092-393-7770 (คุณเสถียร) ได้เลยครับ 👓")

    bubbles = []
    for p in promos[:10]:
        title = p.get("title", "ชุดตัดแว่น")
        price = p.get("price", "990")
        tag = p.get("tag", "🔥 โปรสุดคุ้ม")
        color = p.get("color", "#EA580C")
        raw_details = p.get("details", "")

        detail_lines = [d.strip() for d in raw_details.split("\n") if d.strip()]
        body_contents = []
        for line in detail_lines:
            body_contents.append({
                "type": "text",
                "text": line,
                "size": "xs",
                "color": "#334155",
                "wrap": True
            })

        bubble = {
            "type": "bubble",
            "header": {
                "type": "box",
                "layout": "vertical",
                "backgroundColor": color,
                "paddingAll": "lg",
                "contents": [
                    {"type": "text", "text": tag, "weight": "bold", "size": "xs", "color": "#FEF08A"},
                    {"type": "text", "text": title, "weight": "bold", "size": "xl", "color": "#FFFFFF", "margin": "xs"},
                    {"type": "text", "text": f"฿ {price}.- (กรอบพร้อมเลนส์)", "weight": "bold", "size": "lg", "color": "#FEF08A", "margin": "xs"}
                ]
            },
            "body": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": body_contents
            },
            "footer": {
                "type": "box",
                "layout": "vertical",
                "spacing": "sm",
                "contents": [
                    {
                        "type": "button",
                        "style": "primary",
                        "color": color,
                        "height": "sm",
                        "action": {
                            "type": "message",
                            "label": "💬 สั่งตัด / ปรึกษาคุณนก",
                            "text": f"สนใจ{title} {price}บ."[:20]
                        }
                    },
                    {
                        "type": "button",
                        "style": "secondary",
                        "height": "sm",
                        "action": {
                            "type": "uri",
                            "label": "📍 พิกัดร้าน อาคาร B",
                            "uri": "https://maps.app.goo.gl/RWCdTXF3HJiSskis9"
                        }
                    }
                ]
            }
        }
        bubbles.append(bubble)

    carousel_json = {
        "type": "carousel",
        "contents": bubbles
    }
    return FlexMessage(alt_text="โปรโมชั่นตัดแว่นสุดคุ้ม เสถียรการแว่น", contents=FlexContainer.from_json(json.dumps(carousel_json)))

def get_prescription_flex(user_id=None, phone=None):
    bubble_json = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#7C3AED",
            "contents": [
                {"type": "text", "text": "👓 เสถียรการแว่น", "weight": "bold", "color": "#DDD6FE", "size": "sm"},
                {"type": "text", "text": "ขอประวัติ & สลิปสายตา", "weight": "bold", "color": "#FFFFFF", "size": "xl", "margin": "xs"}
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "📄 ต้องการรูปสลิปผลวัดสายตาคอมพิวเตอร์ หรือเช็คค่าสายตาเดิม:",
                    "size": "sm",
                    "color": "#1E293B",
                    "weight": "bold",
                    "wrap": True
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#FAF5FF",
                    "cornerRadius": "md",
                    "paddingAll": "md",
                    "contents": [
                        {"type": "text", "text": "💬 สะดวก รวดเร็ว ช่างส่งรูปให้ตรงๆ:", "size": "xs", "weight": "bold", "color": "#7C3AED"},
                        {"type": "text", "text": "เพียงพิมพ์แจ้งชื่อ หรือ เบอร์โทร ทิ้งไว้ในแชทนี้ได้เลยครับ ทางร้านจะค้นใบประวัติและถ่ายรูปสลิปส่งให้ในแชทนี้ทันทีครับ 😊", "size": "xs", "color": "#6D28D9", "wrap": True, "margin": "xs"}
                    ]
                },
                {
                    "type": "text",
                    "text": "🏬 หรือแวะมาตรวจวัดสายตาใหม่ฟรีด้วยระบบคอมพิวเตอร์ได้ที่ ศูนย์ราชการ อาคาร B ชั้นล่าง ตรงข้าม AIS ครับ",
                    "size": "xs",
                    "color": "#64748B",
                    "wrap": True
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#7C3AED",
                    "height": "sm",
                    "action": {
                        "type": "uri",
                        "label": "📞 โทรหาคุณนก",
                        "uri": "tel:0854336699"
                    }
                },
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                        "type": "uri",
                        "label": "📞 โทรหาคุณเสถียร",
                        "uri": "tel:0923937770"
                    }
                }
            ]
        }
    }
    return FlexMessage(alt_text="ขอประวัติสลิปสายตา เสถียรการแว่น", contents=FlexContainer.from_json(json.dumps(bubble_json)))


def get_service_care_flex():
    bubble_json = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#DB2777",
            "contents": [
                {"type": "text", "text": "🛠️ เสถียรการแว่น ใส่ใจดูแล", "weight": "bold", "color": "#FCE7F3", "size": "md"},
                {"type": "text", "text": "บริการหลังการขาย", "weight": "bold", "color": "#FFFFFF", "size": "xl", "margin": "xs"}
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "ทางร้านเสถียรการแว่นยินดีดูแลคุณลูกค้าทุกท่านด้วยใจจริงครับ 😊",
                    "size": "sm",
                    "color": "#1E293B",
                    "weight": "bold",
                    "wrap": True
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#FDF2F8",
                    "cornerRadius": "lg",
                    "paddingAll": "md",
                    "borderColor": "#FBCFE8",
                    "borderWidth": "light",
                    "contents": [
                        {"type": "text", "text": "👓 หากแว่นตามีปัญหาการใช้งาน:", "size": "sm", "weight": "bold", "color": "#BE185D"},
                        {"type": "text", "text": "• แว่นหลวม ไม่กระชับรูปหน้า\n• ใส่แล้วไม่สบายตา หรือแป้นจมูกหลุด\n• สามารถติดต่อ 'คุณเสถียร' ได้โดยตรงเลยครับ ทางร้านยินดีปรับแต่งและดูแลให้เต็มที่ครับ", "size": "xs", "color": "#374151", "wrap": True, "margin": "xs"}
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#DB2777",
                    "action": {
                        "type": "uri",
                        "label": "📞 โทรหาคุณเสถียร",
                        "uri": "tel:0923937770"
                    }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "action": {
                        "type": "uri",
                        "label": "📞 โทรหาคุณนก",
                        "uri": "tel:0854336699"
                    }
                }
            ]
        }
    }
    return FlexMessage(alt_text="บริการหลังการขาย เสถียรการแว่น", contents=FlexContainer.from_json(json.dumps(bubble_json)))


def get_contact_flex():
    bubble_json = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#E11D48",
            "contents": [
                {"type": "text", "text": "📞 ติดต่อร้านเสถียรการแว่น", "weight": "bold", "color": "#FFE4E6", "size": "md"},
                {"type": "text", "text": "ยินดีให้บริการทุกท่านครับ", "weight": "bold", "color": "#FFFFFF", "size": "xl", "margin": "xs"}
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {"type": "text", "text": "สามารถโทรติดต่อสอบถามได้ที่เบอร์:", "size": "xs", "color": "#475569"},
                {"type": "text", "text": "• คุณนก: 085-433-6699", "size": "md", "weight": "bold", "color": "#1E293B"},
                {"type": "text", "text": "• คุณเสถียร: 092-393-7770", "size": "md", "weight": "bold", "color": "#1E293B"},
                {"type": "text", "text": "หรือพิมพ์ข้อความทิ้งไว้ในแชทนี้ได้เลยครับ", "size": "xs", "color": "#64748B", "margin": "sm"}
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#E11D48",
                    "action": {
                        "type": "uri",
                        "label": "📞 โทรหาคุณนก",
                        "uri": "tel:0854336699"
                    }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "action": {
                        "type": "uri",
                        "label": "📞 โทรหาคุณเสถียร",
                        "uri": "tel:0923937770"
                    }
                }
            ]
        }
    }
    return FlexMessage(alt_text="เบอร์โทรติดต่อ เสถียรการแว่น", contents=FlexContainer.from_json(json.dumps(bubble_json)))


def get_appointment_flex():
    bubble_json = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#059669",
            "contents": [
                {"type": "text", "text": "👓 เสถียรการแว่น", "weight": "bold", "color": "#D1FAE5", "size": "md"},
                {"type": "text", "text": "นัดตรวจวัดสายตาละเอียด", "weight": "bold", "color": "#FFFFFF", "size": "xl", "margin": "xs"}
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "contents": [
                {
                    "type": "text",
                    "text": "คุณลูกค้าสามารถ Walk-in เข้ามาตรวจวัดสายตาได้เลย ไม่ต้องจองคิวล่วงหน้าครับ! 😊",
                    "weight": "bold",
                    "size": "sm",
                    "color": "#1E293B",
                    "wrap": True
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#ECFDF5",
                    "cornerRadius": "lg",
                    "paddingAll": "md",
                    "borderColor": "#A7F3D0",
                    "borderWidth": "light",
                    "contents": [
                        {"type": "text", "text": "📍 พิกัดหน้าร้านหลัก:", "size": "xs", "weight": "bold", "color": "#065F46"},
                        {"type": "text", "text": "ชั้นล่าง อาคาร B (ตรงข้าม AIS) ศูนย์ราชการเฉลิมพระเกียรติฯ ถ.แจ้งวัฒนะ", "size": "xs", "color": "#333333", "wrap": True, "margin": "xs"},
                        {"type": "text", "text": "⏰ เวลาทำการ: จันทร์ - ศุกร์ 08:30 - 15:30 น.", "size": "xs", "color": "#059669", "weight": "bold", "margin": "xs"}
                    ]
                },
                {
                    "type": "text",
                    "text": "📞 สอบถามหรือแจ้งเวลาก่อนเข้ามาได้ที่:\n• 085-433-6699 (คุณนก)\n• 092-393-7770 (คุณเสถียร)",
                    "size": "xs",
                    "color": "#475569",
                    "wrap": True
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#059669",
                    "action": {
                        "type": "uri",
                        "label": "🗺️ เปิด Google Maps",
                        "uri": "https://maps.app.goo.gl/RWCdTXF3HJiSskis9"
                    }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "action": {
                        "type": "uri",
                        "label": "📞 โทรหาคุณนก",
                        "uri": "tel:0854336699"
                    }
                }
            ]
        }
    }
    return FlexMessage(alt_text="นัดตรวจวัดสายตา เสถียรการแว่น", contents=FlexContainer.from_json(json.dumps(bubble_json)))


def get_reply_for_text(user_msg, user_id=""):
    # Record user active state
    if user_id:
        database.record_line_user(user_id)

    msg_lower = user_msg.lower()

    # 1. Check if user typed a phone number (8-10 digits) to track order
    clean_digits = re.sub(r"[^0-9]", "", user_msg)
    if len(clean_digits) in [9, 10]:
        if user_id:
            database.link_user_phone(clean_digits, user_id)
        order = database.get_order_by_phone(clean_digits)
        if order:
            return get_tracking_flex(order, user_id)
        else:
            return TextMessage(text=f"ไม่พบข้อมูลออเดอร์ของเบอร์ {clean_digits} ในระบบครับ\n\nหากคุณลูกค้าสั่งตัดไว้ที่บูทหรือหน้าร้าน สามารถพิมพ์สอบถามแอดมิน หรือโทรติดต่อได้ที่:\n• 085-433-6699 (คุณนก)\n• 092-393-7770 (คุณเสถียร) ได้เลยครับ 👓")

    # 2. Promotion & Packages Inquiry
    if any(k in msg_lower for k in ["โปร", "promotion", "ราคา", "แพ็กเกจ", "แพคเกจ", "เท่าไหร่", "กี่บาท", "ค่าตัด", "ส่วนลด", "ลดราคา", "990"]):
        return get_promotion_flex()

    # 3. Shipping & Delivery Inquiry (ดักคำถามเรื่องการส่งแว่น/พัสดุ ให้ขึ้นเมนูติดตามแว่นตาเสมอ)
    elif any(k in msg_lower for k in ["ส่งรึยัง", "ส่งหรือยัง", "จัดส่ง", "พัสดุ", "ติดตาม", "ส่งของ", "แว่นเสร็จ", "ถึงไหน", "เช็กพัสดุ", "สถานะ", "เลขพัสดุ", "ที่อยู่", "flash"]):
        return get_tracking_flex(user_id=user_id)

    # 3. Appointment / Eye Exam Inquiry (ดักคำถามเรื่องการนัดตรวจวัดสายตา ไม่ให้ตอบสลิปผิด)
    elif any(k in user_msg for k in ["นัด", "จองคิว", "ตรวจวัด", "ตรวจสายตา", "เข้ามาตรวจ", "เปิดกี่โมง", "เปิดวันไหน", "วัดตา"]):
        return get_appointment_flex()

    # 4. Prescription Slip Inquiry
    elif any(k in user_msg for k in ["สลิป", "ใบวัด", "ขอประวัติ", "ค่าสายตา"]):
        return get_prescription_flex(user_id=user_id)

    # 5. Store Location / Maps
    elif any(k in user_msg for k in ["แผนที่", "อาคาร b", "ศูนย์ราชการ", "พิกัดร้าน", "ร้านหลัก", "ais", "อยู่ตรงไหน"]):
        return get_store_location_flex()

    # 6. Booth Schedule
    elif any(k in user_msg for k in ["บูท", "สัญจร", "ตารางบูท", "พิกัดบูท"]):
        return get_booth_location_flex()

    # 7. After-Sales Support
    elif any(k in user_msg for k in ["บริการ", "หลังการขาย", "ปัญหา", "ดูแล", "ดัดทรง", "ซ่อม", "ไม่สบายตา", "หลวม"]):
        return get_service_care_flex()

    # 8. Contact Store
    elif any(k in user_msg for k in ["โทร", "เบอร์", "ติดต่อ", "คุยกับคน"]):
        return get_contact_flex()

    # 9. Smart Optical Consultation: Gaming & Screen (แว่นเล่นเกม / ทำงานหน้าจอ / กรองแสงสีฟ้า)
    elif any(k in msg_lower for k in ["เล่นเกม", "เกม", "เกมส์", "คอม", "หน้าจอ", "จอมือถือ", "แสงสีฟ้า", "บลู", "blue", "blue block", "blue cut", "ตาล้า", "ตาแห้ง", "แสบตา"]):
        gaming_reply = (
            "👓 แนะนำแว่นสำหรับ 'เล่นเกม & ทำงานหน้าจอ' โดยเสถียรการแว่นครับ!\n\n"
            "สำหรับคนที่ต้องจ้องหน้าจอนานๆ เล่นเกม หรือทำงานหน้าคอม ทางร้านขอแนะนำ 2 แพ็กเกจยอดนิยมครับ:\n\n"
            "1️⃣ ชุดเลนส์ Blue Block (ถนอมสายตาหน้าจอ) ฿ 1,490.-\n"
            "• กรองแสงสีฟ้าที่เป็นอันตรายจากหน้าจอมือถือและจอคอมพิวเตอร์\n"
            "• ลดอาการตาล้า แสบตา และตาแห้งได้ดีมาก ภาพคมชัด สบายตา\n"
            "• กรอบแว่นแฟชั่น น้ำหนักเบา (เลือกกรอบได้ทั้งร้าน)\n\n"
            "2️⃣ ชุดเลนส์ Blue Block Auto (2 in 1 ครบจบ) ฿ 1,990.-\n"
            "• อยู่ในร่ม/หน้าจอ: กรองแสงสีฟ้า เล่นเกม ทำงานสบายตา\n"
            "• ออกแดด: เลนส์จะเปลี่ยนสีเข้มเป็นแว่นกันแดดให้อัตโนมัติ ป้องกันรังสี UV 100%\n\n"
            "✨ ทั้ง 2 แพ็กเกจ ฟรี! บริการตรวจวัดสายตาละเอียดด้วยระบบคอมพิวเตอร์ + กล่องแว่น + ผ้าเช็ดเลนส์ไมโครไฟเบอร์ครับ\n\n"
            "📍 แวะมาลองกรอบจริงและตรวจสายตาได้ที่:\n"
            "ศูนย์ราชการเฉลิมพระเกียรติฯ อาคาร B ชั้น 1 (ตรงข้าม AIS)\n"
            "📞 สอบถามเพิ่มเติม: 085-433-6699 (คุณนก), 092-393-7770 (คุณเสถียร) ได้เลยครับ 😊"
        )
        return TextMessage(text=gaming_reply)

    # 10. Smart Optical Consultation: Driving & Sun (ขับรถ / ออกแดดเปลี่ยนสี)
    elif any(k in msg_lower for k in ["ขับรถ", "กลางคืน", "แดด", "ออกแดด", "เปลี่ยนสี", "ออโต้", "auto", "กันแดด", "แสงจ้า", "ตาแพ้แสง"]):
        driving_reply = (
            "👓 แนะนำแว่นสำหรับ 'ขับรถ & ออกแดด' โดยเสถียรการแว่นครับ!\n\n"
            "สำหรับคุณลูกค้าที่ต้องขับรถ หรือทำงานกลางแจ้ง ตาแพ้แสง:\n\n"
            "✨ ขอแนะนำ เลนส์ Auto Photochromic (ออกแดดเปลี่ยนสี) ฿ 1,990.-\n"
            "• เลนส์ใสเมื่ออยู่ในร่ม สบายตาเมื่อขับรถตอนกลางคืน\n"
            "• ปรับเฉดสีเข้มขึ้นเป็นแว่นกันแดดอัตโนมัติเมื่อเจอรังสี UV / แสงแดดจัด\n"
            "• สารเคลือบ Multicoat ลดแสงสะท้อนจากไฟหน้ารถและไฟถนน\n\n"
            "🎁 ราคานี้รวมกรอบแว่นน้ำหนักเบา + ตรวจวัดสายตาคอมพิวเตอร์ฟรีครับ\n\n"
            "📍 หน้าร้าน: ศูนย์ราชการ อาคาร B ชั้น 1 (ตรงข้าม AIS)\n"
            "📞 โทรปรึกษาคุณนกได้ที่: 085-433-6699 ครับ"
        )
        return TextMessage(text=driving_reply)

    # 11. Smart Optical Consultation: Progressive (เลนส์โปรเกรสซีฟ / มองใกล้ไม่ชัด / อายุ 40+)
    elif any(k in msg_lower for k in ["โปรเกรสซีฟ", "progressive", "สองชั้น", "มองใกล้", "มองไกล", "อ่านหนังสือ", "ยื่นแขน", "อายุ 40", "ผู้สูงอายุ"]):
        progressive_reply = (
            "👓 เลนส์โปรเกรสซีฟไร้รอยต่อ (ชัดทุกระยะ ไร้รอยต่อ) เสถียรการแว่น\n\n"
            "สำหรับผู้ที่มีปัญหาเริ่มมองใกล้ไม่ชัด อ่านหนังสือหรือดูมือถือต้องยื่นแขนออก:\n\n"
            "👑 ชุดเลนส์โปรเกรสซีฟเริ่มต้น ฿ 3,500.- (กรอบพร้อมเลนส์)\n"
            "• มองชัดครบ 3 ระยะ: ไกล (ขับรถ/ดูทีวี) - กลาง (จอคอม) - ใกล้ (อ่านหนังสือ/มือถือ) ในแว่นตัวเดียว\n"
            "• เลนส์ไร้รอยต่อ มองดูอ่อนกว่าวัยเหมือนแว่นสายตาทั่วไป\n"
            "• ตรวจวัดองศาตาและจุดกึ่งกลางตาดำ (PD) อย่างละเอียดโดย 'คุณเสถียร' ช่างผู้ชำนาญการกว่า 30 ปี\n\n"
            "📍 Walk-in เข้ามาวัดตาละเอียดได้เลยที่:\n"
            "ศูนย์ราชการ อาคาร B ชั้น 1 (ตรงข้าม AIS)\n"
            "📞 นัดเวลาหรือสอบถาม: 092-393-7770 (คุณเสถียร), 085-433-6699 (คุณนก)"
        )
        return TextMessage(text=progressive_reply)

    # 12. Smart Greeting & Welcome (คำทักทาย)
    elif any(k in msg_lower for k in ["สวัสดี", "หวัดดี", "hello", "hi", "ดีครับ", "ดีค่ะ", "สอบถาม"]):
        greeting_reply = (
            "สวัสดีครับ! ยินดีต้อนรับสู่ 'ร้านแว่นตา เสถียรการแว่น' ครับ 😊👓\n\n"
            "ทางร้านยินดีให้คำปรึกษาเรื่องสายตา เลนส์ และกรอบแว่นทุกชนิดครับ\n\n"
            "🏢 หน้าร้านหลัก: ศูนย์ราชการเฉลิมพระเกียรติฯ แจ้งวัฒนะ อาคาร B ชั้น 1 (โซน Million Mall ตรงข้าม AIS)\n"
            "⏰ เปิดทำการ: จันทร์ - ศุกร์ ตามเวลาราชการ (ปิด 15:30 น.)\n\n"
            "คุณลูกค้าสามารถแตะเมนูด้านล่างเพื่อ:\n"
            "• ดูโปรโมชั่นแว่นตาสุดคุ้ม (เริ่มต้น 990.-)\n"
            "• เช็กพิกัดบูทสัญจรของคุณพ่อ\n"
            "• เปิด Google Maps นำทางมาหน้าร้าน\n\n"
            "📞 โทรติดต่อด่วน: 085-433-6699 (คุณนก), 092-393-7770 (คุณเสถียร) ได้ตลอดเวลาครับ!"
        )
        return TextMessage(text=greeting_reply)

    # 13. AI Consultation fallback via Gemini (พร้อมป้ายกำกับข้อความอัตโนมัติ)
    ai_answer = ask_gemini(user_msg)
    if ai_answer:
        ai_disclaimer = (
            "\n\n───────────────\n"
            "🤖 [ข้อความตอบกลับอัตโนมัติโดย AI ผู้ช่วยร้านเสถียรการแว่น]\n"
            "(ไม่ใช่ข้อความจากเจ้าของร้านโดยตรง หากต้องการติดต่อเจ้าหน้าที่ โทร: 085-433-6699, 092-393-7770)"
        )
        return TextMessage(text=f"{ai_answer}{ai_disclaimer}")

    # 14. General fallback
    fallback_text = (
        f"ขอบคุณสำหรับข้อความครับ แอดมินร้านเสถียรการแว่นได้รับข้อความแล้ว จะรีบมาตอบกลับนะครับ 👓\n\n"
        f"หากมีเรื่องเร่งด่วน หรือต้องการสอบถามพิกัด สามารถโทรได้ที่:\n"
        f"• 085-433-6699 (คุณนก)\n"
        f"• 092-393-7770 (คุณเสถียร)"
    )
    return TextMessage(text=fallback_text)

# ==========================================
# WEB & API ROUTES
# ==========================================

UPLOAD_FOLDER = os.path.join(os.path.dirname(__file__), "static", "prescriptions")
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

@app.route("/", methods=["GET"])
def home():
    return render_template(
        "admin_dashboard.html",
        orders=database.get_recent_orders(),
        schedules=database.get_active_schedules(),
        prescriptions=database.get_all_prescriptions(),
        promotions=database.get_all_promotions()
    )

@app.route("/form/address", methods=["GET"])
def address_form():
    return render_template("address_form.html")

@app.route("/api/submit_address", methods=["POST"])
def submit_address():
    data = request.json or {}
    name = data.get("customer_name", "").strip()
    phone = data.get("phone", "").strip()
    addr = data.get("address", "").strip()
    details = data.get("order_details", "").strip()
    user_id = data.get("userId", "").strip()

    if not user_id:
        user_id = database.get_latest_line_user()

    if not name or not phone or not addr:
        return jsonify({"status": "error", "message": "กรุณากรอกข้อมูลให้ครบถ้วน"}), 400

    order_no = database.create_order(user_id, name, phone, addr, details)
    if user_id:
        database.link_user_phone(phone, user_id)

    # If LINE user ID exists, send push message confirmation
    if user_id:
        try:
            messaging_api = get_messaging_api()
            confirm_text = (
                f"✅ ร้านเสถียรการแว่นได้รับที่อยู่จัดส่งของคุณเรียบร้อยแล้วครับ!\n\n"
                f"เลขที่ออเดอร์: {order_no}\n"
                f"ผู้รับ: {name}\n"
                f"เบอร์ติดต่อ: {phone}\n"
                f"ที่อยู่: {addr}\n\n"
                f"เมื่อตัดประกอบแว่นเสร็จแล้ว ทางร้านจะแจ้งให้ทราบผ่านแชทนี้ทันทีครับ 👓"
            )
            messaging_api.push_message(PushMessageRequest(to=user_id, messages=[TextMessage(text=confirm_text)]))
        except Exception as e:
            print(f"[WARN] Failed to push confirmation: {e}")

    return jsonify({"status": "ok", "order_no": order_no})

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    error = None
    if request.method == "POST":
        pwd = request.form.get("password", "").strip()
        expected = os.getenv("ADMIN_PASSWORD", ADMIN_PASSWORD).strip()
        if pwd and pwd == expected:
            session["admin_logged_in"] = True
            session.permanent = True
            next_url = request.args.get("next") or "/admin"
            return redirect(next_url)
        else:
            error = "รหัสผ่านไม่ถูกต้อง กรุณาลองใหม่อีกครั้งครับ"
    return render_template("admin_login.html", error=error)

@app.route("/admin/logout", methods=["GET"])
def admin_logout():
    session.pop("admin_logged_in", None)
    return redirect("/admin/login")

@app.route("/admin", methods=["GET"])
@admin_required
def admin():
    orders = database.get_recent_orders()
    schedules = database.get_active_schedules()
    prescriptions = database.get_all_prescriptions()
    promotions = database.get_all_promotions()

    completed_orders = sum(1 for o in orders if "เสร็จ" in o.get("status", "") or "จัดส่ง" in o.get("status", "") or "ส่งมอบ" in o.get("status", ""))
    pending_orders = len(orders) - completed_orders

    stats = {
        "total_orders": len(orders),
        "pending_orders": pending_orders,
        "completed_orders": completed_orders,
        "total_promos": len(promotions),
        "total_rx": len(prescriptions),
        "total_schedules": len(schedules)
    }

    return render_template(
        "admin_dashboard.html",
        orders=orders,
        schedules=schedules,
        prescriptions=prescriptions,
        promotions=promotions,
        stats=stats
    )

@app.route("/admin/add_promotion", methods=["POST"])
@admin_required
def add_promotion_route():
    title = request.form.get("title", "").strip()
    price = request.form.get("price", "").strip()
    tag = request.form.get("tag", "").strip()
    color = request.form.get("color", "#EA580C").strip()
    details = request.form.get("details", "").strip()
    sort_order_raw = request.form.get("sort_order", "0").strip()
    try:
        sort_order = int(sort_order_raw)
    except ValueError:
        sort_order = 0
    if title and price:
        database.add_promotion(title, price, tag, color, details, sort_order)
    return redirect("/admin")

@app.route("/admin/delete_promotion", methods=["POST"])
@admin_required
def delete_promotion_route():
    promo_id = request.form.get("promo_id")
    if promo_id:
        database.delete_promotion(int(promo_id))
    return redirect("/admin")

@app.route("/admin/add_prescription", methods=["POST"])
@admin_required
def add_prescription_route():
    import time
    phone = request.form.get("phone", "").strip()
    customer_name = request.form.get("customer_name", "").strip()
    patient_name = request.form.get("patient_name", "").strip() or customer_name
    relation = request.form.get("relation", "เจ้าของบัญชี").strip()
    exam_date = request.form.get("exam_date", "").strip()
    sph_r = request.form.get("sph_r", "").strip()
    cyl_r = request.form.get("cyl_r", "").strip()
    axis_r = request.form.get("axis_r", "").strip()
    add_r = request.form.get("add_r", "").strip()
    sph_l = request.form.get("sph_l", "").strip()
    cyl_l = request.form.get("cyl_l", "").strip()
    axis_l = request.form.get("axis_l", "").strip()
    add_l = request.form.get("add_l", "").strip()
    pd = request.form.get("pd", "").strip()
    notes = request.form.get("notes", "").strip()
    line_user_id = request.form.get("line_user_id", "").strip()

    # Handle image upload
    image_url = ""
    slip_file = request.files.get("slip_image")
    if slip_file and slip_file.filename:
        ext = os.path.splitext(slip_file.filename)[1].lower() or ".jpg"
        clean_p = phone[-4:] if len(phone) >= 4 else "rx"
        safe_name = f"slip_{int(time.time())}_{clean_p}{ext}"
        filepath = os.path.join(UPLOAD_FOLDER, safe_name)
        slip_file.save(filepath)
        image_url = f"{BASE_URL}/static/prescriptions/{safe_name}"

    # Save to database
    rx_id, resolved_uid = database.add_prescription(
        line_user_id=line_user_id,
        phone=phone,
        customer_name=customer_name,
        patient_name=patient_name,
        relation=relation,
        sph_r=sph_r, cyl_r=cyl_r, axis_r=axis_r, add_r=add_r,
        sph_l=sph_l, cyl_l=cyl_l, axis_l=axis_l, add_l=add_l,
        pd=pd, image_url=image_url, notes=notes, exam_date=exam_date
    )

    # Auto-push interactive prescription flex card to customer on LINE!
    if resolved_uid:
        try:
            messaging_api = get_messaging_api()
            flex_msg = get_prescription_flex(user_id=resolved_uid, phone=phone)
            greeting = f"🎉 เสถียรการแว่น ขอส่งผลตรวจวัดสายตาของ '{patient_name}' ({relation}) เรียบร้อยแล้วครับ สามารถเปิดดูข้อมูลสลิปด้านล่างนี้ได้ตลอดเวลาครับ 👓"
            messaging_api.push_message(PushMessageRequest(
                to=resolved_uid,
                messages=[TextMessage(text=greeting), flex_msg]
            ))
            print(f"[SUCCESS] Pushed prescription flex to LINE user: {resolved_uid}")
        except Exception as e:
            print(f"[WARN] Failed to push prescription to LINE: {e}")

    return redirect("/admin")

@app.route("/admin/delete_prescription", methods=["POST"])
@admin_required
def delete_prescription_route():
    rx_id = request.form.get("rx_id")
    if rx_id:
        database.delete_prescription(int(rx_id))
    return redirect("/admin")

@app.route("/admin/add_schedule", methods=["POST"])
@admin_required
def add_schedule():
    date_range = request.form.get("date_range", "").strip()
    location = request.form.get("location", "").strip()
    note = request.form.get("note", "").strip()
    if date_range and location:
        database.add_booth_schedule(date_range, location, note)
    return redirect("/admin")

@app.route("/admin/update_order", methods=["POST"])
@admin_required
def update_order():
    order_id = request.form.get("order_id")
    status = request.form.get("status", "").strip()
    tracking_no = request.form.get("tracking_no", "").strip()

    if order_id and status:
        database.update_order_status(order_id, status, tracking_no)
        conn = database.get_db()
        cur = conn.cursor()
        cur.execute("SELECT * FROM orders WHERE id = ?", (order_id,))
        order = cur.fetchone()
        conn.close()

        target_user_id = ""
        if order and order["line_user_id"]:
            target_user_id = order["line_user_id"]
        else:
            target_user_id = database.get_latest_line_user()
            if target_user_id:
                # Update back to order
                conn = database.get_db()
                conn.execute("UPDATE orders SET line_user_id = ? WHERE id = ?", (target_user_id, order_id))
                conn.commit()
                conn.close()

        # Send push notification to customer
        if target_user_id:
            try:
                messaging_api = get_messaging_api()
                msg_body = f"👓 เสถียรการแว่น ขอแจ้งอัปเดตสถานะแว่นตาของคุณ ({order['customer_name']}):\n\nสถานะ: {status}"
                if tracking_no:
                    msg_body += f"\n\nเลขพัสดุ Flash Express: {tracking_no}\nตรวจสอบสถานะ: https://www.flashexpress.co.th/tracking/?se={tracking_no}"
                elif "เสร็จ" in status:
                    msg_body += f"\n\nคุณลูกค้าสามารถแวะมารับแว่นที่บูทได้เลยครับ! หากหาบูทไม่เจอ โทรติดต่อ 092-393-7770 (คุณเสถียร) ได้เลยครับ ✨"
                elif "ส่งมอบ" in status:
                    msg_body += f"\n\nทางร้านกำลังเดินทางไปส่งมอบให้ถึงมือคุณลูกค้า หากใกล้ถึงแล้วจะโทรประสานงานนะครับ 🚗"

                messaging_api.push_message(PushMessageRequest(to=target_user_id, messages=[TextMessage(text=msg_body)]))
                print(f"[SUCCESS] Pushed order update to {target_user_id}")
            except Exception as e:
                print(f"[WARN] Failed to send order status push: {e}")

    return redirect("/admin")

@app.route("/booth-card", methods=["GET"])
def booth_card():
    return send_file(os.path.join(os.path.dirname(__file__), "booth_stand_card.html"))

@app.route("/logo-image", methods=["GET"])
def logo_image():
    return send_file(os.path.join(os.path.dirname(__file__), "logo_original.jpg"), mimetype="image/jpeg")

# ==========================================
# WEBHOOK CALLBACK
# ==========================================

@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    # 1. Verification ping check
    try:
        data = json.loads(body) if body else {}
        if "events" in data and len(data.get("events", [])) == 0:
            print("[INFO] Webhook Verification ping received from LINE! Returning 200 OK.")
            return "OK", 200
    except Exception as e:
        print(f"[WARN] Error decoding JSON: {e}")

    # 2. Standard LINE Handler
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("[WARN] InvalidSignatureError. Attempting fallback event processing...")
        try:
            data = json.loads(body)
            messaging_api = get_messaging_api()
            for ev in data.get("events", []):
                reply_token = ev.get("replyToken")
                user_id = ev.get("source", {}).get("userId", "")
                if user_id:
                    database.record_line_user(user_id)
                if not reply_token:
                    continue
                try:
                    if ev.get("type") == "message" and ev.get("message", {}).get("type") == "text":
                        text = ev.get("message", {}).get("text", "")
                        reply_msg = get_reply_for_text(text, user_id)
                        messaging_api.reply_message(
                            ReplyMessageRequest(
                                reply_token=reply_token,
                                messages=[reply_msg]
                            )
                        )
                    elif ev.get("type") == "follow":
                        welcome_text = (
                            "ยินดีต้อนรับสู่ เสถียรการแว่น ครับ! 👓\n\n"
                            "ขอบคุณที่แวะมาพบกันนะครับ ไม่ว่าจะพบกันที่บูท หรือที่หน้าร้านประจำ\n\n"
                            "คุณลูกค้าสามารถแตะที่เมนูด้านล่างเพื่อ:\n"
                            "• ดูแผนที่ร้านประจำ (ศูนย์ราชการ อาคาร B)\n"
                            "• สอบถามพิกัดออกบูทของคุณพ่อ\n"
                            "• ติดตามแว่นและพัสดุ\n"
                            "• รับบริการดูแลแว่นตา ล้าง ดัดทรง เปลี่ยนแป้นจมูกฟรีตลอดชีพครับ!"
                        )
                        messaging_api.reply_message(
                            ReplyMessageRequest(
                                reply_token=reply_token,
                                messages=[TextMessage(text=welcome_text)]
                            )
                        )
                except Exception as api_err:
                    print(f"[WARN] Error calling LINE Reply API: {api_err}")
        except Exception as err:
            print(f"[ERROR] Fallback parsing failed: {err}")
    except Exception as e:
        print(f"[ERROR] General exception: {e}")

    return "OK", 200

@handler.add(FollowEvent)
def handle_follow(event):
    messaging_api = get_messaging_api()
    if event.source.user_id:
        database.record_line_user(event.source.user_id)
    welcome_text = (
        "ยินดีต้อนรับสู่ เสถียรการแว่น ครับ! 👓\n\n"
        "ขอบคุณที่แวะมาพบกันนะครับ ไม่ว่าจะพบกันที่บูท หรือที่หน้าร้านประจำ\n\n"
        "คุณลูกค้าสามารถแตะที่เมนูด้านล่างเพื่อ:\n"
        "• ดูแผนที่ร้านประจำ (ศูนย์ราชการ อาคาร B)\n"
        "• สอบถามพิกัดออกบูทของคุณพ่อ\n"
        "• ติดตามแว่นและพัสดุ\n"
        "• รับบริการดูแลแว่นตา ล้าง ดัดทรง เปลี่ยนแป้นจมูกฟรีตลอดชีพครับ!"
    )
    messaging_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[TextMessage(text=welcome_text)]
        )
    )

@handler.add(MessageEvent, message=TextMessageContent)
def handle_message(event):
    messaging_api = get_messaging_api()
    user_id = event.source.user_id
    if user_id:
        database.record_line_user(user_id)
    user_msg = event.message.text.strip()
    msg = get_reply_for_text(user_msg, user_id)
    messaging_api.reply_message(
        ReplyMessageRequest(
            reply_token=event.reply_token,
            messages=[msg]
        )
    )

if __name__ == "__main__":
    port = int(os.getenv("PORT", 5000))
    print(f"Starting Sathien Optics Master Bot on port {port}...")
    app.run(host="0.0.0.0", port=port, debug=False)
