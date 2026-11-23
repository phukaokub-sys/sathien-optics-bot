import os
from PIL import Image, ImageDraw, ImageFont

def create_rich_menu():
    width = 2500
    height = 1686
    img = Image.new('RGB', (width, height), color='#0B132B')
    draw = ImageDraw.Draw(img)

    # Fonts
    font_path = "C:/Windows/Fonts/leelawad.ttf"
    font_bold_path = "C:/Windows/Fonts/leelawadb.ttf"
    if not os.path.exists(font_bold_path):
        font_bold_path = font_path

    try:
        font_brand = ImageFont.truetype(font_bold_path, 54)
        font_title = ImageFont.truetype(font_bold_path, 60)
        font_sub = ImageFont.truetype(font_path, 38)
        font_badge = ImageFont.truetype(font_bold_path, 34)
        font_emoji = ImageFont.truetype(font_bold_path, 72)
    except Exception as e:
        font_brand = ImageFont.load_default()
        font_title = font_brand
        font_sub = font_brand
        font_badge = font_brand
        font_emoji = font_brand

    # Grid specifications (3 columns x 2 rows)
    col_w = [833, 834, 833]
    col_x = [0, 833, 1667, 2500]
    row_h = 843
    row_y = [0, 843, 1686]

    # Tiles configuration
    tiles = [
        # Row 1
        {
            "col": 0, "row": 0,
            "badge": "EVENT & BOOTH",
            "badge_bg": "#1D4ED8",
            "icon_text": "📍",
            "title": "พิกัดบูทสัปดาห์นี้",
            "desc": "เช็กจุดออกบูทของคุณพ่อ\nโทรสอบถามพิกัดหน้างาน",
            "bg": "#111D4A",
            "accent": "#3B82F6"
        },
        {
            "col": 1, "row": 0,
            "badge": "MAIN STORE",
            "badge_bg": "#059669",
            "icon_text": "🏢",
            "title": "ร้านประจำ อาคาร B",
            "desc": "ชั้นล่าง ตรงข้าม Telewiz\nเปิดถึง 15:30 น. (มีแผนที่)",
            "bg": "#0D2818",
            "accent": "#10B981"
        },
        {
            "col": 2, "row": 0,
            "badge": "ORDER & DELIVERY",
            "badge_bg": "#D97706",
            "icon_text": "📦",
            "title": "ติดตามแว่น / พัสดุ",
            "desc": "เช็กเลขพัสดุ Flash Express\nหรือนัดรับแว่นส่งถึงมือ",
            "bg": "#2A1805",
            "accent": "#F59E0B"
        },
        # Row 2
        {
            "col": 0, "row": 1,
            "badge": "PRESCRIPTION",
            "badge_bg": "#7C3AED",
            "icon_text": "👓",
            "title": "สลิปค่าสายตา",
            "desc": "บันทึกประวัติค่าสายตา\nใบเสร็จและการรับประกัน",
            "bg": "#1E1238",
            "accent": "#8B5CF6"
        },
        {
            "col": 1, "row": 1,
            "badge": "AFTER-SALES CARE",
            "badge_bg": "#0284C7",
            "icon_text": "✨",
            "title": "บริการดูแลแว่นฟรี",
            "desc": "ล้างแว่นด้วยอัลตราโซนิก\nดัดทรง & เปลี่ยนแป้นจมูกฟรี",
            "bg": "#082136",
            "accent": "#0EA5E9"
        },
        {
            "col": 2, "row": 1,
            "badge": "DIRECT CONTACT",
            "badge_bg": "#DC2626",
            "icon_text": "📞",
            "title": "โทรติดต่อร้าน",
            "desc": "085-433-6699 (คุณนก)\n092-393-7770 (คุณเสถียร)",
            "bg": "#2E0E0E",
            "accent": "#EF4444"
        }
    ]

    padding = 24
    corner_radius = 28

    for tile in tiles:
        c = tile["col"]
        r = tile["row"]
        x1 = col_x[c] + padding
        y1 = row_y[r] + padding
        x2 = col_x[c+1] - padding
        y2 = row_y[r+1] - padding

        # Card Background
        draw.rounded_rectangle([x1, y1, x2, y2], radius=corner_radius, fill=tile["bg"], outline="#334155", width=3)

        # Top Accent Line
        draw.rounded_rectangle([x1 + 30, y1 + 18, x2 - 30, y1 + 26], radius=4, fill=tile["accent"])

        # Badge
        badge_w = 260
        badge_h = 46
        bx1 = x1 + 40
        by1 = y1 + 50
        draw.rounded_rectangle([bx1, by1, bx1 + badge_w, by1 + badge_h], radius=12, fill=tile["badge_bg"])
        draw.text((bx1 + 16, by1 + 6), tile["badge"], fill="#FFFFFF", font=font_badge)

        # Icon Circle
        ic_center_x = x1 + 120
        ic_center_y = y1 + 240
        ic_r = 75
        draw.ellipse([ic_center_x - ic_r, ic_center_y - ic_r, ic_center_x + ic_r, ic_center_y + ic_r], 
                     fill="#1E293B", outline=tile["accent"], width=4)
        draw.text((ic_center_x - 36, ic_center_y - 48), tile["icon_text"], fill="#FFFFFF", font=font_emoji)

        # Title
        tx = x1 + 230
        ty = y1 + 205
        draw.text((tx, ty), tile["title"], fill="#FFFFFF", font=font_title)

        # Divider
        draw.line([x1 + 40, y1 + 370, x2 - 40, y1 + 370], fill="#334155", width=2)

        # Description
        draw.multiline_text((x1 + 50, y1 + 410), tile["desc"], fill="#CBD5E1", font=font_sub, spacing=20)

        # Action Prompt button inside card
        btn_y1 = y2 - 120
        btn_y2 = y2 - 40
        btn_x1 = x1 + 40
        btn_x2 = x2 - 40
        draw.rounded_rectangle([btn_x1, btn_y1, btn_x2, btn_y2], radius=16, fill="#1E293B", outline=tile["accent"], width=2)
        btn_text = "แตะเพื่อเลือก  ➔"
        draw.text((btn_x1 + 220, btn_y1 + 16), btn_text, fill=tile["accent"], font=font_sub)

    # Save final image
    output_path = os.path.join(os.getcwd(), "rich_menu_sathien.png")
    img.save(output_path, "PNG", quality=95)
    print(f"Rich Menu successfully saved to {output_path}")

if __name__ == "__main__":
    create_rich_menu()
