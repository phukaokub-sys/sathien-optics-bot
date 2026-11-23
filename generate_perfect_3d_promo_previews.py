import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def draw_seamless_gradient(base_img, box, c_top, c_bot, radius=24, blur=12):
    x1, y1, x2, y2 = box
    w = max(10, x2 - x1)
    h = max(10, y2 - y1)
    patch = Image.new('RGBA', (w, h), (0, 0, 0, 0))
    p_draw = ImageDraw.Draw(patch)
    for y in range(h):
        ratio = y / float(h)
        r = int(c_top[0] * (1 - ratio) + c_bot[0] * ratio)
        g = int(c_top[1] * (1 - ratio) + c_bot[1] * ratio)
        b = int(c_top[2] * (1 - ratio) + c_bot[2] * ratio)
        p_draw.line([(0, y), (w, y)], fill=(r, g, b, 255))
    
    mask = Image.new('L', (w, h), 0)
    m_draw = ImageDraw.Draw(mask)
    m_draw.rounded_rectangle([blur, blur, w - blur, h - blur], radius=radius, fill=255)
    mask = mask.filter(ImageFilter.GaussianBlur(blur))
    base_img.paste(patch, (x1, y1), mask)

def draw_clean_top_tag(draw, pos, text, font, border_color="#FFFFFF60"):
    x, y = pos
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    pw = tw + 44
    ph = 56
    # Dark translucent pill
    draw.rounded_rectangle([x, y, x + pw, y + ph], radius=24, fill="#0F172AEE", outline=border_color, width=2)
    # Centered text
    tx = x + (pw - tw) // 2
    ty = y + (ph - th) // 2 - 3
    draw.text((tx, ty), text, fill="#FFFFFF", font=font)

