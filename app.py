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

def get_store_location_flex(user_id=""):
    booking_home_url = f"{BASE_URL}/form/booking?loc=home"
    if user_id:
        booking_home_url += f"&userId={user_id}"

    # Bubble 1: ศูนย์ราชการ อาคาร B
    bubble_gov = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#059669",
            "contents": [
                {"type": "text", "text": "🏢 สาขา 1 (ร้านประจำ)", "weight": "bold", "color": "#D1FAE5", "size": "xs"},
                {"type": "text", "text": "ศูนย์ราชการ อาคาร B", "weight": "bold", "color": "#FFFFFF", "size": "xl", "margin": "xs"}
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "xs",
                    "contents": [
                        {"type": "text", "text": "📍 พิกัดร้านในอาคาร:", "size": "xs", "color": "#059669", "weight": "bold"},
                        {"type": "text", "text": "ชั้นล่าง (โซน Million Mall ตรงข้าม AIS)", "size": "sm", "weight": "bold", "color": "#111111"},
                        {"type": "text", "text": "ศูนย์ราชการเฉลิมพระเกียรติฯ อาคาร B ถ.แจ้งวัฒนะ", "size": "xs", "color": "#555555", "wrap": True}
                    ]
                },
                {"type": "separator", "margin": "xs"},
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "xs",
                    "contents": [
                        {"type": "text", "text": "⏰ เวลาทำการ:", "size": "xs", "color": "#059669", "weight": "bold"},
                        {"type": "text", "text": "จันทร์ - ศุกร์ ตามเวลาราชการ", "size": "xs", "color": "#333333"},
                        {"type": "text", "text": "(ทางร้านเปิดบริการ 08:30 - 15:00 น.)", "size": "xs", "color": "#E11D48", "weight": "bold"}
                    ]
                },
                {"type": "separator", "margin": "xs"},
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "xs",
                    "contents": [
                        {"type": "text", "text": "✨ สะดวก รวดเร็ว รอรับแว่นได้ใน 20-30 นาที", "size": "xs", "color": "#059669", "weight": "bold"}
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
                    "height": "sm",
                    "action": {
                        "type": "uri",
                        "label": "🗺️ แผนที่ศูนย์ราชการ",
                        "uri": "https://maps.app.goo.gl/RWCdTXF3HJiSskis9"
                    }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "height": "sm",
                    "action": {
                        "type": "uri",
                        "label": "📞 โทรหาคุณนก",
                        "uri": "tel:0854336699"
                    }
                }
            ]
        }
    }

    # Bubble 2: สตูดิโอที่บ้าน The Plant-Light ติวานนท์-รังสิต
    bubble_home = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#4338CA",
            "contents": [
                {"type": "text", "text": "🏡 สาขา 2: สตูดิโอส่วนตัว (Home VIP)", "weight": "bold", "color": "#E0E7FF", "size": "xs"},
                {"type": "text", "text": "The Plant-Light ติวานนท์", "weight": "bold", "color": "#FFFFFF", "size": "lg", "margin": "xs"}
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "xs",
                    "contents": [
                        {"type": "text", "text": "📍 พิกัดสตูดิโอที่บ้าน:", "size": "xs", "color": "#4338CA", "weight": "bold"},
                        {"type": "text", "text": "บ้านเลขที่ 99/263 (ม.The Plant-Light)", "size": "sm", "weight": "bold", "color": "#111111"},
                        {"type": "text", "text": "ถ.ติวานนท์-รังสิต อ.เมือง จ.ปทุมธานี", "size": "xs", "color": "#555555", "wrap": True}
                    ]
                },
                {"type": "separator", "margin": "xs"},
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "xs",
                    "contents": [
                        {"type": "text", "text": "👑 จุดเด่นการตรวจที่บ้าน:", "size": "xs", "color": "#4338CA", "weight": "bold"},
                        {"type": "text", "text": "• ตรวจวัดสายตาละเอียดแบบ Private 1 ต่อ 1", "size": "xs", "color": "#333333"},
                        {"type": "text", "text": "• เงียบสงบ ไม่ต้องรอคิว ที่จอดรถสะดวกสบาย", "size": "xs", "color": "#333333"},
                        {"type": "text", "text": "• เปิดบริการทุกวัน (รวม ส.-อา. และช่วงเย็น)", "size": "xs", "color": "#4338CA", "weight": "bold"},
                        {"type": "text", "text": "• กรุณานัดหมายเวลาล่วงหน้าเพื่อการดูแลที่ดีที่สุด", "size": "xs", "color": "#64748B"}
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
                    "color": "#4338CA",
                    "height": "sm",
                    "action": {
                        "type": "uri",
                        "label": "📅 นัดคิวตรวจที่บ้าน",
                        "uri": booking_home_url
                    }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "height": "sm",
                    "action": {
                        "type": "uri",
                        "label": "🗺️ แผนที่บ้านรังสิต",
                        "uri": "https://maps.google.com/?q=The+Plant+Light+Tiwanon+Rangsit"
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

    carousel = {
        "type": "carousel",
        "contents": [bubble_gov, bubble_home]
    }
    return FlexMessage(alt_text="พิกัดร้าน เสถียรการแว่น (ศูนย์ราชการ อาคาร B & สตูดิโอติวานนท์-รังสิต)", contents=FlexContainer.from_json(json.dumps(carousel)))


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
        return TextMessage(text="👓 แพ็กเกจแว่นตายอดนิยม เสถียรการแว่น:\n\n• ชุดกรอบแว่นแฟชั่นน้ำหนักเบา (เลือกได้ทั้งร้าน)\n• ชุดเลนส์ Blue Block ถนอมสายตาหน้าจอคอม/มือถือ\n• ชุดเลนส์ Auto Photochromic ออกแดดเปลี่ยนสีอัจฉริยะ\n• ชุดเลนส์โปรเกรสซีฟ ไร้รอยต่อ ชัดครบทุกระยะ\n\n✨ บริการตรวจวัดสายตาฟรีด้วยระบบคอมพิวเตอร์\n📞 ปรึกษาคุณนก: 085-433-6699 หรือคุณเสถียร: 092-393-7770 ได้เลยครับ")

    bubbles = []
    for p in promos[:10]:
        title = p.get("title", "ชุดตัดแว่น")
        tag = p.get("tag", "✨ คุณภาพพรีเมียม")
        color = p.get("color", "#059669")
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
                    {"type": "text", "text": "กรอบพร้อมเลนส์ • ตรวจวัดสายตาฟรี", "weight": "bold", "size": "sm", "color": "#FEF08A", "margin": "xs"}
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
                            "label": "💬 ปรึกษาคุณนก",
                            "text": f"สนใจ{title} ครับ"[:20]
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
    return FlexMessage(alt_text="แพ็กเกจแว่นตายอดนิยม เสถียรการแว่น", contents=FlexContainer.from_json(json.dumps(carousel_json)))

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


def get_appointment_flex(user_id=""):
    booking_url = f"{BASE_URL}/form/booking"
    if user_id:
        booking_url += f"?userId={user_id}"

    bubble_json = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#4338CA",
            "contents": [
                {"type": "text", "text": "👓 เสถียรการแว่น", "weight": "bold", "color": "#E0E7FF", "size": "xs"},
                {"type": "text", "text": "นัดตรวจวัดสายตาละเอียด", "weight": "bold", "color": "#FFFFFF", "size": "xl", "margin": "xs"}
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "text",
                    "text": "เลือกสถานที่ตรวจวัดสายตาที่สะดวกได้เลยครับ:",
                    "weight": "bold",
                    "size": "sm",
                    "color": "#1E293B"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#EEF2FF",
                    "cornerRadius": "md",
                    "paddingAll": "sm",
                    "borderColor": "#C7D2FE",
                    "borderWidth": "light",
                    "contents": [
                        {"type": "text", "text": "🏡 1. สตูดิโอที่บ้าน (ติวานนท์-รังสิต ปทุมธานี):", "size": "xs", "weight": "bold", "color": "#3730A3"},
                        {"type": "text", "text": "• ตรวจ Private 1 ต่อ 1 เงียบสงบ ไม่ต้องรอคิว\n• เหมาะกับเลนส์โปรเกรสซีฟ หรือพาครอบครัวมาตรวจ\n• เปิดทุกวัน (รวม ส.-อา. และช่วงเย็น) นัดล่วงหน้า", "size": "xs", "color": "#4B5563", "wrap": True, "margin": "xs"}
                    ]
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#ECFDF5",
                    "cornerRadius": "md",
                    "paddingAll": "sm",
                    "borderColor": "#A7F3D0",
                    "borderWidth": "light",
                    "contents": [
                        {"type": "text", "text": "🏢 2. ศูนย์ราชการ อาคาร B (แจ้งวัฒนะ):", "size": "xs", "weight": "bold", "color": "#065F46"},
                        {"type": "text", "text": "• ชั้นล่าง โซน Million Mall ตรงข้าม AIS\n• จันทร์ - ศุกร์ 08:30 - 15:00 น. (Walk-in ได้เลย)", "size": "xs", "color": "#4B5563", "wrap": True, "margin": "xs"}
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
                    "color": "#4338CA",
                    "height": "sm",
                    "action": {
                        "type": "uri",
                        "label": "📅 จองคิวนัดตรวจสายตา",
                        "uri": booking_url
                    }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "height": "sm",
                    "action": {
                        "type": "uri",
                        "label": "📞 โทรนัดคุณเสถียร",
                        "uri": "tel:0923937770"
                    }
                },
                {
                    "type": "button",
                    "style": "link",
                    "height": "sm",
                    "action": {
                        "type": "uri",
                        "label": "📞 โทรนัดคุณนก",
                        "uri": "tel:0854336699"
                    }
                }
            ]
        }
    }
    return FlexMessage(alt_text="นัดตรวจวัดสายตา เสถียรการแว่น (ที่บ้านรังสิต & ศูนย์ราชการ)", contents=FlexContainer.from_json(json.dumps(bubble_json)))


