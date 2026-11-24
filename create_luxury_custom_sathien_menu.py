import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def generate_perfect_menu():
    # Always load fresh base resized from the user's uploaded original
    src_path = "C:/Users/Administrator/.gemini/antigravity/brain/bd4e2114-09d7-49d9-a028-5fcd2873c6e4/.user_uploaded/media_1795514773586_98b21bb2.jpg"
    orig = Image.open(src_path)
    base = orig.resize((2500, 1686), Image.Resampling.LANCZOS).convert("RGBA")

    # Fonts
    font_bold = "fonts/Prompt-Bold.ttf"
    font_semibold = "fonts/Prompt-SemiBold.ttf"
    font_medium = "fonts/Prompt-Medium.ttf"

    f_title = ImageFont.truetype(font_bold, 64)
    f_c3_title = ImageFont.truetype(font_bold, 60)
    f_sub_bold = ImageFont.truetype(font_semibold, 34)
    f_sub_c3 = ImageFont.truetype(font_semibold, 31)
    f_sub_c3_small = ImageFont.truetype(font_medium, 27)
    f_sub = ImageFont.truetype(font_medium, 30)
    f_sub_small = ImageFont.truetype(font_medium, 27)
    f_header_phone = ImageFont.truetype(font_bold, 36)
    f_btn = ImageFont.truetype(font_bold, 45)

    def seamless_patch(img, box, bg_color, radius=12, blur=6):
        x1, y1, x2, y2 = box
        w = max(10, x2 - x1)
        h = max(10, y2 - y1)
        patch = Image.new("RGBA", (w, h), bg_color)
        mask = Image.new("L", (w, h), 0)
        m_draw = ImageDraw.Draw(mask)
        m_draw.rounded_rectangle([blur, blur, w - blur, h - blur], radius=radius, fill=255)
        mask = mask.filter(ImageFilter.GaussianBlur(blur))
        img.paste(patch, (x1, y1), mask)

    def draw_clean_button(draw, box, text, font):
        x1, y1, x2, y2 = box
        draw.rounded_rectangle([x1, y1+4, x2, y2+4], radius=32, fill="#00000030")
        draw.rounded_rectangle([x1, y1, x2, y2], radius=32, fill="#122538", outline="#25384D", width=2)
        draw.rounded_rectangle([x1+6, y1+3, x2-6, y1+16], radius=16, fill="#FFFFFF25")
        bbox = font.getbbox(text)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
        tx = x1 + (x2 - x1 - tw) // 2
        ty = y1 + (y2 - y1 - th) // 2 - 4
        draw.text((tx, ty), text, fill="#FFFFFF", font=font)

    # 1. HEADER (PHONE AREA)
    seamless_patch(base, [1720, 45, 2465, 145], (235, 233, 226, 255), radius=10, blur=6)
    d = ImageDraw.Draw(base)
    phone_text = "📞 085-433-6699 (คุณนก) • 092-393-7770 (คุณเสถียร)"
    bbox_p = f_header_phone.getbbox(phone_text)
    tw_p = bbox_p[2] - bbox_p[0]
    d.text((2460 - tw_p, 65), phone_text, fill="#3D3830", font=f_header_phone)

    # 2. CARD 3: แผนที่ร้านเสถียร (HOME GOOGLE MAPS & GOV CENTER)
    seamless_patch(base, [1675, 495, 2220, 765], (242, 242, 237, 255), radius=16, blur=8)
    d = ImageDraw.Draw(base)
    d.text((1685, 510), "แผนที่ร้านเสถียร", fill="#111111", font=f_c3_title)
    d.text((1685, 595), "🏡 ร้านที่บ้าน: The Plant-Light รังสิต", fill="#2D2820", font=f_sub_c3)
    d.text((1685, 642), "🏢 ศูนย์ราชการ แจ้งวัฒนะ อาคาร B", fill="#2D2820", font=f_sub_c3)
    d.text((1685, 690), "• หน้าร้านชั้น 1 (ตรงข้าม AIS) 08:30-15:00 น.", fill="#5A554C", font=f_sub_c3_small)
    d.text((1685, 725), "• สตูดิโอที่บ้านเปิดทุกวัน (นัดหมายล่วงหน้า)", fill="#5A554C", font=f_sub_c3_small)
    draw_clean_button(d, [1705, 775, 2420, 865], "📍 เปิด Google Maps >", f_btn)

    # 3. CARD 4: บริการหลังการขาย (Completely wipe "บริกๆ" and old overlapping text!)
    # Top-left patch: Erases "บริกๆ"
    seamless_patch(base, [50, 1025, 420, 1130], (235, 234, 229, 255), radius=10, blur=5)
    # Mid-left patch: Erases old "บริการหลังการขาย"
    seamless_patch(base, [50, 1130, 520, 1235], (235, 234, 229, 255), radius=10, blur=5)
    # Lower patch: Erases old bullets
    seamless_patch(base, [50, 1235, 770, 1475], (235, 234, 229, 255), radius=10, blur=6)

    d = ImageDraw.Draw(base)
    d.text((65, 1135), "บริการหลังการขาย", fill="#111111", font=f_title)
    d.text((65, 1250), "✨ เปลี่ยนแป้นจมูก & ดัดทรง ฟรี", fill="#2D2820", font=f_sub_bold)
    d.text((65, 1325), "🛠️ บริการดูแลและซ่อมฟรีตลอดการใช้งาน", fill="#2D2820", font=f_sub_bold)
    d.text((65, 1395), "• แวะมาพบกันได้ที่บูทและหน้าร้านประจำ", fill="#5A554C", font=f_sub)
    draw_clean_button(d, [65, 1495, 780, 1585], "นัดเข้ารับบริการ >", f_btn)

    # 4. CARD 5: เช็กสถานะแว่นตา (REMOVE QR CODE!)
    seamless_patch(base, [1420, 1250, 1590, 1470], (239, 236, 231, 255), radius=12, blur=6)
    d = ImageDraw.Draw(base)
    draw_clean_button(d, [885, 1495, 1600, 1585], "เช็กสถานะแว่นตา >", f_btn)

    # 5. CARD 6: โทรติดต่อร้าน (Completely wipe "สาขาลุมพินี", old numbers, and QR code!)
    # Top-left patch: Erases "สาขาลุมพินี"
    seamless_patch(base, [1680, 1025, 2030, 1130], (243, 243, 235, 255), radius=10, blur=5)
    # Mid-left patch: Erases old "โทรติดต่อร้าน"
    seamless_patch(base, [1680, 1130, 2150, 1230], (243, 243, 235, 255), radius=10, blur=5)
    # Lower patch: Erases old branches & QR code
    seamless_patch(base, [1680, 1230, 2445, 1475], (243, 243, 235, 255), radius=10, blur=6)

    d = ImageDraw.Draw(base)
    d.text((1690, 1135), "โทรติดต่อร้าน", fill="#111111", font=f_title)
    d.text((1690, 1245), "📞 คุณนก (ดูแลร้าน/ส่งแว่น): 085-433-6699", fill="#2D2820", font=f_sub_bold)
    d.text((1690, 1315), "📞 คุณเสถียร (ช่างผู้เชี่ยวชาญ): 092-393-7770", fill="#2D2820", font=f_sub_bold)
    d.text((1690, 1380), "🏢 ศูนย์ราชการ แจ้งวัฒนะ อาคาร B", fill="#5A554C", font=f_sub)
    d.text((1690, 1425), "🏡 สตูดิโอที่บ้าน The Plant-Light ติวานนท์-รังสิต", fill="#5A554C", font=f_sub_small)
    draw_clean_button(d, [1705, 1495, 2420, 1585], "📞 โทรหาเราทันที >", f_btn)

    # 6. OTHER BUTTONS
    draw_clean_button(d, [65, 775, 780, 865], "ดูโปรโมชันทั้งหมด >", f_btn)
    draw_clean_button(d, [885, 775, 1600, 865], "ดูตารางบูท >", f_btn)

    # Save final image
    final_rgb = base.convert("RGB")
    out_path = "rich_menu_perfect_final.jpg"
    final_rgb.save(out_path, "JPEG", quality=95, optimize=True)
    print(f"Generated {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")

    # Save verification crops
    final_rgb.crop((35, 950, 810, 1640)).save("verify_final_c4.jpg")
    final_rgb.crop((850, 950, 1630, 1640)).save("verify_final_c5.jpg")
    final_rgb.crop((1670, 950, 2455, 1640)).save("verify_final_c6.jpg")
    print("Verification crops saved successfully!")
    return out_path

if __name__ == "__main__":
    generate_perfect_menu()
