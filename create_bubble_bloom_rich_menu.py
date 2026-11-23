import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def draw_bubble_bloom_card(base_img, box, bg_gradient_colors, border_color, glow_color, radius=52):
    x1, y1, x2, y2 = box
    w = x2 - x1
    h = y2 - y1

    # 1. Outer Bloom Glow
    glow_pad = 24
    glow_img = Image.new('RGBA', (w + glow_pad * 2, h + glow_pad * 2), (0, 0, 0, 0))
    glow_draw = ImageDraw.Draw(glow_img)
    glow_draw.rounded_rectangle([glow_pad, glow_pad, w + glow_pad, h + glow_pad], radius=radius, fill=glow_color)
    glow_img = glow_img.filter(ImageFilter.GaussianBlur(16))
    base_img.paste(glow_img, (x1 - glow_pad, y1 - glow_pad), glow_img)

    # 2. Main Card Layer with Gradient
    card_img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    card_draw = ImageDraw.Draw(card_img)

    # Gradient fill from top to bottom
    c_top, c_bottom = bg_gradient_colors
    for y in range(h):
        ratio = y / float(h)
        r = int(c_top[0] * (1 - ratio) + c_bottom[0] * ratio)
        g = int(c_top[1] * (1 - ratio) + c_bottom[1] * ratio)
        b = int(c_top[2] * (1 - ratio) + c_bottom[2] * ratio)
        card_draw.line([(0, y), (w, y)], fill=(r, g, b, 255))

    # Mask to rounded rectangle
    mask = Image.new('L', (w, h), 0)
    mask_draw = ImageDraw.Draw(mask)
    mask_draw.rounded_rectangle([0, 0, w, h], radius=radius, fill=255)
    
    # 3. Glassy Top Specular Highlight (Bubble Bloom 3D glass look)
    highlight_img = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    hl_draw = ImageDraw.Draw(highlight_img)
    hl_draw.ellipse([-w * 0.2, -h * 0.4, w * 1.2, h * 0.55], fill=(255, 255, 255, 120))
    card_img.paste(highlight_img, (0, 0), highlight_img)

    # 4. Bubble border
    card_draw.rounded_rectangle([2, 2, w-3, h-3], radius=radius, outline=border_color, width=6)
    card_draw.rounded_rectangle([8, 8, w-9, h-9], radius=radius-6, outline=(255, 255, 255, 180), width=3)

    # Paste into base
    base_img.paste(card_img, (x1, y1), mask)