def build_appointment_alert_flex(booking):
    booking_no = booking.get("booking_no", "-")
    name = booking.get("customer_name", "-")
    phone = booking.get("phone", "-")
    loc = booking.get("preferred_location", "สตูดิโอที่บ้าน")
    b_date = booking.get("booking_date", "-")
    b_time = booking.get("booking_time", "-")
    service = booking.get("service_type", "ตรวจวัดสายตาประกอบแว่น")
    notes = booking.get("notes", "")

    call_label = f"📞 โทรหา {name}"
    if len(call_label) > 20:
        call_label = call_label[:20]

    bubble = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#4338CA",
            "contents": [
                {"type": "text", "text": "🔔 มีการนัดหมายตรวจสายตา!", "weight": "bold", "color": "#E0E7FF", "size": "sm"},
                {"type": "text", "text": f"นัดหมาย #{booking_no}", "weight": "bold", "color": "#FFFFFF", "size": "xl", "margin": "xs"}
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#EEF2FF",
                    "cornerRadius": "md",
                    "paddingAll": "md",
                    "contents": [
                        {"type": "text", "text": f"👤 คุณ: {name}", "weight": "bold", "size": "md", "color": "#312E81"},
                        {"type": "text", "text": f"📞 โทร: {phone}", "weight": "bold", "size": "sm", "color": "#1E293B", "margin": "xs"},
                        {"type": "separator", "margin": "sm"},
                        {"type": "text", "text": f"📍 สถานที่: {loc}", "weight": "bold", "size": "xs", "color": "#4338CA", "margin": "sm", "wrap": True},
                        {"type": "text", "text": f"📅 วันที่: {b_date} ({b_time})", "size": "xs", "color": "#1E293B", "weight": "bold", "margin": "xs"},
                        {"type": "text", "text": f"🎯 บริการ: {service}", "size": "xs", "color": "#475569", "margin": "xs", "wrap": True},
                        {"type": "text", "text": f"📝 หมายเหตุ: {notes}", "size": "xs", "color": "#64748B", "margin": "xs", "wrap": True} if notes else {"type": "text", "text": "📝 หมายเหตุ: -", "size": "xs", "color": "#64748B", "margin": "xs"}
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
                    "color": "#4338CA",
                    "height": "sm",
                    "action": {
                        "type": "uri",
                        "label": call_label,
                        "uri": f"tel:{phone}"
                    }
                }
            ]
        }
    }
    return FlexMessage(alt_text=f"🔔 [นัดหมายใหม่] {name} ({phone}) - {loc}", contents=FlexContainer.from_json(json.dumps(bubble)))


