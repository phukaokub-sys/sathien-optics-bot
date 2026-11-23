import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_gradient_card(w, h, color1, color2, radius=48):
    card = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    draw = ImageDraw.Draw(card)
    
    # Smooth vertical/diagonal gradient
    for y in range(h):
        ratio = y / float(h)
        r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
        g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
        b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
        draw.line([(0, y), (w, y)], fill=(r, g, b, 255))
        
    # Mask to rounded rectangle
    mask = Image.new('L', (w, h), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, w, h], radius=radius, fill=255)
    
    # Modern Glass/Gloss Top Arc
    highlight = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    hl_draw = ImageDraw.Draw(highlight)
    hl_draw.ellipse([-w*0.3, -h*0.5, w*1.3, h*0.48], fill=(255, 255, 255, 45))
    
    card.paste(highlight, (0, 0), highlight)
    return card, mask

def generate_vibrant_cool_menu():
    width = 2500
    height = 1686

    # Modern Dark Obsidian / Carbon Background with vibrant energy
    bg = Image.new('RGB', (width, height), color='#0F172A')
    draw = ImageDraw.Draw(bg)

    # Grid specifications (3 columns x 2 rows)
    col_x = [0, 833, 1667, 2500]
    row_y = [0, 843, 1686]
    pad = 18

    # Fonts
    font_bold_path = "C:/Windows/Fonts/leelawadb.ttf"
    font_path = "C:/Windows/Fonts/leelawad.ttf"
    if not os.path.exists(font_bold_path):
        font_bold_path = font_path

    # MUCH LARGER FONTS FOR ULTRA-CLEAR MOBILE READABILITY
    font_title = ImageFont.truetype(font_bold_path, 98)      # Big bold title
    font_sub = ImageFont.truetype(font_bold_path, 52)        # Big bold subtext
    font_badge = ImageFont.truetype(font_bold_path, 40)      # Punchy badge
    font_emoji = ImageFont.truetype(font_bold_path, 120)     # Big 3D emoji
    font_btn = ImageFont.truetype(font_bold_path, 46)        # Large button text

    # Owl mascot
    owl_img = None
    if os.path.exists("owl_mascot.png"):
        try:
            owl_img = Image.open("owl_mascot.png").convert("RGBA")
        except Exception:
            owl_img = None

    # 6 VIBRANT, HIGH-CONTRAST, COOL GRAPHIC TILES
    tiles = [
        # Tile 1: พิกัดบูทวันนี้ (Electric Sunset Orange)
        {
            "col": 0, "row": 0,
            "badge": "🎪 บูทคุณพ่อสัญจร",
            "emoji": "📍",
            "title": "พิกัดบูทวันนี้",
            "desc": "เช็กจุดออกบูทสัปดาห์นี้\nโทรสอบถามคุณเสถียร",
            "gradient": [(249, 115, 22), (194, 65, 12)],    # Vivid Orange
            "border": "#FDBA74",
            "btn_text": "แตะเช็กพิกัด ➔",
            "btn_bg": "#FFFFFF",
            "btn_color": "#C2410C",
            "use_owl": False
        },
        # Tile 2: แผนที่ร้านหลัก (Neon Emerald Green)
        {
            "col": 1, "row": 0,
            "badge": "🏬 ศูนย์ราชการ อาคาร B",
            "emoji": "🗺️",
            "title": "แผนที่ร้านหลัก",
            "desc": "ชั้นล่าง ตรงข้าม Telewiz\n(แตะเปิด Google Maps)",
            "gradient": [(16, 185, 129), (4, 120, 87)],     # Emerald Green
            "border": "#6EE7B7",
            "btn_text": "เปิด Google Maps 📍",
            "btn_bg": "#FEF08A",                             # Bright Yellow pill
            "btn_color": "#065F46",
            "use_owl": False
        },
        # Tile 3: ติดตามแว่นตา (Cyber Electric Blue)
        {
            "col": 2, "row": 0,
            "badge": "🚚 ส่งพัสดุถึงบ้านฟรี",
            "emoji": "📦",
            "title": "ติดตามแว่นตา",
            "desc": "กรอกที่อยู่จัดส่งพัสดุ\nหรือเช็กเลข Flash",
            "gradient": [(59, 130, 246), (29, 78, 216)],    # Royal Blue
            "border": "#93C5FD",
            "btn_text": "กรอกที่อยู่ / สถานะ ➔",
            "btn_bg": "#FFFFFF",
            "btn_color": "#1D4ED8",
            "use_owl": False
        },
        # Tile 4: สลิปค่าสายตา (Deep Ultra Violet / Purple)
        {
            "col": 0, "row": 1,
            "badge": "👓 บันทึกประวัติสายตา",
            "emoji": "📄",
            "title": "สลิปค่าสายตา",
            "desc": "ดูรูปสลิปจากคอมพิวเตอร์\nเก็บไว้ใช้อ้างอิงตลอดชีพ",
            "gradient": [(147, 51, 234), (107, 33, 168)],  # Vivid Purple
            "border": "#C4B5FD",
            "btn_text": "ดูสลิปสายตา ➔",
            "btn_bg": "#FFFFFF",
            "btn_color": "#6B21A8",
            "use_owl": False
        },
        # Tile 5: บริการหลังการขาย (Brand Magenta Pink featuring the Owl mascot!)
        {
            "col": 1, "row": 1,
            "badge": "🦉 ดูแลใส่ใจบริการ",
            "emoji": "🛠️",
            "title": "บริการหลังการขาย",
            "desc": "หากมีปัญหาการใช้งาน\nติดต่อ คุณเสถียร ได้เลย",
            "gradient": [(236, 72, 153), (190, 24, 93)],   # Magenta Pink matching Logo
            "border": "#FBCFE8",
            "btn_text": "โทรหาคุณเสถียร 📞",
            "btn_bg": "#FEF08A",                            # Bright Yellow pill
            "btn_color": "#9D174D",
            "use_owl": True
        },
        # Tile 6: โทรติดต่อร้าน (Flaming Crimson Red)
        {
            "col": 2, "row": 1,
            "badge": "📞 สอบถามเร่งด่วน",
            "emoji": "📱",
            "title": "โทรติดต่อร้าน",
            "desc": "• คุณนก: 085-433-6699\n• คุณเสถียร: 092-393-7770",
            "gradient": [(239, 68, 68), (185, 28, 28)],     # Vivid Crimson Red
            "border": "#FCA5A5",
            "btn_text": "โทรติดต่อทันที ➔",
            "btn_bg": "#FFFFFF",
            "btn_color": "#991B1B",
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

        # 1. Render High-Contrast Gradient Card
        card_img, mask = create_gradient_card(w, h, tile["gradient"][0], tile["gradient"][1], radius=52)
        
        # Border
        card_draw = ImageDraw.Draw(card_img)
        card_draw.rounded_rectangle([3, 3, w-4, h-4], radius=52, outline=tile["border"], width=8)
        card_draw.rounded_rectangle([10, 10, w-11, h-11], radius=44, outline=(255, 255, 255, 90), width=3)
        bg.paste(card_img, (x1, y1), mask)

        # 2. Top Sleek Badge Pill
        bx1 = x1 + 38
        by1 = y1 + 34
        badge_w = 410
        badge_h = 66
        # Shadow
        draw.rounded_rectangle([bx1+3, by1+4, bx1+badge_w+3, by1+badge_h+4], radius=33, fill="#000000")
        # Pill
        draw.rounded_rectangle([bx1, by1, bx1+badge_w, by1+badge_h], radius=33, fill="#0F172A", outline="#FFFFFF", width=3)
        draw.text((bx1 + 24, by1 + 10), tile["badge"], fill="#FFFFFF", font=font_badge)

        # 3. Large Icon / Mascot Container
        ic_center_x = x1 + 145
        ic_center_y = y1 + 250
        ic_r = 92
        # Outer dark ring & white glow
        draw.ellipse([ic_center_x - ic_r + 4, ic_center_y - ic_r + 6, ic_center_x + ic_r + 4, ic_center_y + ic_r + 6], fill=(0, 0, 0, 120))
        draw.ellipse([ic_center_x - ic_r, ic_center_y - ic_r, ic_center_x + ic_r, ic_center_y + ic_r], fill="#FFFFFF", outline=tile["border"], width=6)

        if tile["use_owl"] and owl_img is not None:
            # Place cute owl mascot
            owl_thumb = owl_img.resize((150, 192), Image.Resampling.LANCZOS)
            bg.paste(owl_thumb, (ic_center_x - 75, ic_center_y - 96), owl_thumb)
        else:
            # Draw big emoji
            draw.text((ic_center_x - 58, ic_center_y - 78), tile["emoji"], fill="#1E293B", font=font_emoji)

        # 4. BIG BOLD TITLE (Text with Drop Shadow for 100% Crisp Legibility)
        tx = x1 + 265
        ty = y1 + 205
        # Shadow
        draw.text((tx + 3, ty + 4), tile["title"], fill="#000000", font=font_title)
        # Main text in Pure White
        draw.text((tx, ty), tile["title"], fill="#FFFFFF", font=font_title)

        # 5. Clean Divider Line
        divider_y = y1 + 375
        draw.line([x1 + 40, divider_y, x2 - 40, divider_y], fill=(255, 255, 255, 120), width=4)

        # 6. BIG CRISP SUBTITLE (52px Bold)
        # Shadow
        draw.multiline_text((x1 + 45 + 2, y1 + 410 + 3), tile["desc"], fill="#000000", font=font_sub, spacing=20)
        # Main text
        draw.multiline_text((x1 + 45, y1 + 410), tile["desc"], fill="#FFFFFF", font=font_sub, spacing=20)

        # 7. HIGH-CONTRAST CANDY BUTTON PILL AT BOTTOM
        btn_y1 = y2 - 145
        btn_y2 = y2 - 42
        btn_x1 = x1 + 40
        btn_x2 = x2 - 40
        
        # Button Shadow
        draw.rounded_rectangle([btn_x1 + 4, btn_y1 + 5, btn_x2 + 4, btn_y2 + 5], radius=32, fill="#000000")
        # Button Main Fill
        draw.rounded_rectangle([btn_x1, btn_y1, btn_x2, btn_y2], radius=32, fill=tile["btn_bg"], outline="#FFFFFF", width=3)
        # Button Gloss Highlight
        draw.rounded_rectangle([btn_x1 + 8, btn_y1 + 4, btn_x2 - 8, btn_y1 + 24], radius=16, fill=(255, 255, 255, 140))
        
        # Center the button text
        draw.text((btn_x1 + 130, btn_y1 + 24), tile["btn_text"], fill=tile["btn_color"], font=font_btn)

    # Save
    out_path = os.path.join(os.getcwd(), "rich_menu_vibrant.png")
    bg.save(out_path, "PNG", quality=95)
    print(f"High-contrast Vibrant Rich Menu created successfully at: {out_path}")

if __name__ == "__main__":
    generate_vibrant_cool_menu()
