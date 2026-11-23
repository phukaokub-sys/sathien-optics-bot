import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_luxury_menu():
    W, H = 2500, 1686
    # 1. Base Canvas - Luxury Porcelain White with delicate Sage Green flowing waves
    img = Image.new('RGB', (W, H), (255, 255, 255))
    draw = ImageDraw.Draw(img)

    # Background luxury curves (matching Attachment 2)
    bg_curves = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    c_draw = ImageDraw.Draw(bg_curves)
    # Wave 1: Soft Sage
    c_draw.polygon([(0, 0), (W, 0), (W, 350), (0, 700)], fill=(240, 253, 244, 255)) # #F0FDF4
    # Wave 2: Delicate Mint
    c_draw.polygon([(W//2, H), (W, H//2), (W, H), (W//2, H)], fill=(236, 253, 245, 255)) # #ECFDF5
    # Wave 3: Flowing curves in bottom-left
    c_draw.ellipse([-200, H - 600, 800, H + 400], fill=(240, 253, 244, 200))
    img.paste(bg_curves, (0, 0), bg_curves)

    # Fonts
    font_bold_path = "C:/Windows/Fonts/LeelaUIb.ttf"
    if not os.path.exists(font_bold_path):
        font_bold_path = "C:/Windows/Fonts/leelawdb.ttf"

    font_header_title = ImageFont.truetype(font_bold_path, 64)
    font_header_sub = ImageFont.truetype(font_bold_path, 28)
    font_header_badge = ImageFont.truetype(font_bold_path, 32)

    font_tag = ImageFont.truetype(font_bold_path, 28)
    font_title = ImageFont.truetype(font_bold_path, 62)
    font_sub = ImageFont.truetype(font_bold_path, 34)
    font_btn = ImageFont.truetype(font_bold_path, 40)

    # 2. Header Brand Ribbon (y: 0 to 185)
    draw.rectangle([0, 0, W, 185], fill="#FFFFFF", outline="#D1FAE5", width=2)
    # Delicate gold hairline at bottom of ribbon
    draw.line([(0, 184), (W, 184)], fill="#CA8A04", width=3)

    # Mascot on left
    owl_path = "green_owl_clean.png"
    owl_img = None
    if os.path.exists(owl_path):
        owl_img = Image.open(owl_path).convert("RGBA")
        owl_scaled = owl_img.resize((105, 140), Image.Resampling.LANCZOS)
        img.paste(owl_scaled, (45, 22), owl_scaled)

    # Header Brand Text
    draw.text((170, 32), "เสถียรการแว่น", fill="#14532D", font=font_header_title) # Forest Green
    draw.text((175, 115), "ศูนย์ราชการแจ้งวัฒนะ อาคาร B ชั้น 1 โซน MILLION MALL • ตรงข้าม AIS", fill="#166534", font=font_header_sub)

    # Header Right Contact Pill (Gold/Champagne)
    contact_pill_text = "📞 085-433-6699 • 092-393-7770"
    cp_bbox = font_header_badge.getbbox(contact_pill_text)
    cp_w = cp_bbox[2] - cp_bbox[0] + 50
    cp_h = 68
    cp_x = W - 45 - cp_w
    cp_y = 58
    draw.rounded_rectangle([cp_x, cp_y, cp_x + cp_w, cp_y + cp_h], radius=34, fill="#FEF3C7", outline="#D97706", width=2)
    draw.text((cp_x + 25, cp_y + 14), contact_pill_text, fill="#92400E", font=font_header_badge)

    # 3. The 6 Luxury Cards Grid (y: 205 to 1665)
    margin_x = 42
    gap_x = 34
    card_w = (W - (margin_x * 2) - (gap_x * 2)) // 3 # ~782px
    card_h = 715
    row1_y = 210
    row2_y = 950

    cards = [
        # Col 0, Row 0: Promotion
        {
            "col": 0, "row": 0, "y": row1_y,
            "bg": "#FFFFFF", "border": "#CA8A04", "border_w": 3,
            "tag": "👑 SPECIAL PROMOTION", "tag_bg": "#FEF3C7", "tag_border": "#F59E0B", "tag_fg": "#92400E",
            "title": "โปรโมชั่นพิเศษ",
            "sub": "กรอบ + เลนส์ เริ่มต้น 990.-\nมัลติโค้ต • บลู • ออโต้ • โปรเกรสซีฟ",
            "btn_bg": "#14532D", "btn_border": "#CA8A04", "btn_fg": "#FEF08A",
            "btn_text": "ดูโปรโมชั่นพิเศษ >",
            "icon_type": "promo"
        },
        # Col 1, Row 0: Pop-Up Event
        {
            "col": 1, "row": 0, "y": row1_y,
            "bg": "#FFFFFF", "border": "#A7F3D0", "border_w": 2,
            "tag": "🎪 POP-UP EVENT", "tag_bg": "#ECFDF5", "tag_border": "#10B981", "tag_fg": "#065F46",
            "title": "พิกัดบูทสัญจร",
            "sub": "เช็กจุดออกบูธสัปดาห์นี้\nคุณพ่อไปจัดงานที่ไหน",
            "btn_bg": "#059669", "btn_border": "#047857", "btn_fg": "#FFFFFF",
            "btn_text": "ดูพิกัดบูทสัญจร >",
            "icon_type": "booth"
        },
        # Col 2, Row 0: Google Maps
        {
            "col": 2, "row": 0, "y": row1_y,
            "bg": "#FFFFFF", "border": "#A7F3D0", "border_w": 2,
            "tag": "📍 GOOGLE MAPS", "tag_bg": "#D1FAE5", "tag_border": "#059669", "tag_fg": "#064E3B",
            "title": "แผนที่ร้านหลัก",
            "sub": "ศูนย์ราชการ อาคาร B ชั้น 1\n(โซน Million Mall ตรงข้าม AIS)",
            "btn_bg": "#047857", "btn_border": "#064E3B", "btn_fg": "#FFFFFF",
            "btn_text": "เปิด GOOGLE MAPS 📍",
            "icon_type": "maps"
        },
        # Col 0, Row 1: Fast Delivery
        {
            "col": 0, "row": 1, "y": row2_y,
            "bg": "#FFFFFF", "border": "#BFDBFE", "border_w": 2,
            "tag": "🚚 FAST DELIVERY", "tag_bg": "#EFF6FF", "tag_border": "#3B82F6", "tag_fg": "#1E40AF",
            "title": "เช็กสถานะแว่นตา",
            "sub": "เลขพัสดุ Flash Express\nหรือกรอกที่อยู่จัดส่งฟรี",
            "btn_bg": "#1D4ED8", "btn_border": "#1E40AF", "btn_fg": "#FFFFFF",
            "btn_text": "เช็กสถานะพัสดุ >",
            "icon_type": "delivery"
        },
        # Col 1, Row 1: Satien Care
        {
            "col": 1, "row": 1, "y": row2_y,
            "bg": "#FFFFFF", "border": "#FBCFE8", "border_w": 2,
            "tag": "🛠️ SATIEN CARE", "tag_bg": "#FDF2F8", "tag_border": "#EC4899", "tag_fg": "#9D174D",
            "title": "บริการหลังการขาย",
            "sub": "แว่นหลวม ไม่สบายตา ซ่อมฟรี\nปรึกษา คุณเสถียร ได้เลย",
            "btn_bg": "#BE185D", "btn_border": "#9D174D", "btn_fg": "#FFFFFF",
            "btn_text": "โทรหาคุณเสถียร 📞",
            "icon_type": "care"
        },
        # Col 2, Row 1: Direct Call
        {
            "col": 2, "row": 1, "y": row2_y,
            "bg": "#FFFFFF", "border": "#FED7AA", "border_w": 2,
            "tag": "📞 CONTACT US", "tag_bg": "#FFFBEB", "tag_border": "#D97706", "tag_fg": "#78350F",
            "title": "โทรติดต่อร้าน",
            "sub": "• คุณนก: 085-433-6699\n• คุณเสถียร: 092-393-7770",
            "btn_bg": "#D97706", "btn_border": "#B45309", "btn_fg": "#FFFFFF",
            "btn_text": "โทรหาร้านทันที >",
            "icon_type": "call"
        }
    ]

    for c in cards:
        x1 = margin_x + c["col"] * (card_w + gap_x)
        y1 = c["y"]
        x2 = x1 + card_w
        y2 = y1 + card_h

        # 1. Floating shadow
        shadow = Image.new('RGBA', (card_w + 30, card_h + 30), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.rounded_rectangle([15, 15, card_w + 15, card_h + 15], radius=36, fill=(0, 0, 0, 22))
        shadow = shadow.filter(ImageFilter.GaussianBlur(12))
        img.paste(shadow, (x1 - 15, y1 - 15), shadow)

        # 2. Card base
        draw.rounded_rectangle([x1, y1, x2, y2], radius=34, fill=c["bg"], outline=c["border"], width=c["border_w"])

        # Top soft gradient header in each card
        card_header = Image.new('RGBA', (card_w, 90), (0, 0, 0, 0))
        ch_draw = ImageDraw.Draw(card_header)
        ch_draw.rounded_rectangle([0, 0, card_w, 90], radius=34, fill=(240, 253, 244, 130))
        img.paste(card_header, (x1, y1), card_header)

        # 3. Category Tag
        tag_text = c["tag"]
        tb = font_tag.getbbox(tag_text)
        tw = tb[2] - tb[0]
        th = tb[3] - tb[1]
        pw = tw + 36
        ph = 50
        tag_x = x1 + 30
        tag_y = y1 + 24
        draw.rounded_rectangle([tag_x, tag_y, tag_x + pw, tag_y + ph], radius=24, fill=c["tag_bg"], outline=c["tag_border"], width=2)
        draw.text((tag_x + 18, tag_y + (ph - th)//2 - 2), tag_text, fill=c["tag_fg"], font=font_tag)

        # 4. Draw Elegant Luxury Graphics on Right
        ix = x2 - 200
        iy = y1 + 105
        if c["icon_type"] == "promo":
            # Gold glasses + price circle
            gx, gy = ix + 10, iy + 25
            draw.rounded_rectangle([gx, gy, gx+70, gy+46], radius=16, outline="#CA8A04", width=4)
            draw.rounded_rectangle([gx+85, gy, gx+155, gy+46], radius=16, outline="#CA8A04", width=4)
            draw.line([(gx+70, gy+22), (gx+85, gy+22)], fill="#CA8A04", width=4)
            # Sparkle
            draw.line([(gx+140, gy-10), (gx+140, gy+5)], fill="#F59E0B", width=3)
            draw.line([(gx+132, gy-2), (gx+148, gy-2)], fill="#F59E0B", width=3)
            # Gold price pill
            font_p = ImageFont.truetype(font_bold_path, 26)
            draw.rounded_rectangle([gx+20, gy+60, gx+145, gy+98], radius=16, fill="#FEF08A", outline="#CA8A04", width=2)
            draw.text((gx+34, gy+66), "เริ่ม 990.-", fill="#854D0E", font=font_p)

        elif c["icon_type"] == "booth":
            # Emerald Event Tent
            bx, by = ix + 30, iy + 20
            draw.polygon([(bx+65, by), (bx+10, by+85), (bx+120, by+85)], fill="#ECFDF5", outline="#059669", width=3)
            draw.polygon([(bx+65, by), (bx+38, by+85), (bx+92, by+85)], fill="#D1FAE5")
            draw.rectangle([bx+25, by+85, bx+105, by+120], fill="#FFFFFF", outline="#059669", width=3)

        elif c["icon_type"] == "maps":
            # Location Pin
            mx, my = ix + 35, iy + 15
            draw.ellipse([mx+20, my, mx+95, my+75], fill="#D1FAE5", outline="#047857", width=3)
            draw.polygon([(mx+28, my+52), (mx+58, my+120), (mx+87, my+52)], fill="#047857")
            draw.ellipse([mx+43, my+23, mx+73, my+53], fill="#FFFFFF")

        elif c["icon_type"] == "delivery":
            # Express Delivery Box with Speed lines
            dx, dy = ix + 20, iy + 30
            draw.rectangle([dx+15, dy+15, dx+115, dy+95], fill="#EFF6FF", outline="#1D4ED8", width=3)
            draw.line([(dx+15, dy+45), (dx+115, dy+45)], fill="#3B82F6", width=2)
            draw.line([(dx+65, dy+15), (dx+65, dy+95)], fill="#3B82F6", width=2)
            # Motion trails
            draw.line([(dx-10, dy+30), (dx+8, dy+30)], fill="#3B82F6", width=3)
            draw.line([(dx-20, dy+55), (dx+8, dy+55)], fill="#3B82F6", width=4)
            draw.line([(dx-10, dy+80), (dx+8, dy+80)], fill="#3B82F6", width=3)

        elif c["icon_type"] == "care" and owl_img:
            # Official store owl mascot
            m_scaled = owl_img.resize((120, 160), Image.Resampling.LANCZOS)
            img.paste(m_scaled, (ix + 35, iy + 15), m_scaled)

        elif c["icon_type"] == "call":
            # Phone Handset / Service
            px, py = ix + 35, iy + 20
            draw.rounded_rectangle([px+20, py+5, px+90, py+125], radius=20, fill="#FFFBEB", outline="#D97706", width=3)
            draw.rectangle([px+30, py+24, px+80, py+100], fill="#FEF3C7")
            draw.ellipse([px+48, py+106, px+62, py+120], fill="#D97706")

        # 5. Main Title
        tx = x1 + 32
        ty = y1 + 115
        draw.text((tx, ty), c["title"], fill="#14532D", font=font_title)

        # 6. Subtitle
        sy = ty + 95
        draw.multiline_text((tx, sy), c["sub"], fill="#334155", font=font_sub, spacing=14)

        # 7. Luxury Action Button at bottom
        bx1 = x1 + 30
        by1 = y2 - 130
        bx2 = x2 - 30
        by2 = y2 - 38
        # Outer button shadow
        draw.rounded_rectangle([bx1+2, by1+3, bx2+2, by2+3], radius=30, fill="#00000020")
        # Solid luxury button base
        draw.rounded_rectangle([bx1, by1, bx2, by2], radius=30, fill=c["btn_bg"], outline=c["btn_border"], width=2)
        # Gloss highlight
        draw.rounded_rectangle([bx1+6, by1+3, bx2-6, by1+20], radius=15, fill="#FFFFFF35")

        # Centered button text + arrow
        btn_txt = c["btn_text"]
        btb = font_btn.getbbox(btn_txt)
        btw = btb[2] - btb[0]
        bth = btb[3] - btb[1]
        btx = bx1 + (bx2 - bx1 - btw) // 2
        bty = by1 + (by2 - by1 - bth) // 2 - 3
        draw.text((btx, bty), btn_txt, fill=c["btn_fg"], font=font_btn)

    # Save final JPG under 1MB
    out_path = os.path.join(os.getcwd(), "rich_menu_luxury_green_gold.jpg")
    img.save(out_path, "JPEG", quality=92, optimize=True)
    print(f"Luxury Green/Gold Rich Menu created: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")
    return out_path

if __name__ == "__main__":
    create_luxury_menu()