def build_order_alert_flex(order):
    order_no = order.get("order_no", "-")
    name = order.get("customer_name", "-")
    phone = order.get("phone", "-")
    address = order.get("address", "-")
    details = order.get("order_details", "ตัดประกอบแว่นตา")

    call_label = f"📞 โทรหา {name}"
    if len(call_label) > 20:
        call_label = call_label[:20]

    bubble = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#DC2626",
            "contents": [
                {"type": "text", "text": "🚨 มีออเดอร์ใหม่จัดส่ง!", "weight": "bold", "color": "#FEE2E2", "size": "sm"},
                {"type": "text", "text": f"ออเดอร์ #{order_no}", "weight": "bold", "color": "#FFFFFF", "size": "xl", "margin": "xs"}
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#FEF2F2",
                    "cornerRadius": "md",
                    "paddingAll": "md",
                    "contents": [
                        {"type": "text", "text": f"👤 คุณ: {name}", "weight": "bold", "size": "md", "color": "#991B1B"},
                        {"type": "text", "text": f"📞 โทร: {phone}", "weight": "bold", "size": "sm", "color": "#1E293B", "margin": "xs"},
                        {"type": "separator", "margin": "sm"},
                        {"type": "text", "text": "🏠 ที่อยู่จัดส่ง:", "size": "xs", "weight": "bold", "color": "#64748B", "margin": "sm"},
                        {"type": "text", "text": address, "size": "xs", "color": "#334155", "wrap": True, "margin": "xs"},
                        {"type": "separator", "margin": "sm"},
                        {"type": "text", "text": f"👓 รายละเอียด: {details}", "size": "xs", "color": "#475569", "wrap": True, "margin": "sm"}
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
                    "color": "#DC2626",
                    "height": "sm",
                    "action": {
                        "type": "uri",
                        "label": call_label,
                        "uri": f"tel:{phone}"
                    }
                }
            ]
        }
    }
    return FlexMessage(alt_text=f"🚨 [มีออเดอร์ใหม่] {name} ({phone})", contents=FlexContainer.from_json(json.dumps(bubble)))


def build_prescription_alert_flex(user_msg, user_id="", user_name=""):
    bubble = {
        "type": "bubble",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#7C3AED",
            "contents": [
                {"type": "text", "text": "📄 ลูกค้าทักขอสลิปสายตา!", "weight": "bold", "color": "#EDE9FE", "size": "sm"},
                {"type": "text", "text": "แจ้งเตือนคุณเสถียร/คุณนก", "weight": "bold", "color": "#FFFFFF", "size": "xl", "margin": "xs"}
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#F5F3FF",
                    "cornerRadius": "md",
                    "paddingAll": "md",
                    "contents": [
                        {"type": "text", "text": f"👤 ผู้ทัก: {user_name if user_name else 'ลูกค้าใน LINE'}", "weight": "bold", "size": "sm", "color": "#5B21B6"},
                        {"type": "text", "text": f"💬 ข้อความ: \"{user_msg}\"", "size": "xs", "color": "#1E293B", "wrap": True, "margin": "xs"},
                        {"type": "separator", "margin": "sm"},
                        {"type": "text", "text": "💡 ลูกค้าต้องการดูสลิปผลวัดสายตาเดิม หรือขอใบประวัติ คุณนก/คุณเสถียรสามารถค้นใบวัดสายตา แล้วถ่ายรูปส่งให้ในแชทนี้ได้เลยครับ 😊", "size": "xs", "color": "#6D28D9", "wrap": True, "margin": "sm"}
                    ]
                }
            ]
        }
    }
    return FlexMessage(alt_text=f"📄 [ลูกค้าขอสลิปสายตา] {user_msg[:30]}", contents=FlexContainer.from_json(json.dumps(bubble)))


def notify_all_admins(alert_text, flex_message=None):
    """
    Sends instant push alert to all registered admin LINE accounts.
    """
    try:
        admins = database.get_active_admin_subscribers()
        if not admins:
            print("[INFO] No active admin subscribers registered.")
            return 0

        messaging_api = get_messaging_api()
        count = 0
        for admin in admins:
            uid = admin.get("line_user_id")
            if not uid:
                continue
            try:
                msgs = [flex_message] if flex_message else [TextMessage(text=alert_text)]
                messaging_api.push_message(
                    PushMessageRequest(
                        to=uid,
                        messages=msgs
                    )
                )
                count += 1
                print(f"[SUCCESS] Pushed admin alert to {admin.get('name', 'Admin')} ({uid[:8]}...)")
            except Exception as err:
                print(f"[WARN] Failed to push to admin {uid}: {err}")
        return count
    except Exception as e:
        print(f"[ERROR] notify_all_admins failed: {e}")
        return 0