def draw_glossy_button_with_arrow(draw, box, text, fg_color, font, radius=32):
    x1, y1, x2, y2 = box
    # Outer button shadow
    draw.rounded_rectangle([x1+2, y1+4, x2+2, y2+4], radius=radius, fill="#00000035")
    # Clean white button base
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill="#FFFFFF", outline="#E2E8F0", width=2)
    # Gloss highlight on top half
    draw.rounded_rectangle([x1+6, y1+3, x2-6, y1+18], radius=radius//2, fill="#FFFFFF80")
    
    # Text + vector chevron arrow `>`
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    arrow_w = 16
    total_w = tw + 18 + arrow_w
    tx = x1 + (x2 - x1 - total_w) // 2
    ty = y1 + (y2 - y1 - th) // 2 - 4
    draw.text((tx, ty), text, fill=fg_color, font=font)

    # Draw crisp vector chevron arrow `>` (NO unicode square box glitch!)
    ax = tx + tw + 18
    ay = y1 + (y2 - y1) // 2 - 2
    arrow_points = [(ax, ay - 13), (ax + 13, ay), (ax, ay + 13)]
    draw.line(arrow_points, fill=fg_color, width=5, joint="curve")

def generate_option1():
    # Option 1: 3D Pixar Characters with Promotion in Tile 4 (Purple with 3D Eyeball wearing glasses!)
    src_path = "C:/Users/Administrator/.gemini/antigravity/brain/bd4e2114-09d7-49d9-a028-5fcd2873c6e4/.user_uploaded/media_1795442129232_a6ab2b9c.jpg"
    raw_img = Image.open(src_path).convert('RGBA')
    base = raw_img.resize((2500, 1686), Image.Resampling.LANCZOS)

    font_bold_path = "C:/Windows/Fonts/LeelaUIb.ttf"
    if not os.path.exists(font_bold_path):
        font_bold_path = "C:/Windows/Fonts/leelawdb.ttf"

    font_tag = ImageFont.truetype(font_bold_path, 34)
    font_title = ImageFont.truetype(font_bold_path, 84)
    font_title_t4 = ImageFont.truetype(font_bold_path, 80)
    font_title_t5 = ImageFont.truetype(font_bold_path, 66)
    font_sub = ImageFont.truetype(font_bold_path, 44)
    font_sub_t2 = ImageFont.truetype(font_bold_path, 42)
    font_btn = ImageFont.truetype(font_bold_path, 46)

    # 1. Seamless gradient patches to cover old AI text & square boxes cleanly
    # Tile 1: บูทสัญจร (Orange)
    draw_seamless_gradient(base, [260, 160, 720, 330], (252, 127, 100), (230, 100, 75), radius=20, blur=10)
    draw_seamless_gradient(base, [50, 380, 580, 570], (245, 90, 55), (225, 60, 30), radius=20, blur=10)
    # Tile 2: แผนที่ร้าน (Green) - covers square box at 920!
    draw_seamless_gradient(base, [915, 160, 1580, 330], (76, 230, 183), (60, 205, 155), radius=20, blur=10)
    draw_seamless_gradient(base, [880, 380, 1420, 570], (55, 200, 150), (40, 175, 130), radius=20, blur=10)
    # Tile 3: เช็กสถานะ (Blue)
    draw_seamless_gradient(base, [1870, 160, 2430, 330], (92, 172, 242), (65, 145, 235), radius=20, blur=10)
    draw_seamless_gradient(base, [1680, 380, 2220, 570], (60, 140, 230), (35, 115, 215), radius=20, blur=10)
    # Tile 4: โปรโมชั่นพิเศษ (Purple)
    draw_seamless_gradient(base, [280, 1000, 780, 1170], (174, 119, 238), (150, 95, 225), radius=20, blur=10)
    draw_seamless_gradient(base, [60, 1200, 780, 1410], (145, 90, 220), (120, 65, 200), radius=20, blur=10)
    # Tile 5: บริการหลังการขาย (Pink)
    draw_seamless_gradient(base, [1060, 1000, 1630, 1170], (235, 98, 153), (215, 75, 135), radius=20, blur=10)
    draw_seamless_gradient(base, [880, 1200, 1630, 1410], (210, 70, 130), (190, 50, 110), radius=20, blur=10)
    # Tile 6: โทรติดต่อร้าน (Coral Red)
    draw_seamless_gradient(base, [1900, 1000, 2430, 1170], (218, 86, 117), (200, 65, 95), radius=20, blur=10)
    draw_seamless_gradient(base, [1700, 1200, 2440, 1410], (195, 60, 90), (175, 40, 70), radius=20, blur=10)

    draw = ImageDraw.Draw(base)

    # 2. Draw Top Category Badges (Zero square box glyphs!)
    draw_clean_top_tag(draw, (70, 70), "POP-UP EVENT", font_tag, "#FDBA74")
    draw_clean_top_tag(draw, (900, 70), "GOOGLE MAPS", font_tag, "#6EE7B7")
    draw_clean_top_tag(draw, (1730, 70), "FAST DELIVERY", font_tag, "#93C5FD")
    draw_clean_top_tag(draw, (70, 900), "HOT PROMOTION", font_tag, "#FDE047") # Golden for promo!
    draw_clean_top_tag(draw, (900, 900), "SATIEN CARE", font_tag, "#F9A8D4")
    draw_clean_top_tag(draw, (1730, 900), "CALL STORE", font_tag, "#FCA5A5")

    # Text shadows helper
    def draw_text_shadow(pos, text, font, fill="#FFFFFF", shadow="#00000045", offset=3):
        x, y = pos
        draw.text((x + offset, y + offset), text, fill=shadow, font=font)
        draw.text((x, y), text, fill=fill, font=font)

    def draw_multiline_shadow(pos, text, font, fill="#FFFFFF", shadow="#00000045", offset=3, spacing=14):
        x, y = pos
        draw.multiline_text((x + offset, y + offset), text, fill=shadow, font=font, spacing=spacing)
        draw.multiline_text((x, y), text, fill=fill, font=font, spacing=spacing)

    # 3. Titles & Subtitles
    # Tile 1: บูทสัญจร
    draw_text_shadow((270, 195), "บูทสัญจร", font_title)
    draw_multiline_shadow((68, 410), "เช็กจุดออกบูธวันนี้\nสัปดาห์นี้พ่อไปงานไหน", font_sub)
    draw_glossy_button_with_arrow(draw, [80, 680, 750, 785], "ดูพิกัดบูท", "#D9381E", font_btn)

    # Tile 2: แผนที่ร้าน
    draw_text_shadow((1040, 195), "แผนที่ร้าน", font_title)
    draw_multiline_shadow((895, 410), "ชั้นล่าง อาคาร B ตรงข้าม AIS\n(แตะเปิด Maps นำทางทันที)", font_sub_t2)
    draw_glossy_button_with_arrow(draw, [910, 680, 1580, 785], "เปิด MAPS 📍", "#059669", font_btn)

    # Tile 3: เช็กสถานะ
    draw_text_shadow((1895, 195), "เช็กสถานะ", font_title)
    draw_multiline_shadow((1715, 410), "เลขพัสดุ / เลข Flash\nหรือกรอกที่อยู่จัดส่งฟรี", font_sub)
    draw_glossy_button_with_arrow(draw, [1740, 680, 2410, 785], "เช็กสถานะ", "#1D4ED8", font_btn)

    # Tile 4: โปรโมชั่นพิเศษ (PROMOTION)
    draw_text_shadow((275, 1030), "โปรโมชั่นพิเศษ", font_title_t4)
    draw_multiline_shadow((68, 1235), "กรอบ + เลนส์ เริ่มต้น 990.-\nบลู • ออโต้ • โปรเกรสซีฟ", font_sub)
    draw_glossy_button_with_arrow(draw, [80, 1510, 750, 1615], "ดูโปรโมชั่น", "#7C3AED", font_btn)

    # Tile 5: บริการหลังการขาย
    draw_text_shadow((1075, 1035), "บริการหลังการขาย", font_title_t5)
    draw_multiline_shadow((895, 1235), "แว่นหลวม ไม่สบายตา ซ่อมฟรี\nติดต่อ คุณเสถียร ได้เลย", font_sub)
    draw_glossy_button_with_arrow(draw, [910, 1510, 1580, 1615], "โทรหาคุณเสถียร", "#BE185D", font_btn)

    # Tile 6: โทรติดต่อร้าน
    draw_text_shadow((1920, 1030), "โทรติดต่อร้าน", font_title)
    draw_multiline_shadow((1715, 1235), "• คุณนก: 085-433-6699\n• คุณเสถียร: 092-393-7770", font_sub, spacing=16)
    draw_glossy_button_with_arrow(draw, [1740, 1510, 2410, 1615], "โทรหาร้าน", "#B91C1C", font_btn)

    # Save Option 1
    final_img = base.convert('RGB')
    out_path = os.path.join(os.getcwd(), "preview_option1_3d_promo.jpg")
    final_img.save(out_path, "JPEG", quality=92, optimize=True)
    print(f"Option 1 Preview saved: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")
    return out_path

def generate_option2():
    # Option 2: Promotion is in Tile 1 (Top-Left Star Position) and Booth is in Tile 4!
    src_path = "C:/Users/Administrator/.gemini/antigravity/brain/bd4e2114-09d7-49d9-a028-5fcd2873c6e4/.user_uploaded/media_1795442129232_a6ab2b9c.jpg"
    raw_img = Image.open(src_path).convert('RGBA')
    base = raw_img.resize((2500, 1686), Image.Resampling.LANCZOS)

    font_bold_path = "C:/Windows/Fonts/LeelaUIb.ttf"
    if not os.path.exists(font_bold_path):
        font_bold_path = "C:/Windows/Fonts/leelawdb.ttf"

    font_tag = ImageFont.truetype(font_bold_path, 34)
    font_title = ImageFont.truetype(font_bold_path, 84)
    font_title_t1 = ImageFont.truetype(font_bold_path, 80)
    font_title_t5 = ImageFont.truetype(font_bold_path, 66)
    font_sub = ImageFont.truetype(font_bold_path, 44)
    font_sub_t2 = ImageFont.truetype(font_bold_path, 42)
    font_btn = ImageFont.truetype(font_bold_path, 46)

    # Gradients
    draw_seamless_gradient(base, [260, 160, 720, 330], (252, 127, 100), (230, 100, 75), radius=20, blur=10)
    draw_seamless_gradient(base, [50, 380, 580, 570], (245, 90, 55), (225, 60, 30), radius=20, blur=10)
    draw_seamless_gradient(base, [915, 160, 1580, 330], (76, 230, 183), (60, 205, 155), radius=20, blur=10)
    draw_seamless_gradient(base, [880, 380, 1420, 570], (55, 200, 150), (40, 175, 130), radius=20, blur=10)
    draw_seamless_gradient(base, [1870, 160, 2430, 330], (92, 172, 242), (65, 145, 235), radius=20, blur=10)
    draw_seamless_gradient(base, [1680, 380, 2220, 570], (60, 140, 230), (35, 115, 215), radius=20, blur=10)
    draw_seamless_gradient(base, [280, 1000, 780, 1170], (174, 119, 238), (150, 95, 225), radius=20, blur=10)
    draw_seamless_gradient(base, [60, 1200, 780, 1410], (145, 90, 220), (120, 65, 200), radius=20, blur=10)
    draw_seamless_gradient(base, [1060, 1000, 1630, 1170], (235, 98, 153), (215, 75, 135), radius=20, blur=10)
    draw_seamless_gradient(base, [880, 1200, 1630, 1410], (210, 70, 130), (190, 50, 110), radius=20, blur=10)
    draw_seamless_gradient(base, [1900, 1000, 2430, 1170], (218, 86, 117), (200, 65, 95), radius=20, blur=10)
    draw_seamless_gradient(base, [1700, 1200, 2440, 1410], (195, 60, 90), (175, 40, 70), radius=20, blur=10)

    draw = ImageDraw.Draw(base)

    # Badges
    draw_clean_top_tag(draw, (70, 70), "HOT PROMOTION", font_tag, "#FDE047") # Top-Left PROMO!
    draw_clean_top_tag(draw, (900, 70), "GOOGLE MAPS", font_tag, "#6EE7B7")
    draw_clean_top_tag(draw, (1730, 70), "FAST DELIVERY", font_tag, "#93C5FD")
    draw_clean_top_tag(draw, (70, 900), "POP-UP EVENT", font_tag, "#FDBA74") # Bottom-Left BOOTH!
    draw_clean_top_tag(draw, (900, 900), "SATIEN CARE", font_tag, "#F9A8D4")
    draw_clean_top_tag(draw, (1730, 900), "CALL STORE", font_tag, "#FCA5A5")

    def draw_text_shadow(pos, text, font, fill="#FFFFFF", shadow="#00000045", offset=3):
        x, y = pos
        draw.text((x + offset, y + offset), text, fill=shadow, font=font)
        draw.text((x, y), text, fill=fill, font=font)

    def draw_multiline_shadow(pos, text, font, fill="#FFFFFF", shadow="#00000045", offset=3, spacing=14):
        x, y = pos
        draw.multiline_text((x + offset, y + offset), text, fill=shadow, font=font, spacing=spacing)
        draw.multiline_text((x, y), text, fill=fill, font=font, spacing=spacing)

    # Tile 1: โปรโมชั่นพิเศษ (Top-Left!)
    draw_text_shadow((260, 195), "โปรโมชั่นพิเศษ", font_title_t1)
    draw_multiline_shadow((68, 410), "กรอบ + เลนส์ เริ่มต้น 990.-\nบลู • ออโต้ • โปรเกรสซีฟ", font_sub)
    draw_glossy_button_with_arrow(draw, [80, 680, 750, 785], "ดูโปรโมชั่น", "#D9381E", font_btn)

    # Tile 2: แผนที่ร้าน
    draw_text_shadow((1040, 195), "แผนที่ร้าน", font_title)
    draw_multiline_shadow((895, 410), "ชั้นล่าง อาคาร B ตรงข้าม AIS\n(แตะเปิด Maps นำทางทันที)", font_sub_t2)
    draw_glossy_button_with_arrow(draw, [910, 680, 1580, 785], "เปิด MAPS 📍", "#059669", font_btn)

    # Tile 3: เช็กสถานะ
    draw_text_shadow((1895, 195), "เช็กสถานะ", font_title)
    draw_multiline_shadow((1715, 410), "เลขพัสดุ / เลข Flash\nหรือกรอกที่อยู่จัดส่งฟรี", font_sub)
    draw_glossy_button_with_arrow(draw, [1740, 680, 2410, 785], "เช็กสถานะ", "#1D4ED8", font_btn)

    # Tile 4: บูทสัญจร (Bottom-Left!)
    draw_text_shadow((290, 1030), "บูทสัญจร", font_title)
    draw_multiline_shadow((68, 1235), "เช็กจุดออกบูธวันนี้\nสัปดาห์นี้พ่อไปงานไหน", font_sub)
    draw_glossy_button_with_arrow(draw, [80, 1510, 750, 1615], "ดูพิกัดบูท", "#7C3AED", font_btn)

    # Tile 5: บริการหลังการขาย
    draw_text_shadow((1075, 1035), "บริการหลังการขาย", font_title_t5)
    draw_multiline_shadow((895, 1235), "แว่นหลวม ไม่สบายตา ซ่อมฟรี\nติดต่อ คุณเสถียร ได้เลย", font_sub)
    draw_glossy_button_with_arrow(draw, [910, 1510, 1580, 1615], "โทรหาคุณเสถียร", "#BE185D", font_btn)

    # Tile 6: โทรติดต่อร้าน
    draw_text_shadow((1920, 1030), "โทรติดต่อร้าน", font_title)
    draw_multiline_shadow((1715, 1235), "• คุณนก: 085-433-6699\n• คุณเสถียร: 092-393-7770", font_sub, spacing=16)
    draw_glossy_button_with_arrow(draw, [1740, 1510, 2410, 1615], "โทรหาร้าน", "#B91C1C", font_btn)

    # Save Option 2
    final_img = base.convert('RGB')
    out_path = os.path.join(os.getcwd(), "preview_option2_top_promo.jpg")
    final_img.save(out_path, "JPEG", quality=92, optimize=True)
    print(f"Option 2 Preview saved: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")
    return out_path

if __name__ == "__main__":
    generate_option1()
    generate_option2()
