import os
from PIL import Image, ImageDraw, ImageFont

def draw_bubble_card(draw, box, fill_color, border_color, radius=36, border_width=6):
    x1, y1, x2, y2 = box
    # Draw soft shadow
    draw.rounded_rectangle([x1+8, y1+10, x2+8, y2+10], radius=radius, fill="#E2E8F0")
    # Draw main card
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill=fill_color, outline=border_color, width=border_width)

def create_cartoon_rich_menu():
    width = 2500
    height = 1686
    # Friendly warm background
    img = Image.new('RGB', (width, height), color='#FFFDF7')
    draw = ImageDraw.Draw(img)

    # Decorative background dots/stripes
    for x in range(0, width, 80):
        for y in range(0, height, 80):
            draw.ellipse([x-2, y-2, x+2, y+2], fill="#F1F5F9")

    # Fonts
    font_bold_path = "C:/Windows/Fonts/leelawadb.ttf"
    font_path = "C:/Windows/Fonts/leelawad.ttf"
    if not os.path.exists(font_bold_path):
        font_bold_path = font_path

    font_title = ImageFont.truetype(font_bold_path, 68)
    font_sub = ImageFont.truetype(font_path, 40)
    font_badge = ImageFont.truetype(font_bold_path, 36)
    font_emoji = ImageFont.truetype(font_bold_path, 88)
    font_btn = ImageFont.truetype(font_bold_path, 42)

    # Grid specifications (3 columns x 2 rows)
    col_x = [0, 833, 1667, 2500]
    row_y = [0, 843, 1686]

    tiles = [
        # Row 1
        {
            "col": 0, "row": 0,
            "badge": "🎪 บูทคุณพ่อสัญจร",
            "badge_bg": "#EA580C",
            "emoji": "📍",
            "title": "พิกัดบูทวันนี้",
            "desc": "เช็กจุดออกบูทสัปดาห์นี้\nโทรสอบถามคุณพ่อโดยตรง",
            "bg": "#FFF7ED",      # Warm Cream Orange
            "border": "#FDBA74",
            "accent": "#EA580C",
            "btn_bg": "#FFEDD5"
        },
        {
            "col": 1, "row": 0,
            "badge": "🏬 สาขาประจำ อาคาร B",
            "badge_bg": "#059669",
            "emoji": "🏢",
            "title": "แผนที่ร้านหลัก",
            "desc": "ชั้นล่าง ตรงข้าม Telewiz\nศูนย์ราชการฯ ปิด 15:30",
            "bg": "#ECFDF5",      # Mint Green
            "border": "#6EE7B7",
            "accent": "#059669",
            "btn_bg": "#D1FAE5"
        },
        {
            "col": 2, "row": 0,
            "badge": "🚚 ส่งฟรีถึงบ้าน",
            "badge_bg": "#2563EB",
            "emoji": "📦",
            "title": "ติดตามแว่นตา",
            "desc": "กรอกที่อยู่จัดส่งพัสดุ\nหรือเช็กเลข Flash Express",
            "bg": "#EFF6FF",      # Soft Sky Blue
            "border": "#93C5FD",
            "accent": "#2563EB",
            "btn_bg": "#DBEAFE"
        },
        # Row 2
        {
            "col": 0, "row": 1,
            "badge": "🤓 บันทึกประวัติ",
            "badge_bg": "#7C3AED",
            "emoji": "👓",
            "title": "สลิปค่าสายตา",
            "desc": "ดูรูปสลิปจากเครื่องวัด\nเก็บประวัติใช้ตัดแว่นครั้งหน้า",
            "bg": "#FAF5FF",      # Lavender
            "border": "#C4B5FD",
            "accent": "#7C3AED",
            "btn_bg": "#EDE9FE"
        },
        {
            "col": 1, "row": 1,
            "badge": "✨ สิทธิพิเศษฟรี",
            "badge_bg": "#0D9488",
            "emoji": "🧼",
            "title": "บริการดูแลฟรี",
            "desc": "ล้างอัลตราโซนิก ดัดทรง\nเปลี่ยนแป้นจมูกฟรีตลอดชีพ",
            "bg": "#F0FDFA",      # Clean Aqua
            "border": "#5EEAD4",
            "accent": "#0D9488",
            "btn_bg": "#CCFBF1"
        },
        {
            "col": 2, "row": 1,
            "badge": "❤️ ยินดีต้อนรับครับ",
            "badge_bg": "#E11D48",
            "emoji": "📞",
            "title": "โทรหาร้าน",
            "desc": "085-433-6699 (คุณนก)\n092-393-7770 (คุณเสถียร)",
            "bg": "#FFF1F2",      # Rose Peach
            "border": "#FDA4AF",
            "accent": "#E11D48",
            "btn_bg": "#FFE4E6"
        }
    ]

    padding = 20

    for tile in tiles:
        c = tile["col"]
        r = tile["row"]
        x1 = col_x[c] + padding
        y1 = row_y[r] + padding
        x2 = col_x[c+1] - padding
        y2 = row_y[r+1] - padding

        # Draw cute bubbly card
        draw_bubble_card(draw, [x1, y1, x2, y2], tile["bg"], tile["border"], radius=42, border_width=5)

        # Draw cute top badge pill
        badge_text = tile["badge"]
        badge_w = 340
        badge_h = 56
        bx1 = x1 + 35
        by1 = y1 + 38
        draw.rounded_rectangle([bx1, by1, bx1 + badge_w, by1 + badge_h], radius=28, fill=tile["badge_bg"])
        draw.text((bx1 + 24, by1 + 6), badge_text, fill="#FFFFFF", font=font_badge)

        # Cute Circle Icon background
        ic_center_x = x1 + 130
        ic_center_y = y1 + 225
        ic_r = 78
        draw.ellipse([ic_center_x - ic_r + 4, ic_center_y - ic_r + 4, ic_center_x + ic_r + 4, ic_center_y + ic_r + 4], fill="#CBD5E1")
        draw.ellipse([ic_center_x - ic_r, ic_center_y - ic_r, ic_center_x + ic_r, ic_center_y + ic_r], 
                     fill="#FFFFFF", outline=tile["border"], width=5)
        draw.text((ic_center_x - 44, ic_center_y - 56), tile["emoji"], fill="#1E293B", font=font_emoji)

        # Title
        tx = x1 + 240
        ty = y1 + 190
        draw.text((tx, ty), tile["title"], fill="#1E293B", font=font_title)

        # Cute dotted divider line
        line_y = y1 + 345
        for lx in range(x1 + 40, x2 - 40, 18):
            draw.ellipse([lx, line_y, lx + 8, line_y + 8], fill=tile["border"])

        # Description
        draw.multiline_text((x1 + 45, y1 + 380), tile["desc"], fill="#475569", font=font_sub, spacing=16)

        # Bottom Button Pill "กดตรงนี้เลย 👆"
        btn_y1 = y2 - 130
        btn_y2 = y2 - 45
        btn_x1 = x1 + 40
        btn_x2 = x2 - 40
        draw.rounded_rectangle([btn_x1 + 4, btn_y1 + 4, btn_x2 + 4, btn_y2 + 4], radius=26, fill="#E2E8F0")
        draw.rounded_rectangle([btn_x1, btn_y1, btn_x2, btn_y2], radius=26, fill=tile["btn_bg"], outline=tile["accent"], width=3)
        btn_label = "แตะเพื่อเลือก ➔"
        draw.text((btn_x1 + 200, btn_y1 + 20), btn_label, fill=tile["accent"], font=font_btn)

    # Save final image
    output_path = os.path.join(os.getcwd(), "rich_menu_cartoon.png")
    img.save(output_path, "PNG", quality=95)
    print(f"Cartoon Rich Menu successfully created at {output_path}")

if __name__ == "__main__":
    create_cartoon_rich_menu()