def get_reply_for_text(user_msg, user_id=""):
    # Record user active state
    if user_id:
        database.record_line_user(user_id)

    msg_clean = user_msg.strip()
    msg_lower = msg_clean.lower()

    # 0. Admin Registration & Alert Subscription (#แอดมิน, #admin, ลงทะเบียนแอดมิน, #เสถียร, #นก)
    if msg_clean.startswith("#แอดมิน") or msg_lower.startswith("#admin") or msg_clean in ["#สมัครแอดมิน", "ลงทะเบียนแอดมิน", "#เสถียร", "#นก"]:
        parts = msg_clean.split(maxsplit=1)
        admin_name = ""
        if len(parts) > 1:
            admin_name = parts[1].strip()
        elif "#เสถียร" in msg_clean:
            admin_name = "คุณเสถียร"
        elif "#นก" in msg_clean:
            admin_name = "คุณนก"
        else:
            try:
                prof = get_messaging_api().get_profile(user_id)
                admin_name = prof.display_name
            except Exception:
                admin_name = "แอดมินร้าน"

        database.register_admin_subscriber(user_id, name=admin_name, role="ผู้ดูแลร้าน")
        confirm_reply = (
            f"🎉 ยินดีต้อนรับ '{admin_name}' เข้าสู่ระบบรับแจ้งเตือนร้านเสถียรการแว่นครับ! 👓\n\n"
            f"🔔 ระบบบันทึกบัญชี LINE ของท่านเรียบร้อยแล้ว\n"
            f"ตั้งแต่นี้เป็นต้นไป ระบบจะ ยิงข้อความเด้งเข้า LINE นี้ทันที เมื่อ:\n"
            f"1. 📦 มีลูกค้ากรอกที่อยู่จัดส่งแว่นตาใหม่\n"
            f"2. 📄 มีลูกค้าทักขอสลิปสายตา / ประวัติสายตา\n\n"
            f"คุณเสถียรและคุณนกไม่ต้องคอยเปิดคอมหรือเปิดหน้าเว็บเช็คเลยครับ ระบบจะส่งเตือนให้ทันที! ✨"
        )
        return TextMessage(text=confirm_reply)

    if msg_clean in ["#ยกเลิกแอดมิน", "#ยกเลิกรับแจ้งเตือน", "#unsubscribe"]:
        admins = database.get_all_admin_subscribers()
        for a in admins:
            if a["line_user_id"] == user_id:
                database.delete_admin_subscriber(a["id"])
        return TextMessage(text="🔕 ยกเลิกการรับแจ้งเตือนสำหรับบัญชี LINE นี้เรียบร้อยแล้วครับ หากต้องการเปิดใหม่สามารถพิมพ์ #แอดมิน ได้ทุกเมื่อครับ")

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
    if any(k in msg_lower for k in ["โปร", "promotion", "ราคา", "แพ็กเกจ", "แพคเกจ", "เท่าไหร่", "กี่บาท", "ค่าตัด", "ส่วนลด", "ลดราคา"]):
        return get_promotion_flex()

    # 3. Shipping & Delivery Inquiry (ดักคำถามเรื่องการส่งแว่น/พัสดุ ให้ขึ้นเมนูติดตามแว่นตาเสมอ)
    elif any(k in msg_lower for k in ["ส่งรึยัง", "ส่งหรือยัง", "จัดส่ง", "พัสดุ", "ติดตาม", "ส่งของ", "แว่นเสร็จ", "ถึงไหน", "เช็กพัสดุ", "สถานะ", "เลขพัสดุ", "ที่อยู่", "flash"]):
        return get_tracking_flex(user_id=user_id)

    # 4. Appointment / Eye Exam Inquiry (ดักคำถามเรื่องการนัดตรวจวัดสายตา)
    elif any(k in user_msg for k in ["นัด", "จองคิว", "ตรวจวัด", "ตรวจสายตา", "เข้ามาตรวจ", "เปิดกี่โมง", "เปิดวันไหน", "วัดตา", "ตรวจตา", "นัดหมาย", "จองเวลา", "นัดที่บ้าน"]):
        return get_appointment_flex(user_id=user_id)

    # 5. Prescription Slip Inquiry
    elif any(k in user_msg for k in ["สลิป", "ใบวัด", "ขอประวัติ", "ค่าสายตา"]):
        # Instant admin push alert to Khun Nok and Khun Sathien
        try:
            user_display_name = ""
            if user_id:
                try:
                    prof = get_messaging_api().get_profile(user_id)
                    user_display_name = prof.display_name
                except Exception:
                    pass
            rx_alert_flex = build_prescription_alert_flex(user_msg, user_id=user_id, user_name=user_display_name)
            notify_all_admins(
                alert_text=f"📄 [ลูกค้าขอสลิปสายตา] {user_display_name or 'ลูกค้า'}: \"{user_msg}\"",
                flex_message=rx_alert_flex
            )
        except Exception as e:
            print(f"[WARN] Failed to trigger prescription alert to admins: {e}")

        return get_prescription_flex(user_id=user_id)

    # 6. Store Location / Maps
    elif any(k in user_msg for k in ["แผนที่", "อาคาร b", "ศูนย์ราชการ", "พิกัดร้าน", "ร้านหลัก", "ais", "อยู่ตรงไหน", "เดินทาง", "ที่ตั้ง", "บ้าน", "รังสิต", "ติวานนท์", "ปทุมธานี", "the plant", "สาขา", "พิกัด", "ที่อยู่", "หน้าร้าน"]):
        return get_store_location_flex(user_id=user_id)

    # 7. Booth Schedule
    elif any(k in user_msg for k in ["บูท", "สัญจร", "ตารางบูท", "พิกัดบูท", "ออกบูท", "ไปงานไหน"]):
        return get_booth_location_flex()

    # 8. After-Sales Support & Repairs
    elif any(k in user_msg for k in ["บริการ", "หลังการขาย", "ปัญหา", "ดูแล"]):
        return get_service_care_flex()

    # 9. Contact Store
    elif any(k in user_msg for k in ["โทร", "เบอร์", "ติดต่อ", "คุยกับคน", "เบอร์โทร", "ขอเบอร์"]):
        return get_contact_flex()

    # 10. Smart Optical Knowledge: ทำงานหน้าคอม / จ้องจอนาน / เล่นเกม / ตาล้า / แสงสีฟ้า
    elif any(k in msg_lower for k in ["หน้าคอม", "ทำงานหน้าจอ", "จ้องจอ", "เล่นเกม", "เกมส์", "เกม", "คอมพิวเตอร์", "มือถือ", "แสงสีฟ้า", "บลู", "blue block", "blue cut", "บลูคัท", "ตาล้า", "แสบตา", "ตาแห้ง", "แพ้แสงหน้าจอ", "ปวดกระบอกตา", "ปวดตา", "ออฟฟิศ", "นั่งโต๊ะ"]):
        screen_reply = (
            "💻 สำหรับผู้ที่ 'ทำงานหน้าคอม จ้องจอนาน หรือเล่นเกม' โดยเสถียรการแว่นครับ:\n\n"
            "✨ แนะนำ: เลนส์กรองแสงสีฟ้า (Blue Block / Blue Control)\n"
            "• ช่วยตัดคลื่นแสงสีฟ้าพลังงานสูงจากหน้าจอมือถือและจอคอมพิวเตอร์\n"
            "• ลดอาการตาล้า แสบตา ตาแห้ง และช่วยให้นอนหลับได้สบายขึ้น\n"
            "• ภาพคมชัดสบายตา สีสันเป็นธรรมชาติ ไม่หลอกตา\n\n"
            "👓 คำแนะนำในการเลือกกรอบ:\n"
            "ควรเลือกกรอบแว่นน้ำหนักเบา (เช่น วัสดุ TR90 หรือไทเทเนียม) ที่ไม่บีบขมับและไม่กดแป้นจมูกเวลาใส่ทำงานต่อเนื่องหลายชั่วโมงครับ\n\n"
            "💡 ทริคดูแลตา (กฎ 20-20-20):\n"
            "ทุก 20 นาที ให้พักสายตามองไกล 20 ฟุต (6 เมตร) เป็นเวลา 20 วินาที จะช่วยคลายกล้ามเนื้อตาได้ดีมากครับ\n\n"
            "📍 แวะมาทดลองกรอบและตรวจวัดสายตาฟรีได้ที่:\n"
            "ศูนย์ราชการ อาคาร B ชั้น 1 (ตรงข้าม AIS)\n"
            "📞 สอบถามเลนส์และข้อมูล: 085-433-6699 (คุณนก), 092-393-7770 (คุณเสถียร)"
        )
        return TextMessage(text=screen_reply)

    # 11. Smart Optical Knowledge: ขับรถ / ขับรถกลางคืน / ออกแดด / ตาแพ้แสง
    elif any(k in msg_lower for k in ["ขับรถ", "กลางคืน", "แดด", "ออกแดด", "เปลี่ยนสี", "ออโต้", "auto", "กันแดด", "แสงจ้า", "ตาแพ้แสง", "สู้แดดไม่ไหว", "ไฟฟุ้ง", "ไฟแยงตา"]):
        driving_reply = (
            "🚗 สำหรับผู้ที่ 'ขับรถเป็นประจำ หรือตาแพ้แสงแดด' โดยเสถียรการแว่นครับ:\n\n"
            "✨ ขับรถตอนกลางคืน / เจอไฟหน้ารถแยงตา:\n"
            "• แนะนำ: เลนส์ Multicoat สารเคลือบตัดแสงสะท้อนรอบทิศทาง ช่วยลดแสงฟุ้งกระจายจากไฟหน้ารถและป้ายไฟ ทำให้มองทางคมชัดและปลอดภัยยิ่งขึ้น\n\n"
            "☀️ ขับรถกลางวัน / ออกแดดกลางแจ้ง:\n"
            "• แนะนำ: เลนส์ Auto Photochromic (ออกแดดเปลี่ยนสีอัจฉริยะ)\n"
            "  - อยู่ในร่มหรือในรถ: เลนส์ใส สบายตา\n"
            "  - ออกแดดกลางแจ้ง: เลนส์จะปรับเฉดสีเข้มขึ้นเป็นแว่นกันแดดอัตโนมัติ ป้องกันรังสี UV ได้ 100%\n\n"
            "📍 แวะเข้ามาตรวจเช็คค่าสายตาละเอียดได้ฟรีที่:\n"
            "ศูนย์ราชการ อาคาร B ชั้น 1 (ตรงข้าม AIS)\n"
            "📞 โทรปรึกษาคุณนก: 085-433-6699 หรือคุณเสถียร: 092-393-7770 ครับ"
        )
        return TextMessage(text=driving_reply)

    # 12. Smart Optical Knowledge: มองใกล้ไม่ชัด / วัย 40+ / อ่านหนังสือ / โปรเกรสซีฟ
    elif any(k in msg_lower for k in ["โปรเกรสซีฟ", "progressive", "สองชั้น", "มองใกล้", "มองไกล", "อ่านหนังสือ", "ยื่นแขน", "อายุ 40", "สายตายาว", "ยาวตามวัย", "ผู้สูงอายุ", "พ่อแม่", "วัยเกษียณ", "สลับแว่น", "ถอดแว่นอ่านหนังสือ"]):
        progressive_reply = (
            "👓 สำหรับผู้ที่มีอาการ 'เริ่มมองใกล้ไม่ชัด หรือวัย 40+' โดยเสถียรการแว่นครับ:\n\n"
            "ภาวะนี้เรียกว่า 'สายตายาวตามวัย' เกิดจากกล้ามเนื้อตาปรับโฟกัสใกล้ช้าลงตามธรรมชาติครับ:\n\n"
            "👑 เลนส์โปรเกรสซีฟ (Progressive Lens) - มองชัดครบทุกระยะ ไร้รอยต่อ:\n"
            "• มองไกล (ขับรถ/ดูทีวี) - ระยะกลาง (จอคอมพิวเตอร์) - ระยะใกล้ (อ่านหนังสือ/มือถือ) ได้ในแว่นตัวเดียว\n"
            "• เลนส์ใสเรียบเนียน ไร้รอยต่อ มองดูอ่อนกว่าวัยเหมือนแว่นสายตาทั่วไป ไม่ต้องคอยสลับแว่นหรือถอดแว่นเข้า-ออก\n\n"
            "✨ การตัดเลนส์โปรเกรสซีฟต้องอาศัยความชำนาญสูงมาก โดยที่ร้านจะได้รับการตรวจวัดและหาจุดกึ่งกลางตาดำ (PD) อย่างละเอียดโดย 'คุณเสถียร' ช่างผู้เชี่ยวชาญกว่า 30 ปีครับ\n\n"
            "📍 หน้าร้าน: ศูนย์ราชการ อาคาร B ชั้น 1 (ตรงข้าม AIS)\n"
            "📞 ปรึกษาคุณเสถียรโดยตรง: 092-393-7770, คุณนก: 085-433-6699"
        )
        return TextMessage(text=progressive_reply)

    # 13. Smart Optical Knowledge: สายตาสั้น / ยาว / เอียง ต่างกันอย่างไร
    elif any(k in msg_lower for k in ["สายตาสั้น", "สายตายาว", "สายตาเอียง", "เอียงคือ", "สั้นคือ", "เงาซ้อน", "มองไม่ชัด", "ภาพเบลอ", "ตาเอียง", "ภาพซ้อน"]):
        refraction_reply = (
            "🔍 ความแตกต่างของปัญหาสายตา โดยเสถียรการแว่นครับ:\n\n"
            "• สายตาสั้น (Myopia): มองวัตถุระยะไกลเบลอแต่มองใกล้ชัด มักเกิดจากกระบอกตายาวกว่าปกติ\n\n"
            "• สายตายาว (Hyperopia): กระบอกตาสั้น ทำให้ต้องเพ่งมองทั้งระยะใกล้และไกลจนเกิดอาการตาล้า\n\n"
            "• สายตาเอียง (Astigmatism): กระจกตามีความโค้งไม่เท่ากันในแต่ละแนว ทำให้จุดโฟกัสตกไม่พร้อมกัน มองเห็นเป็น 'เงาซ้อน หรือแสงไฟฟุ้งกระจาย' โดยเฉพาะเวลากลางคืน\n\n"
            "💡 อาการสายตาเอียงจำเป็นต้องตรวจวัดหา 'องศาเอียง (Axis)' ที่แม่นยำ เพื่อตัดแว่นแล้วใส่สบายตา ไม่เวียนหัวครับ\n\n"
            "📍 แวะมาตรวจวัดสายตาฟรีด้วยระบบคอมพิวเตอร์ได้ที่:\n"
            "ศูนย์ราชการ อาคาร B ชั้น 1 (ตรงข้าม AIS)\n"
            "📞 085-433-6699 (คุณนก), 092-393-7770 (คุณเสถียร)"
        )
        return TextMessage(text=refraction_reply)

    # 14. Smart Optical Knowledge: เลือกกรอบแว่นให้เข้ากับรูปหน้า
    elif any(k in msg_lower for k in ["เลือกกรอบ", "ทรงแว่น", "กรอบแว่น", "รูปหน้า", "หน้ากลม", "หน้าเหลี่ยม", "หน้ารูปไข่", "หน้ายาว", "กรอบแบบไหน", "เข้ากับหน้า", "กรอบหน้า"]):
        frame_reply = (
            "🎨 เทคนิคการเลือกกรอบแว่นให้เข้ากับรูปหน้า โดยเสถียรการแว่นครับ:\n\n"
            "• หน้ากลม: เหมาะกับกรอบทรงเหลี่ยม (Square / Wayfarer) หรือทรงหยดน้ำที่มีเหลี่ยมมุม เพื่อช่วยดึงให้ใบหน้าดูเรียวยาวขึ้น\n\n"
            "• หน้าเหลี่ยม: เหมาะกับกรอบทรงมน ทรงกลม หรือทรงหยดน้ำ ช่วยลดความคมของแนวกราม ให้หน้าดูนุ่มนวลขึ้น\n\n"
            "• หน้ารูปไข่: โชคดีมากครับ! สามารถใส่กรอบได้สวยแทบทุกทรง ทั้งทรงกลม เหลี่ยม และแคทอาย\n\n"
            "✨ คำแนะนำเรื่องวัสดุ: แนะนำกรอบ TR90 หรือไทเทเนียม น้ำหนักเบา ยืดหยุ่น ทนทาน ไม่กดดั้งจมูก\n\n"
            "📍 ทางร้านเสถียรการแว่นมีกรอบให้ลองสวมเทียบใบหน้าจริงมากกว่า 500 แบบ แวะมาลองสวมได้ที่ ศูนย์ราชการ อาคาร B ชั้น 1 ได้เลยครับ 😊"
        )
        return TextMessage(text=frame_reply)

    # 15. Smart Optical Knowledge: แว่นหลวม / ขาแว่นเอียง / แป้นจมูก / การดูแลรักษาแว่น
    elif any(k in msg_lower for k in ["แว่นหลวม", "แว่นเอียง", "แป้นจมูก", "ดัดแว่น", "ดัดทรง", "ซ่อมแว่น", "น็อตหลุด", "แว่นบีบ", "เจ็บดั้ง", "ล้างแว่น", "ทำความสะอาดแว่น", "เช็ดแว่น"]):
        care_reply = (
            "🛠️ การดูแลรักษาและปรับแต่งแว่นตา โดยเสถียรการแว่นครับ:\n\n"
            "• แว่นหลวม ไหลลงมาที่จมูก หรือขาแว่นเอียงข้างสูงต่ำไม่เท่ากัน: แวะนำแว่นเข้ามาให้ 'คุณเสถียร' ดัดปรับทรงและปรับแป้นจมูกให้กระชับใบหน้าได้ ฟรีตลอดชีพ ครับ!\n\n"
            "• แป้นจมูกเหลืองหรือกดทับดั้ง: ทางร้านมีบริการเปลี่ยนแป้นจมูกซิลิโคนนุ่มให้ฟรีครับ\n\n"
            "🧼 วิธีล้างทำความสะอาดเลนส์ที่ถูกต้อง:\n"
            "1. ใช้น้ำเปล่าไหลผ่านตัวแว่น\n"
            "2. ใช้น้ำยาล้างจานเจือจางลูบเบาๆ (ห้ามใช้สบู่หรือแอลกอฮอล์ เพราะจะกัดสารเคลือบเลนส์)\n"
            "3. ล้างน้ำให้สะอาด แล้วซับด้วยกระดาษทิชชูไร้ขนหรือผ้าไมโครไฟเบอร์\n\n"
            "📍 หน้าร้าน: ศูนย์ราชการ อาคาร B ชั้น 1 (ตรงข้าม AIS)\n"
            "📞 โทรหาคุณเสถียรได้เลยครับ: 092-393-7770"
        )
        return TextMessage(text=care_reply)

    # 16. Smart Optical Knowledge: ตัดแว่นใช้เวลากี่วัน / รอรับได้เลยไหม
    elif any(k in msg_lower for k in ["กี่วัน", "รอรับ", "รับแว่น", "ใช้เวลา", "ตัดนานไหม", "เสร็จกี่วัน", "วันเดียวได้ไหม", "รอรับได้ไหม"]):
        duration_reply = (
            "⏰ ระยะเวลาในการประกอบแว่นตา เสถียรการแว่นครับ:\n\n"
            "• เลนส์สายตาทั่วไป / เลนส์บลูคัทมาตรฐาน: หากมีค่าสายตาในสต็อก สามารถรอรับได้เลยภายใน 20 - 30 นาที หรือฝากส่ง Flash ถึงบ้านฟรีครับ\n\n"
            "• เลนส์สั่งผลิตพิเศษ / เลนส์โปรเกรสซีฟ: สั่งผลิตจากแล็บมาตรฐาน ใช้เวลาประมาณ 3 - 5 วันทำการ เพื่อความคมชัดและแม่นยำสูงสุดครับ\n\n"
            "✨ เมื่อแว่นตาตัดประกอบเสร็จแล้ว ทางร้านจะส่งข้อความแจ้งเตือนผ่าน LINE ให้ทราบทันทีครับ 👓\n\n"
            "📞 สอบถามสต็อกเลนส์: 085-433-6699 (คุณนก), 092-393-7770 (คุณเสถียร)"
        )
        return TextMessage(text=duration_reply)

    # 17. Smart Optical Knowledge: เด็กและวัยเรียน สายตาสั้นเร็ว
    elif any(k in msg_lower for k in ["เด็ก", "ลูก", "วัยรุ่น", "นักเรียน", "สั้นเร็ว", "ถนอมสายตาเด็ก", "ลูกสายตาสั้น"]):
        kids_reply = (
            "👧 คำแนะนำการดูแลสายตาเด็กและวัยเรียน โดยเสถียรการแว่นครับ:\n\n"
            "• เด็กวัยเรียนกระบอกตากำลังเจริญเติบโต แนะนำให้ตรวจวัดสายตาทุก 6 เดือน เพื่อเช็คว่าค่าสายตาเปลี่ยนหรือไม่\n"
            "• หากเล่นแท็บเล็ตหรือเรียนออนไลน์ ควรใช้เลนส์กรองแสงสีฟ้าเพื่อป้องกันอาการตาล้า\n"
            "• ควรเลือกกรอบแว่นซิลิโคนหรือ TR90 ที่ยืดหยุ่นสูง ตกไม่แตก ปลอดภัยสำหรับเด็ก\n"
            "• ส่งเสริมให้เด็กทำกิจกรรมกลางแจ้งรับแสงธรรมชาติวันละ 1-2 ชั่วโมง ช่วยชะลอสายตาสั้นได้ดีมากครับ\n\n"
            "📍 พาคุณน้องๆ หนูๆ มาตรวจวัดสายตาฟรีได้ที่ ศูนย์ราชการ อาคาร B ชั้น 1 (ตรงข้าม AIS) ได้เลยครับ 😊"
        )
        return TextMessage(text=kids_reply)

    # 18. Smart Greeting & Welcome (คำทักทาย)
    elif any(k in msg_lower for k in ["สวัสดี", "หวัดดี", "hello", "hi", "ดีครับ", "ดีค่ะ", "สอบถาม"]):
        greeting_reply = (
            "สวัสดีครับ! ยินดีต้อนรับสู่ 'ร้านแว่นตา เสถียรการแว่น' ครับ 😊👓\n\n"
            "ทางร้านยินดีให้คำปรึกษาเรื่องสายตา เลนส์ และการเลือกกรอบแว่นทุกชนิดครับ\n\n"
            "🏢 สาขา 1: ศูนย์ราชการเฉลิมพระเกียรติฯ แจ้งวัฒนะ อาคาร B ชั้น 1 (ตรงข้าม AIS)\n"
            "⏰ เปิดทำการ: จันทร์ - ศุกร์ ตามเวลาราชการ (08:30 - 15:00 น.)\n\n"
            "🏡 สาขา 2: สตูดิโอส่วนตัวที่บ้าน (The Plant-Light ติวานนท์-รังสิต ปทุมธานี)\n"
            "✨ ตรวจวัดสายตาละเอียดแบบ Private VIP (เปิดทุกวัน รวม ส.-อา. นัดล่วงหน้า)\n\n"
            "คุณลูกค้าสามารถแตะเมนูด้านล่าง หรือพิมพ์สอบถามเรื่องสายตาได้เลยครับ:\n"
            "• เช่น 'ทำงานหน้าคอมควรใส่แว่นแบบไหน'\n"
            "• 'ขับรถกลางคืนแสงไฟฟุ้ง'\n"
            "• 'มองใกล้ไม่ชัดต้องยื่นแขน'\n"
            "• 'ขอแผนที่ร้าน' หรือ 'จองคิวนัดตรวจ'\n\n"
            "📞 โทรติดต่อด่วน: 085-433-6699 (คุณนก), 092-393-7770 (คุณเสถียร) ได้ตลอดเวลาครับ!"
        )
        return TextMessage(text=greeting_reply)

    # 19. AI Consultation fallback via Gemini (พร้อมป้ายกำกับข้อความอัตโนมัติ)
    ai_answer = ask_gemini(user_msg)
    if ai_answer:
        ai_disclaimer = (
            "\n\n───────────────\n"
            "🤖 [ข้อความตอบกลับอัตโนมัติโดย AI ผู้ช่วยร้านเสถียรการแว่น]\n"
            "(ไม่ใช่ข้อความจากเจ้าของร้านโดยตรง หากต้องการติดต่อเจ้าหน้าที่ โทร: 085-433-6699, 092-393-7770)"
        )
        return TextMessage(text=f"{ai_answer}{ai_disclaimer}")

    # 20. General fallback
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

    # Instant admin push notification to Khun Nok and Khun Sathien
    try:
        order_dict = {
            "order_no": order_no,
            "customer_name": name,
            "phone": phone,
            "address": addr,
            "order_details": details
        }
        order_alert_flex = build_order_alert_flex(order_dict)
        notify_all_admins(
            alert_text=f"🚨 [มีออเดอร์ใหม่] คุณ {name} ({phone})\nที่อยู่: {addr}\nรหัส: {order_no}\nรายละเอียด: {details or 'ตัดประกอบแว่นตา'}",
            flex_message=order_alert_flex
        )
    except Exception as alert_err:
        print(f"[WARN] Failed to send admin order push alert: {alert_err}")

    return jsonify({"status": "ok", "order_no": order_no})

