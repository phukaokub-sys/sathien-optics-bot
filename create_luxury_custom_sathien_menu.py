import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def build_rich_menu():
    src_path = "scratch_resized_2500x1686.png"
    if not os.path.exists(src_path):
        orig = Image.open("C:/Users/Administrator/.gemini/antigravity/brain/bd4e2114-09d7-49d9-a028-5fcd2873c6e4/.user_uploaded/media_1795514773586_98b21bb2.jpg")
        base = orig.resize((2500, 1686), Image.Resampling.LANCZOS)
    else:
        base = Image.open(src_path).convert("RGBA")

    # Fonts
    font_bold = "fonts/Prompt-Bold.ttf"
    font_semibold = "fonts/Prompt-SemiBold.ttf"
    font_medium = "fonts/Prompt-Medium.ttf"

    f_title = ImageFont.truetype(font_bold, 64)
    f_c3_title = ImageFont.truetype(font_bold, 60)
    f_sub_bold = ImageFont.truetype(font_semibold, 34)
    f_sub_c3 = ImageFont.truetype(font_semibold, 30)
    f_sub_c3_small = ImageFont.truetype(font_medium, 27)
    f_sub = ImageFont.truetype(font_medium, 32)
    f_header_phone = ImageFont.truetype(font_bold, 36)
    f_btn = ImageFont.truetype(font_bold, 45)

    # Seamless patch helper
    def seamless_patch(img, box, bg_color, radius=16, blur=8):
        x1, y1, x2, y2 = box
        w = max(10, x2 - x1)
        h = max(10, y2 - y1)
        patch = Image.new("RGBA", (w, h), bg_color)
        mask = Image.new("L", (w, h), 0)
        m_draw = ImageDraw.Draw(mask)
        m_draw.rounded_rectangle([blur, blur, w - blur, h - blur], radius=radius, fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(blur))
        img.paste(patch, (x1, y1), mask)

    # Clean button renderer
    def draw_clean_button(draw, box, text, font):
        x1, y1, x2, y2 = box
        # Outer subtle drop shadow
        draw.rounded_rectangle([x1, y1+4, x2, y2+4], radius=32, fill="#00000030")
        # Base Navy Button
        draw.rounded_rectangle([x1, y1, x2, y2], radius=32, fill="#122538", outline="#25384D", width=2)
        # Subtle top gloss highlight
        draw.rounded_rectangle([x1+6, y1+3, x2-6, y1+16], radius=16, fill="#FFFFFF25")
        # Centered white text
        bbox = font.getbbox(text)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = x1 + (x2 - x1 - tw) // 2
        ty = y1 + (y2 - y1 - th) // 2 - 4
        draw.text((tx, ty), text, fill="#FFFFFF", font=font)

    # ==========================================
    # 1. HEADER (PHONE AREA)
    # ==========================================
    seamless_patch(base, [1720, 45, 2465, 145], (235, 233, 226, 255), radius=10, blur=6)
    d = ImageDraw.Draw(base)
    phone_text = "📞 085-433-6699 (คุณนก) • 092-393-7770 (คุณเสถียร)"
    bbox_p = f_header_phone.getbbox(phone_text)
    tw_p = bbox_p[2] - bbox_p[0]
    d.text((2460 - tw_p, 65), phone_text, fill="#3D3830", font=f_header_phone)

    # ==========================================
    # 2. CARD 3: แผนที่ร้านเสถียร (HOME GOOGLE MAPS & GOV CENTER)
    # ==========================================
    # Erase old fake text "ศูนย์การค้าธัญญาพาร์ค..."
    seamless_patch(base, [1675, 495, 2220, 765], (243, 243, 238, 255), radius=16, blur=8)
    d = ImageDraw.Draw(base)
    d.text((1685, 510), "แผนที่ร้านเสถียร", fill="#111111", font=f_c3_title)
    d.text((1685, 595), "🏡 ร้านที่บ้าน: The Plant-Light รังสิต", fill="#2D2820", font=f_sub_c3)
    d.text((1685, 642), "🏢 ศูนย์ราชการ แจ้งวัฒนะ อาคาร B", fill="#2D2820", font=f_sub_c3)
    d.text((1685, 690), "• หน้าร้านชั้น 1 (ตรงข้าม AIS) 08:30-15:00 น.", fill="#5A554C", font=f_sub_c3_small)
    d.text((1685, 725), "• สตูดิโอที่บ้านเปิดทุกวัน (นัดหมายล่วงหน้า)", fill="#5A554C", font=f_sub_c3_small)

    draw_clean_button(d, [1705, 775, 2420, 865], "📍 เปิด Google Maps >", f_btn)

    # ==========================================
    # 3. CARD 4: บริการหลังการขาย (FIX GLITCH "บริกๆ")
    # ==========================================
    # Erase corrupted "บริกๆ บริการหลังการขาย"
    seamless_patch(base, [50, 1180, 520, 1300], (244, 245, 240, 255), radius=16, blur=8)
    d = ImageDraw.Draw(base)
    d.text((65, 1205), "บริการหลังการขาย", fill="#111111", font=f_title)

    draw_clean_button(d, [65, 1495, 780, 1585], "นัดเข้ารับบริการ >", f_btn)

    # ==========================================
    # 4. CARD 6: โทรติดต่อร้าน (REAL SATHIEN CONTACT INFO)
    # ==========================================
    # Erase fake branches "สาขาลุมพินี..."
    seamless_patch(base, [1675, 1180, 2250, 1485], (241, 242, 237, 255), radius=16, blur=8)
    d = ImageDraw.Draw(base)
    d.text((1685, 1205), "โทรติดต่อร้าน", fill="#111111", font=f_title)
    d.text((1685, 1285), "• คุณนก (ดูแลร้าน/ส่งแว่น): 085-433-6699", fill="#2D2820", font=f_sub_bold)
    d.text((1685, 1335), "• คุณเสถียร (ช่างผู้เชี่ยวชาญ): 092-393-7770", fill="#2D2820", font=f_sub_bold)
    d.text((1685, 1385), "• ศูนย์ราชการ อาคาร B & สตูดิโอที่บ้าน", fill="#5A554C", font=f_sub)
    d.text((1685, 1430), "ยินดีให้คำปรึกษาและนัดตรวจวัดสายตา", fill="#757065", font=f_sub)

    draw_clean_button(d, [1705, 1495, 2420, 1585], "📞 โทรหาเราทันที >", f_btn)

    # ==========================================
    # 5. UNIFORM BUTTONS FOR CARDS 1, 2, 5
    # ==========================================
    draw_clean_button(d, [65, 775, 780, 865], "ดูโปรโมชันทั้งหมด >", f_btn)
    draw_clean_button(d, [885, 775, 1600, 865], "ดูตารางบูท >", f_btn)
    draw_clean_button(d, [885, 1495, 1600, 1585], "เช็กสถานะแว่นตา >", f_btn)

    # Save final high-res output
    out_name = "rich_menu_luxury_custom_sathien.jpg"
    final_rgb = base.convert("RGB")
    final_rgb.save(out_name, "JPEG", quality=95, optimize=True)
    print(f"Rich Menu successfully generated: {out_name} ({os.path.getsize(out_name)/1024:.1f} KB)")
    return out_name

if __name__ == "__main__":
    build_rich_menu()
