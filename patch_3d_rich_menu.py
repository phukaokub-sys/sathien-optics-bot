import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def patch_and_perfect_3d_menu():
    src_path = "C:/Users/Administrator/.gemini/antigravity/brain/bd4e2114-09d7-49d9-a028-5fcd2873c6e4/.user_uploaded/media_1795442129232_a6ab2b9c.jpg"
    raw_img = Image.open(src_path)
    
    # Scale to standard LINE Rich Menu size: 2500 x 1686
    base = raw_img.resize((2500, 1686), Image.Resampling.LANCZOS)
    draw = ImageDraw.Draw(base)

    # Fonts
    font_bold_path = "C:/Windows/Fonts/leelawadb.ttf"
    font_path = "C:/Windows/Fonts/leelawad.ttf"
    if not os.path.exists(font_bold_path):
        font_bold_path = font_path

    font_title = ImageFont.truetype(font_bold_path, 82)
    font_sub = ImageFont.truetype(font_bold_path, 42)
    font_badge = ImageFont.truetype(font_bold_path, 34)
    font_btn = ImageFont.truetype(font_bold_path, 44)

    # 1. Clean and Stamp Tile 1 (Orange: บูทสัญจร)
    # Text area: x from 250 to 560, y from 160 to 520
    # Button: x from 70 to 760, y from 670 to 780
    # Clean Title
    draw.rounded_rectangle([250, 190, 560, 310], radius=16, fill="#FF5E36")
    draw.text((260, 200), "บูทสัญจร", fill="#FFFFFF", font=font_title)
    
    # Clean Subtitle
    draw.rounded_rectangle([60, 390, 560, 560], radius=16, fill="#FF5E36")
    draw.multiline_text((70, 400), "เช็กจุดออกบูทวันนี้\nสัปดาห์นี้พ่อไปงานไหน", fill="#FFFFFF", font=font_sub, spacing=14)
    
    # Clean Button
    draw.rounded_rectangle([80, 680, 750, 785], radius=32, fill="#FFFFFF")
    draw.text((250, 705), "ดูพิกัดบูท ➔", fill="#EB2F06", font=font_btn)

    # 2. Clean and Stamp Tile 2 (Green: แผนที่ร้าน)
    # Title
    draw.rounded_rectangle([1080, 190, 1500, 310], radius=16, fill="#00D28E")
    draw.text((1090, 200), "แผนที่ร้าน", fill="#FFFFFF", font=font_title)
    
    # Subtitle
    draw.rounded_rectangle([890, 390, 1420, 560], radius=16, fill="#00D28E")
    draw.multiline_text((900, 400), "ชั้นล่าง อาคาร B ตรงข้าม AIS\n(แตะเปิด Maps นำทางทันที)", fill="#FFFFFF", font=font_sub, spacing=14)
    
    # Button
    draw.rounded_rectangle([910, 680, 1580, 785], radius=32, fill="#FFFFFF")
    draw.text((1110, 705), "เปิด MAPS 📍", fill="#059669", font=font_btn)

    # 3. Clean and Stamp Tile 3 (Blue: เช็คสถานะ)
    # Title
    draw.rounded_rectangle([1910, 190, 2260, 310], radius=16, fill="#2F8DF5")
    draw.text((1920, 200), "เช็กสถานะ", fill="#FFFFFF", font=font_title)
    
    # Subtitle
    draw.rounded_rectangle([1720, 390, 2240, 560], radius=16, fill="#2F8DF5")
    draw.multiline_text((1730, 400), "เลขพัสดุ / เลข Flash\nหรือกรอกที่อยู่จัดส่งฟรี", fill="#FFFFFF", font=font_sub, spacing=14)
    
    # Button
    draw.rounded_rectangle([1740, 680, 2410, 785], radius=32, fill="#FFFFFF")
    draw.text((1960, 705), "เช็กสถานะ ➔", fill="#1D4ED8", font=font_btn)

    # 4. Clean and Stamp Tile 4 (Purple: สลิปสายตา)
    # Title
    draw.rounded_rectangle([270, 1020, 720, 1140], radius=16, fill="#9952E8")
    draw.text((280, 1030), "สลิปสายตา", fill="#FFFFFF", font=font_title)
    
    # Subtitle
    draw.rounded_rectangle([60, 1220, 600, 1380], radius=16, fill="#9952E8")
    draw.multiline_text((70, 1230), "ดูประวัติวัดสายตา\nสลิปจากคอมพิวเตอร์", fill="#FFFFFF", font=font_sub, spacing=14)
    
    # Button
    draw.rounded_rectangle([80, 1510, 750, 1615], radius=32, fill="#FFFFFF")
    draw.text((240, 1535), "ดูสลิปสายตา ➔", fill="#7C3AED", font=font_btn)

    # 5. Clean and Stamp Tile 5 (Pink: บริการหลังการขาย - FIX THE TYPO!)
    # Title
    draw.rounded_rectangle([1100, 1020, 1630, 1150], radius=16, fill="#E6397E")
    draw.text((1110, 1035), "บริการหลังขาย", fill="#FFFFFF", font=font_title)
    
    # Subtitle
    draw.rounded_rectangle([890, 1220, 1500, 1380], radius=16, fill="#E6397E")
    draw.multiline_text((900, 1230), "มีปัญหาแว่นไม่กระชับ\nติดต่อ คุณเสถียร ได้เลย", fill="#FFFFFF", font=font_sub, spacing=14)
    
    # Button
    draw.rounded_rectangle([910, 1510, 1580, 1615], radius=32, fill="#FFFFFF")
    draw.text((1060, 1535), "โทรหาคุณเสถียร 📞", fill="#BE185D", font=font_btn)

    # 6. Clean and Stamp Tile 6 (Red: โทรด่วน - FIX "คุณพะ" -> "คุณนก"!)
    # Title
    draw.rounded_rectangle([1930, 1020, 2350, 1140], radius=16, fill="#EA3A54")
    draw.text((1940, 1030), "โทรด่วน", fill="#FFFFFF", font=font_title)
    
    # Subtitle
    draw.rounded_rectangle([1720, 1220, 2440, 1380], radius=16, fill="#EA3A54")
    draw.multiline_text((1730, 1230), "• คุณนก: 085-433-6699\n• คุณเสถียร: 092-393-7770", fill="#FFFFFF", font=font_sub, spacing=14)
    
    # Button
    draw.rounded_rectangle([1740, 1510, 2410, 1615], radius=32, fill="#FFFFFF")
    draw.text((1960, 1535), "โทรหาร้าน ➔", fill="#B91C1C", font=font_btn)

    # Save
    out_path = os.path.join(os.getcwd(), "rich_menu_3d_pixar.png")
    base.save(out_path, "PNG", quality=95)
    print(f"3D Pixar Rich Menu with 100% correct Thai text saved at: {out_path}")

if __name__ == "__main__":
    patch_and_perfect_3d_menu()