@app.route("/form/booking", methods=["GET"])
def booking_form():
    return render_template("booking_form.html")

@app.route("/api/submit_booking", methods=["POST"])
def submit_booking():
    data = request.json or {}
    name = data.get("customer_name", "").strip()
    phone = data.get("phone", "").strip()
    loc = data.get("preferred_location", "สตูดิโอที่บ้าน (The Plant-Light ติวานนท์-รังสิต ปทุมธานี)").strip()
    b_date = data.get("booking_date", "").strip()
    b_time = data.get("booking_time", "").strip()
    service = data.get("service_type", "ตรวจวัดสายตาประกอบแว่น").strip()
    notes = data.get("notes", "").strip()
    user_id = data.get("userId", "").strip()

    if not user_id:
        user_id = database.get_latest_line_user()

    if not name or not phone or not b_date:
        return jsonify({"status": "error", "message": "กรุณากรอกข้อมูลให้ครบถ้วน"}), 400

    booking_no = database.create_appointment(
        line_user_id=user_id,
        customer_name=name,
        phone=phone,
        preferred_location=loc,
        booking_date=b_date,
        booking_time=b_time,
        service_type=service,
        notes=notes
    )
    if user_id:
        database.link_user_phone(phone, user_id)

    # If LINE user ID exists, send push confirmation to customer
    if user_id:
        try:
            messaging_api = get_messaging_api()
            confirm_text = (
                f"✅ ร้านเสถียรการแว่น ได้รับข้อมูลการนัดหมายของคุณเรียบร้อยแล้วครับ!\n\n"
                f"รหัสนัดหมาย: #{booking_no}\n"
                f"คุณ: {name}\n"
                f"สถานที่: {loc}\n"
                f"วันที่: {b_date} ({b_time})\n"
                f"บริการ: {service}\n\n"
                f"คุณเสถียรหรือคุณนกจะโทรยืนยันเวลาเพื่อเตรียมการต้อนรับอย่างดีที่สุดครับ 👓"
            )
            messaging_api.push_message(PushMessageRequest(to=user_id, messages=[TextMessage(text=confirm_text)]))
        except Exception as e:
            print(f"[WARN] Failed to push booking confirmation to user: {e}")

    # Instant push alert to all registered admins
    try:
        booking_data = {
            "booking_no": booking_no,
            "customer_name": name,
            "phone": phone,
            "preferred_location": loc,
            "booking_date": b_date,
            "booking_time": b_time,
            "service_type": service,
            "notes": notes
        }
        alert_flex = build_appointment_alert_flex(booking_data)
        notify_all_admins(
            alert_text=f"🔔 [มีการนัดหมายใหม่!] คุณ {name} ({phone})\nสถานที่: {loc}\nวันที่: {b_date} ({b_time})\nบริการ: {service}",
            flex_message=alert_flex
        )
    except Exception as e:
        print(f"[WARN] Failed to notify admins of appointment: {e}")

    return jsonify({"status": "ok", "booking_no": booking_no})

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
    admin_subscribers = database.get_all_admin_subscribers()
    appointments = database.get_recent_appointments()

    completed_orders = sum(1 for o in orders if "เสร็จ" in o.get("status", "") or "จัดส่ง" in o.get("status", "") or "ส่งมอบ" in o.get("status", ""))
    pending_orders = len(orders) - completed_orders
    pending_appointments = sum(1 for a in appointments if a.get("status") == "รอยืนยันนัดหมาย")

    stats = {
        "total_orders": len(orders),
        "pending_orders": pending_orders,
        "completed_orders": completed_orders,
        "total_promos": len(promotions),
        "total_rx": len(prescriptions),
        "total_schedules": len(schedules),
        "total_subscribers": len([s for s in admin_subscribers if s.get("is_active")]),
        "total_appointments": len(appointments),
        "pending_appointments": pending_appointments
    }

    return render_template(
        "admin_dashboard.html",
        orders=orders,
        schedules=schedules,
        prescriptions=prescriptions,
        promotions=promotions,
        admin_subscribers=admin_subscribers,
        appointments=appointments,
        stats=stats
    )