def generate_bubble_bloom():
    width = 2500
    height = 1686

    # 1. Base Luminous Pearl Background
    bg = Image.new('RGB', (width, height), color='#FFF9F8')

    # Add Dreamy Bubble Blooms
    bloom_canvas = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    b_draw = ImageDraw.Draw(bloom_canvas)

    # Colorful ambient bloom orbs
    blooms = [
        (400, 300, 320, (254, 205, 211, 140)),   # Rose pink
        (1250, 250, 350, (187, 247, 208, 140)),  # Mint emerald
        (2100, 320, 320, (191, 219, 254, 150)),  # Sky blue
        (400, 1300, 340, (233, 213, 255, 140)),  # Lavender
        (1250, 1350, 350, (254, 240, 138, 150)), # Golden yellow
        (2100, 1300, 340, (254, 215, 170, 140))  # Peach orange
    ]
    for bx, by, br, bcolor in blooms:
        b_draw.ellipse([bx-br, by-br, bx+br, by+br], fill=bcolor)
    bloom_canvas = bloom_canvas.filter(ImageFilter.GaussianBlur(90))
    bg.paste(bloom_canvas, (0, 0), bloom_canvas)

    # Draw overlay for clean drawing
    draw = ImageDraw.Draw(bg)

    # Fonts
    font_bold_path = "C:/Windows/Fonts/leelawadb.ttf"
    font_path = "C:/Windows/Fonts/leelawad.ttf"
    if not os.path.exists(font_bold_path):
        font_bold_path = font_path

    font_title = ImageFont.truetype(font_bold_path, 66)
    font_sub = ImageFont.truetype(font_path, 38)
    font_sub_bold = ImageFont.truetype(font_bold_path, 39)
    font_badge = ImageFont.truetype(font_bold_path, 35)
    font_emoji = ImageFont.truetype(font_bold_path, 80)
    font_btn = ImageFont.truetype(font_bold_path, 42)

    # Load Owl Mascot
    owl_img = None
    if os.path.exists("owl_mascot.png"):
        try:
            owl_img = Image.open("owl_mascot.png").convert("RGBA")
        except Exception:
            owl_img = None

    # Grid specifications
    col_x = [0, 833, 1667, 2500]
    row_y = [0, 843, 1686]
    pad = 22

    tiles = [
        # Tile 1: พิกัดบูทวันนี้
        {
            "col": 0, "row": 0,
            "badge": "🎪 บูทสัญจรของคุณพ่อ",
            "badge_color": "#EA580C",
            "emoji": "📍",
            "title": "พิกัดบูทวันนี้",
            "desc": "เช็กจุดออกบูทสัปดาห์นี้\nโทรสอบถามคุณเสถียรได้เลย",
            "bg_gradient": [(255, 250, 240), (255, 237, 213)], # Warm honey cream
            "border": "#FB923C",
            "glow": (251, 146, 60, 60),
            "accent": "#EA580C",
            "btn_text": "เช็กจุดออกบูท ➔",
            "use_owl": False
        },
        # Tile 2: แผนที่ร้านหลัก (Google Maps)
        {
            "col": 1, "row": 0,
            "badge": "🏢 หน้าร้านประจำ อาคาร B",
            "badge_color": "#059669",
            "emoji": "🗺️",
            "title": "แผนที่ร้านหลัก",
            "desc": "ชั้นล่าง ตรงข้าม Telewiz\n(แตะปุ่มนี้เปิด Google Maps ทันที)",
            "bg_gradient": [(240, 253, 244), (209, 250, 229)], # Soft emerald mint
            "border": "#34D399",
            "glow": (52, 211, 153, 60),
            "accent": "#059669",
            "btn_text": "เปิด Google Maps 📍",
            "use_owl": False
        },
        # Tile 3: ติดตามแว่นตา / พัสดุ
        {
            "col": 2, "row": 0,
            "badge": "🚚 ส่งฟรีถึงบ้าน",
            "badge_color": "#2563EB",
            "emoji": "📦",
            "title": "ติดตามแว่นตา",
            "desc": "กรอกที่อยู่จัดส่งพัสดุ\nหรือเช็กเลข Flash Express",
            "bg_gradient": [(240, 249, 255), (219, 234, 254)], # Sky blue
            "border": "#60A5FA",
            "glow": (96, 165, 250, 60),
            "accent": "#2563EB",
            "btn_text": "กรอกที่อยู่ / เช็กสถานะ ➔",
            "use_owl": False
        },
        # Tile 4: สลิปค่าสายตา
        {
            "col": 0, "row": 1,
            "badge": "👓 ประวัติจากเครื่องวัด",
            "badge_color": "#7C3AED",
            "emoji": "📄",
            "title": "สลิปค่าสายตา",
            "desc": "เก็บบันทึกประวัติสายตา\nใช้เป็นข้อมูลตัดแว่นครั้งต่อไป",
            "bg_gradient": [(250, 245, 255), (237, 233, 254)], # Dreamy Lavender
            "border": "#A78BFA",
            "glow": (167, 139, 250, 60),
            "accent": "#7C3AED",
            "btn_text": "ดูสลิปค่าสายตา ➔",
            "use_owl": False
        },
        # Tile 5: บริการหลังการขาย (คุณเสถียร) - featuring the Owl Mascot!
        {
            "col": 1, "row": 1,
            "badge": "🦉 ดูแลด้วยใจจริง",
            "badge_color": "#DB2777", # Pink matching logo
            "emoji": "🛠️",
            "title": "บริการหลังการขาย",
            "desc": "หากแว่นตามีปัญหาการใช้งาน\nติดต่อ คุณเสถียร ได้ทันทีครับ",
            "bg_gradient": [(255, 245, 247), (254, 226, 236)], # Soft Rose Pearl
            "border": "#F472B6",
            "glow": (244, 114, 182, 70),
            "accent": "#DB2777",
            "btn_text": "โทรหาคุณเสถียร 📞",
            "use_owl": True
        },
        # Tile 6: โทรติดต่อร้าน
        {
            "col": 2, "row": 1,
            "badge": "📞 คุยกับทางร้าน",
            "badge_color": "#E11D48",
            "emoji": "📱",
            "title": "โทรติดต่อร้าน",
            "desc": "• คุณนก: 085-433-6699\n• คุณเสถียร: 092-393-7770",
            "bg_gradient": [(255, 241, 242), (254, 205, 211)], # Coral Peach
            "border": "#FB7185",
            "glow": (251, 113, 133, 60),
            "accent": "#E11D48",
            "btn_text": "โทรติดต่อทันที ➔",
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

        # 1. Render Glassy Bubble Card
        draw_bubble_bloom_card(bg, [x1, y1, x2, y2], tile["bg_gradient"], tile["border"], tile["glow"], radius=50)

        # 2. Top Candy Badge
        bx1 = x1 + 36
        by1 = y1 + 36
        badge_w = 345
        badge_h = 56
        draw.rounded_rectangle([bx1 + 3, by1 + 4, bx1 + badge_w + 3, by1 + badge_h + 4], radius=28, fill="#E2E8F0")
        draw.rounded_rectangle([bx1, by1, bx1 + badge_w, by1 + badge_h], radius=28, fill=tile["badge_color"])
        draw.text((bx1 + 24, by1 + 6), tile["badge"], fill="#FFFFFF", font=font_badge)

        # 3. Icon / Owl Mascot
        ic_center_x = x1 + 130
        ic_center_y = y1 + 225
        ic_r = 78

        # Draw glowing 3D bubble orb for icon
        draw.ellipse([ic_center_x - ic_r + 4, ic_center_y - ic_r + 5, ic_center_x + ic_r + 4, ic_center_y + ic_r + 5], fill=(0, 0, 0, 25))
        draw.ellipse([ic_center_x - ic_r, ic_center_y - ic_r, ic_center_x + ic_r, ic_center_y + ic_r], fill="#FFFFFF", outline=tile["border"], width=5)
        # Specular glint inside bubble
        draw.ellipse([ic_center_x - ic_r + 14, ic_center_y - ic_r + 12, ic_center_x - ic_r + 46, ic_center_y - ic_r + 34], fill="#F1F5F9")

        if tile["use_owl"] and owl_img is not None:
            # Place cute owl inside the bubble icon
            owl_thumb = owl_img.resize((125, 160), Image.Resampling.LANCZOS)
            bg.paste(owl_thumb, (ic_center_x - 62, ic_center_y - 80), owl_thumb)
        else:
            draw.text((ic_center_x - 40, ic_center_y - 52), tile["emoji"], fill="#1E293B", font=font_emoji)

        # 4. Title
        tx = x1 + 238
        ty = y1 + 190
        draw.text((tx, ty), tile["title"], fill="#0F172A", font=font_title)

        # 5. Dotted divider line
        divider_y = y1 + 340
        for lx in range(x1 + 40, x2 - 40, 20):
            draw.ellipse([lx, divider_y, lx + 7, divider_y + 7], fill=tile["border"])

        # 6. Description Text
        draw.multiline_text((x1 + 42, y1 + 375), tile["desc"], fill="#334155", font=font_sub, spacing=16)

        # 7. Bottom Glossy Candy Button Pill
        btn_y1 = y2 - 130
        btn_y2 = y2 - 42
        btn_x1 = x1 + 38
        btn_x2 = x2 - 38
        
        # Soft shadow
        draw.rounded_rectangle([btn_x1 + 3, btn_y1 + 4, btn_x2 + 3, btn_y2 + 4], radius=28, fill="#CBD5E1")
        # Pill base
        draw.rounded_rectangle([btn_x1, btn_y1, btn_x2, btn_y2], radius=28, fill="#FFFFFF", outline=tile["accent"], width=4)
        # Glossy top highlight
        draw.rounded_rectangle([btn_x1 + 6, btn_y1 + 4, btn_x2 - 6, btn_y1 + 22], radius=14, fill=(255, 255, 255, 160))
        
        # Button label centered
        btn_txt = tile["btn_text"]
        draw.text((btn_x1 + 170, btn_y1 + 18), btn_txt, fill=tile["accent"], font=font_btn)

    # Save
    out_path = os.path.join(os.getcwd(), "rich_menu_bubble_bloom.png")
    bg.save(out_path, "PNG", quality=95)
    print(f"Bubble Bloom Rich Menu saved to: {out_path}")

if __name__ == "__main__":
    generate_bubble_bloom()
