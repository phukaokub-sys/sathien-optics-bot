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

def draw_clean_glossy_button(draw, box, text, fg_color, font, radius=32):
    x1, y1, x2, y2 = box
    # Outer button shadow
    draw.rounded_rectangle([x1+2, y1+4, x2+2, y2+4], radius=radius, fill="#00000035")
    # Clean white button base
    draw.rounded_rectangle([x1, y1, x2, y2], radius=radius, fill="#FFFFFF", outline="#E2E8F0", width=2)
    # Gloss highlight on top half
    draw.rounded_rectangle([x1+6, y1+3, x2-6, y1+18], radius=radius//2, fill="#FFFFFF80")
    # Centered Text
    bbox = font.getbbox(text)
    tw = bbox[2] - bbox[0]
    th = bbox[3] - bbox[1]
    tx = x1 + (x2 - x1 - tw) // 2
    ty = y1 + (y2 - y1 - th) // 2 - 4
    draw.text((tx, ty), text, fill=fg_color, font=font)

def create_perfect_3d_rich_menu():
    src_path = "C:/Users/Administrator/.gemini/antigravity/brain/bd4e2114-09d7-49d9-a028-5fcd2873c6e4/.user_uploaded/media_1795442129232_a6ab2b9c.jpg"
    raw_img = Image.open(src_path).convert('RGBA')
    base = raw_img.resize((2500, 1686), Image.Resampling.LANCZOS)

    # Fonts
    font_bold_path = "C:/Windows/Fonts/LeelaUIb.ttf"
    if not os.path.exists(font_bold_path):
        font_bold_path = "C:/Windows/Fonts/leelawdb.ttf"

    font_title = ImageFont.truetype(font_bold_path, 84)
    font_title_t5 = ImageFont.truetype(font_bold_path, 66)
    font_sub = ImageFont.truetype(font_bold_path, 44)
    font_sub_t2 = ImageFont.truetype(font_bold_path, 42)
    font_btn = ImageFont.truetype(font_bold_path, 48)

    # 1. Tile 1: บูทสัญจร (Orange-Red)
    # Background top: (252, 127, 100), bot: (213, 117, 98)
    draw_seamless_gradient(base, [260, 160, 720, 330], (252, 127, 100), (230, 100, 75), radius=20, blur=10)
    draw_seamless_gradient(base, [50, 380, 580, 570], (245, 90, 55), (225, 60, 30), radius=20, blur=10)
    
    # 2. Tile 2: แผนที่ร้าน (Emerald Green)
    # Background top: (76, 230, 183), bot: (87, 184, 155)
    # Patch covers from 915 to 1580 to erase the corrupted square box [][] completely!
    draw_seamless_gradient(base, [915, 160, 1580, 330], (76, 230, 183), (60, 205, 155), radius=20, blur=10)
    draw_seamless_gradient(base, [880, 380, 1420, 570], (55, 200, 150), (40, 175, 130), radius=20, blur=10)

    # 3. Tile 3: เช็กสถานะ (Vibrant Blue)
    # Background top: (92, 172, 242), bot: (84, 141, 200)
    draw_seamless_gradient(base, [1870, 160, 2430, 330], (92, 172, 242), (65, 145, 235), radius=20, blur=10)
    draw_seamless_gradient(base, [1680, 380, 2220, 570], (60, 140, 230), (35, 115, 215), radius=20, blur=10)

    # 4. Tile 4: สลิปสายตา (Royal Purple)
    # Background top: (174, 119, 238), bot: (171, 148, 200)
    draw_seamless_gradient(base, [280, 1000, 780, 1170], (174, 119, 238), (150, 95, 225), radius=20, blur=10)
    draw_seamless_gradient(base, [60, 1200, 780, 1410], (145, 90, 220), (120, 65, 200), radius=20, blur=10)

    # 5. Tile 5: บริการหลังการขาย (Hot Pink)
    # Background top: (235, 98, 153), bot: (203, 123, 156)
    draw_seamless_gradient(base, [1060, 1000, 1630, 1170], (235, 98, 153), (215, 75, 135), radius=20, blur=10)
    draw_seamless_gradient(base, [880, 1200, 1630, 1410], (210, 70, 130), (190, 50, 110), radius=20, blur=10)

    # 6. Tile 6: โทรด่วน (Warm Coral / Crimson)
    # Background top: (218, 86, 117), bot: (194, 115, 135)
    draw_seamless_gradient(base, [1900, 1000, 2430, 1170], (218, 86, 117), (200, 65, 95), radius=20, blur=10)
    draw_seamless_gradient(base, [1700, 1200, 2440, 1410], (195, 60, 90), (175, 40, 70), radius=20, blur=10)

    draw = ImageDraw.Draw(base)

    # Stamp Crisp Thai Text with Drop Shadow for Maximum Legibility
    def draw_text_shadow(pos, text, font, fill="#FFFFFF", shadow="#00000045", offset=3):
        x, y = pos
        draw.text((x + offset, y + offset), text, fill=shadow, font=font)
        draw.text((x, y), text, fill=fill, font=font)

    def draw_multiline_shadow(pos, text, font, fill="#FFFFFF", shadow="#00000045", offset=3, spacing=14):
        x, y = pos
        draw.multiline_text((x + offset, y + offset), text, fill=shadow, font=font, spacing=spacing)
        draw.multiline_text((x, y), text, fill=fill, font=font, spacing=spacing)

    # 1. Text Tile 1 (บูทสัญจร)
    draw_text_shadow((270, 195), "บูทสัญจร", font_title)
    draw_multiline_shadow((68, 410), "เช็กจุดออกบูธวันนี้\nสัปดาห์นี้พ่อไปงานไหน", font_sub)
    draw_clean_glossy_button(draw, [80, 680, 750, 785], "ดูพิกัดบูธ ➔", "#D9381E", font_btn)

    # 2. Text Tile 2 (แผนที่ร้าน - No square box, clear AIS text)
    draw_text_shadow((1040, 195), "แผนที่ร้าน", font_title)
    draw_multiline_shadow((895, 410), "ชั้นล่าง อาคาร B ตรงข้าม AIS\n(แตะเปิด Maps นำทางทันที)", font_sub_t2)
    draw_clean_glossy_button(draw, [910, 680, 1580, 785], "เปิด MAPS 📍", "#059669", font_btn)

    # 3. Text Tile 3 (เช็กสถานะ)
    draw_text_shadow((1895, 195), "เช็กสถานะ", font_title)
    draw_multiline_shadow((1715, 410), "เลขพัสดุ / เลข Flash\nหรือกรอกที่อยู่จัดส่งฟรี", font_sub)
    draw_clean_glossy_button(draw, [1740, 680, 2410, 785], "เช็กสถานะ ➔", "#1D4ED8", font_btn)

    # 4. Text Tile 4 (สลิปสายตา)
    draw_text_shadow((290, 1030), "สลิปสายตา", font_title)
    draw_multiline_shadow((68, 1235), "ดูประวัติวัดสายตา\nสลิปจากคอมพิวเตอร์", font_sub)
    draw_clean_glossy_button(draw, [80, 1510, 750, 1615], "ดูสลิปสายตา ➔", "#7C3AED", font_btn)

    # 5. Text Tile 5 (บริการหลังการขาย - 100% correct Thai spelling!)
    draw_text_shadow((1075, 1035), "บริการหลังการขาย", font_title_t5)
    draw_multiline_shadow((895, 1235), "มีปัญหาแว่นไม่กระชับ\nติดต่อ คุณเสถียร ได้เลย", font_sub)
    draw_clean_glossy_button(draw, [910, 1510, 1580, 1615], "โทรหาคุณเสถียร 📞", "#BE185D", font_btn)

    # 6. Text Tile 6 (โทรด่วน - Fixed คุณนก)
    draw_text_shadow((1920, 1030), "โทรด่วน", font_title)
    draw_multiline_shadow((1715, 1235), "• คุณนก: 085-433-6699\n• คุณเสถียร: 092-393-7770", font_sub, spacing=16)
    draw_clean_glossy_button(draw, [1740, 1510, 2410, 1615], "โทรหาร้าน ➔", "#B91C1C", font_btn)

    # Save final JPG (Under 1MB for LINE API requirements)
    final_img = base.convert('RGB')
    out_path = os.path.join(os.getcwd(), "rich_menu_3d_perfect.jpg")
    final_img.save(out_path, "JPEG", quality=90, optimize=True)
    print(f"Perfect 3D Pixar Rich Menu created successfully at: {out_path} ({os.path.getsize(out_path) / 1024:.1f} KB)")

if __name__ == "__main__":
    create_perfect_3d_rich_menu()