@app.route("/admin/update_appointment", methods=["POST"])
@admin_required
def update_appointment_route():
    app_id = request.form.get("appointment_id")
    status = request.form.get("status", "").strip()
    if app_id and status:
        database.update_appointment_status(int(app_id), status)
    return redirect("/admin#appointments")

@app.route("/admin/delete_appointment", methods=["POST"])
@admin_required
def delete_appointment_route():
    app_id = request.form.get("appointment_id")
    if app_id:
        database.delete_appointment(int(app_id))
    return redirect("/admin#appointments")

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

@app.route("/admin/delete_subscriber", methods=["POST"])
@admin_required
def delete_subscriber_route():
    sub_id = request.form.get("subscriber_id")
    if sub_id:
        database.delete_admin_subscriber(int(sub_id))
    return redirect("/admin")

@app.route("/admin/test_notify", methods=["POST"])
@admin_required
def test_notify_route():
    try:
        count = notify_all_admins(
            alert_text="🧪 [ทดสอบระบบแจ้งเตือนร้านเสถียรการแว่น]\nการเชื่อมต่อสมบูรณ์! เมื่อมีออเดอร์ใหม่หรือลูกค้าขอสลิป ข้อความจะเด้งเข้า LINE นี้ทันทีครับ 👓"
        )
        return jsonify({"status": "ok", "sent_count": count})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

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
