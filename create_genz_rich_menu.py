import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_genz_menu():
    width = 2500
    height = 1686

    # Sleek Cyber Minimal Dark Canvas
    bg = Image.new('RGB', (width, height), color='#0A0E17')
    draw = ImageDraw.Draw(bg)

    # Ambient Cyber Bloom Lights in background
    bloom_canvas = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(bloom_canvas)
    blooms = [
        (400, 350, 360, (255, 94, 58, 80)),    # Neon Orange
        (1250, 350, 380, (0, 245, 160, 80)),   # Acid Lime / Emerald
        (2100, 350, 360, (0, 180, 255, 90)),   # Cyan Blue
        (400, 1300, 360, (138, 35, 135, 80)),  # Cyber Purple
        (1250, 1300, 380, (255, 0, 127, 90)),  # Neon Pink
        (2100, 1300, 360, (255, 65, 108, 80))  # Flame Red
    ]
    for bx, by, br, bcolor in blooms:
        b_draw.ellipse([bx-br, by-br, bx+br, by+br], fill=bcolor)
    bloom_canvas = bloom_canvas.filter(ImageFilter.GaussianBlur(100))
    bg.paste(bloom_canvas, (0, 0), bloom_canvas)

    # Fonts
    font_bold_path = "C:/Windows/Fonts/leelawadb.ttf"
    font_path = "C:/Windows/Fonts/leelawad.ttf"
    if not os.path.exists(font_bold_path):
        font_bold_path = font_path

    # GEN Z TYPOGRAPHY - BOLD, CLEAN, ULTRA CRISP
    font_title = ImageFont.truetype(font_bold_path, 114)     # Big Punchy Title
    font_sub = ImageFont.truetype(font_bold_path, 54)        # Clean Crisp Subtext
    font_badge = ImageFont.truetype(font_bold_path, 42)      # Badge text
    font_emoji = ImageFont.truetype(font_bold_path, 128)     # Big 3D Icon
    font_btn = ImageFont.truetype(font_bold_path, 50)        # Action button

    # Load Owl Mascot
    owl_img = None
    if os.path.exists("owl_mascot.png"):
        try:
            owl_img = Image.open("owl_mascot.png").convert("RGBA")
        except Exception:
            owl_img = None

    # Grid
    col_x = [0, 833, 1667, 2500]
    row_y = [0, 843, 1686]
    pad = 18

    # 6 SHORT, PUNCHY, GEN Z TILES
    tiles = [
        # Tile 1: บูทสัญจร
        {
            "col": 0, "row": 0,
            "badge": "🎪 POP-UP EVENT",
            "emoji": "📍",
            "title": "บูทสัญจร",
            "desc": "เช็กจุดออกบูทวันนี้\nสัปดาห์นี้พ่อไปงานไหน",
            "grad1": (255, 94, 58), "grad2": (235, 47, 6),
            "border": "#FF7A59",
            "btn_text": "ดูพิกัดบูท ➔",
            "btn_bg": "#FFFFFF",
            "btn_fg": "#EB2F06",
            "use_owl": False
        },
        # Tile 2: แผนที่ร้านหลัก (ตรงข้าม AIS)
        {
            "col": 1, "row": 0,
            "badge": "📍 GOOGLE MAPS",
            "emoji": "🗺️",
            "title": "แผนที่ร้าน",
            "desc": "ชั้นล่าง อาคาร B ตรงข้าม AIS\n(แตะเปิดแผนที่นำทางทันที)",
            "grad1": (0, 245, 160), "grad2": (0, 168, 120),
            "border": "#5CFDC7",
            "btn_text": "เปิด MAPS 📍",
            "btn_bg": "#FEF08A",
            "btn_fg": "#065F46",
            "use_owl": False
        },
        # Tile 3: เช็กสถานะ
        {
            "col": 2, "row": 0,
            "badge": "📦 FAST DELIVERY",
            "emoji": "🚚",
            "title": "เช็กสถานะ",
            "desc": "แว่นเสร็จยัง / เลข Flash\nหรือกรอกที่อยู่จัดส่งฟรี",
            "grad1": (56, 161, 243), "grad2": (17, 98, 222),
            "border": "#7CC4FD",
            "btn_text": "เช็กสถานะ ➔",
            "btn_bg": "#FFFFFF",
            "btn_fg": "#1162DE",
            "use_owl": False
        },
        # Tile 4: สลิปสายตา
        {
            "col": 0, "row": 1,
            "badge": "👓 DIGITAL RECORD",
            "emoji": "📄",
            "title": "สลิปสายตา",
            "desc": "ดูประวัติวัดสายตา\nสลิปจากคอมเครื่องวัด",
            "grad1": (168, 85, 247), "grad2": (109, 40, 217),
            "border": "#D8B4FE",
            "btn_text": "ดูสลิปสายตา ➔",
            "btn_bg": "#FFFFFF",
            "btn_fg": "#6D28D9",
            "use_owl": False
        },
        # Tile 5: บริการหลังขาย (Owl Mascot)
        {
            "col": 1, "row": 1,
            "badge": "🦉 SATIEN CARE",
            "emoji": "🛠️",
            "title": "บริการหลังขาย",
            "desc": "มีปัญหาแว่นไม่กระชับ\nติดต่อ คุณเสถียร ได้เลย",
            "grad1": (244, 63, 134), "grad2": (190, 24, 93),
            "border": "#F472B6",
            "btn_text": "โทรคุณเสถียร 📞",
            "btn_bg": "#FEF08A",
            "btn_fg": "#9D174D",
            "use_owl": True
        },
        # Tile 6: โทรด่วน
        {
            "col": 2, "row": 1,
            "badge": "⚡ CALL STORE",
            "emoji": "📞",
            "title": "โทรด่วน",
            "desc": "• คุณนก: 085-433-6699\n• คุณเสถียร: 092-393-7770",
            "grad1": (239, 68, 68), "grad2": (185, 28, 28),
            "border": "#FCA5A5",
            "btn_text": "โทรหาร้าน ➔",
            "btn_bg": "#FFFFFF",
            "btn_fg": "#991B1B",
            "use_owl": False
        }
    ]

    for tile in tiles:
        c = tile["col"]
        r = tile["row"]
        x1 = col_x[c] + pad
        y1 = row_y[r] + pad
        x2 = col_x[c+1] - pad
        y2 = row_y[r+1] - pad
        w = x2 - x1
        h = y2 - y1

        # 1. Gradient Card
        card = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        c_draw = ImageDraw.Draw(card)
        g1, g2 = tile["grad1"], tile["grad2"]
        for y in range(h):
            ratio = y / float(h)
            cr = int(g1[0] * (1 - ratio) + g2[0] * ratio)
            cg = int(g1[1] * (1 - ratio) + g2[1] * ratio)
            cb = int(g1[2] * (1 - ratio) + g2[2] * ratio)
            c_draw.line([(0, y), (w, y)], fill=(cr, cg, cb, 255))
        
        # Rounded mask
        mask = Image.new('L', (w, h), 0)
        m_draw = ImageDraw.Draw(mask)
        m_draw.rounded_rectangle([0, 0, w, h], radius=50, fill=255)
        
        # Specular Highlight Arc
        hl = Image.new('RGBA', (w, h), (0, 0, 0, 0))
        hl_draw = ImageDraw.Draw(hl)
        hl_draw.ellipse([-w*0.2, -h*0.4, w*1.2, h*0.5], fill=(255, 255, 255, 55))
        card.paste(hl, (0, 0), hl)

        # Borders
        c_draw.rounded_rectangle([3, 3, w-4, h-4], radius=50, outline=tile["border"], width=7)
        c_draw.rounded_rectangle([10, 10, w-11, h-11], radius=43, outline=(255, 255, 255, 100), width=3)
        bg.paste(card, (x1, y1), mask)

        # 2. Sleek Pill Badge (Top Left)
        bx1 = x1 + 36
        by1 = y1 + 32
        badge_w = 380
        badge_h = 62
        draw.rounded_rectangle([bx1+3, by1+4, bx1+badge_w+3, by1+badge_h+4], radius=31, fill="#000000")
        draw.rounded_rectangle([bx1, by1, bx1+badge_w, by1+badge_h], radius=31, fill="#0B0F19", outline="#FFFFFF", width=3)
        draw.text((bx1 + 24, by1 + 9), tile["badge"], fill="#FFFFFF", font=font_badge)

        # 3. Big Icon Container
        ic_center_x = x1 + 150
        ic_center_y = y1 + 250
        ic_r = 95
        draw.ellipse([ic_center_x - ic_r + 4, ic_center_y - ic_r + 6, ic_center_x + ic_r + 4, ic_center_y + ic_r + 6], fill=(0, 0, 0, 130))
        draw.ellipse([ic_center_x - ic_r, ic_center_y - ic_r, ic_center_x + ic_r, ic_center_y + ic_r], fill="#FFFFFF", outline=tile["border"], width=6)

        if tile["use_owl"] and owl_img is not None:
            owl_thumb = owl_img.resize((158, 202), Image.Resampling.LANCZOS)
            bg.paste(owl_thumb, (ic_center_x - 79, ic_center_y - 101), owl_thumb)
        else:
            draw.text((ic_center_x - 62, ic_center_y - 82), tile["emoji"], fill="#0F172A", font=font_emoji)

        # 4. HUGE PUNCHY TITLE (114px with drop shadow)
        tx = x1 + 275
        ty = y1 + 195
        # Shadow
        draw.text((tx + 4, ty + 5), tile["title"], fill="#000000", font=font_title)
        # Main text in Pure White
        draw.text((tx, ty), tile["title"], fill="#FFFFFF", font=font_title)

        # 5. Clean Divider Line
        divider_y = y1 + 380
        draw.line([x1 + 38, divider_y, x2 - 38, divider_y], fill=(255, 255, 255, 120), width=4)

        # 6. CRISP SUBTITLE (54px Bold)
        draw.multiline_text((x1 + 45 + 3, y1 + 415 + 3), tile["desc"], fill="#000000", font=font_sub, spacing=18)
        draw.multiline_text((x1 + 45, y1 + 415), tile["desc"], fill="#FFFFFF", font=font_sub, spacing=18)

        # 7. HIGH-CONTRAST CANDY BUTTON PILL
        btn_y1 = y2 - 145
        btn_y2 = y2 - 40
        btn_x1 = x1 + 38
        btn_x2 = x2 - 38
        
        # Shadow
        draw.rounded_rectangle([btn_x1 + 4, btn_y1 + 5, btn_x2 + 4, btn_y2 + 5], radius=32, fill="#000000")
        # Pill Base
        draw.rounded_rectangle([btn_x1, btn_y1, btn_x2, btn_y2], radius=32, fill=tile["btn_bg"], outline="#FFFFFF", width=3)
        # Gloss
        draw.rounded_rectangle([btn_x1 + 8, btn_y1 + 4, btn_x2 - 8, btn_y1 + 24], radius=16, fill=(255, 255, 255, 160))
        # Button Text
        draw.text((btn_x1 + 180, btn_y1 + 24), tile["btn_text"], fill=tile["btn_fg"], font=font_btn)

    # Save
    out_path = os.path.join(os.getcwd(), "rich_menu_genz.png")
    bg.save(out_path, "PNG", quality=95)
    print(f"Gen Z Vibrant Rich Menu created successfully at: {out_path}")

if __name__ == "__main__":
    create_genz_menu()
