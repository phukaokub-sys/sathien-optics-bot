import os
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

def create_rich_menu():
    W, H = 2500, 1686
    # 1. Base Canvas - Deep Luxury Navy/Slate
    img = Image.new('RGB', (W, H), (15, 23, 42)) # #0F172A
    draw = ImageDraw.Draw(img)

    # Subtle ambient lighting in background
    glow = Image.new('RGBA', (W, H), (0, 0, 0, 0))
    g_draw = ImageDraw.Draw(glow)
    g_draw.ellipse([200, 100, 1200, 900], fill=(255, 138, 0, 30))
    g_draw.ellipse([1400, 200, 2400, 1000], fill=(16, 185, 129, 25))
    g_draw.ellipse([800, 800, 1800, 1600], fill=(236, 72, 153, 25))
    glow = glow.filter(ImageFilter.GaussianBlur(120))
    img.paste(glow, (0, 0), glow)

    # Fonts
    font_bold_path = "C:/Windows/Fonts/LeelaUIb.ttf"
    if not os.path.exists(font_bold_path):
        font_bold_path = "C:/Windows/Fonts/leelawdb.ttf"

    font_tag = ImageFont.truetype(font_bold_path, 34)
    font_title = ImageFont.truetype(font_bold_path, 76)
    font_sub = ImageFont.truetype(font_bold_path, 42)
    font_sub_sm = ImageFont.truetype(font_bold_path, 38)
    font_btn = ImageFont.truetype(font_bold_path, 46)

    # 2. Card layout definition (3 cols x 2 rows)
    margin_x = 45
    margin_y = 45
    gap_x = 35
    gap_y = 35
    card_w = (W - (margin_x * 2) - (gap_x * 2)) // 3 # ~776px
    card_h = (H - (margin_y * 2) - gap_y) // 2      # ~780px

    cards = [
        # Col 0, Row 0: Promotion
        {
            "col": 0, "row": 0,
            "c_top": (255, 56, 56), "c_bot": (234, 88, 12), # Red to Orange
            "border": "#FDE047", "border_w": 5, # Golden border for Star Promo!
            "tag": "🔥 HOT DEAL • PROMOTION",
            "tag_bg": "#7F1D1D", "tag_fg": "#FEF08A",
            "title": "โปรโมชั่นพิเศษ",
            "sub": "กรอบ + เลนส์ เริ่มต้น 990.-\nเลนส์บลู • ออโต้ • โปรเกรสซีฟ",
            "btn_text": "ดูโปรโมชั่น ➔", "btn_fg": "#DC2626",
            "type": "promo"
        },
        # Col 1, Row 0: Pop-up Event
        {
            "col": 1, "row": 0,
            "c_top": (249, 115, 22), "c_bot": (194, 65, 12), # Orange to Amber
            "border": "#FED7AA", "border_w": 3,
            "tag": "🎪 POP-UP EVENT",
            "tag_bg": "#7C2D12", "tag_fg": "#FFEDD5",
            "title": "พิกัดบูทสัญจร",
            "sub": "เช็กจุดออกบูธสัปดาห์นี้\nพ่อไปจัดงานที่ไหน",
            "btn_text": "ดูพิกัดบูท ➔", "btn_fg": "#EA580C",
            "type": "booth"
        },
        # Col 2, Row 0: Google Maps
        {
            "col": 2, "row": 0,
            "c_top": (16, 185, 129), "c_bot": (4, 120, 87), # Mint to Emerald
            "border": "#A7F3D0", "border_w": 3,
            "tag": "📍 GOOGLE MAPS",
            "tag_bg": "#064E3B", "tag_fg": "#D1FAE5",
            "title": "แผนที่ร้านหลัก",
            "sub": "ศูนย์ราชการ อาคาร B ชั้นล่าง\n(ตรงข้าม AIS นำทางทันที)",
            "btn_text": "เปิด MAPS 📍", "btn_fg": "#059669",
            "type": "maps"
        },
        # Col 0, Row 1: Fast Delivery
        {
            "col": 0, "row": 1,
            "c_top": (59, 130, 246), "c_bot": (29, 78, 216), # Blue to Indigo
            "border": "#BFDBFE", "border_w": 3,
            "tag": "🚚 FAST DELIVERY",
            "tag_bg": "#1E3A8A", "tag_fg": "#DBEAFE",
            "title": "เช็กสถานะแว่นตา",
            "sub": "เลขพัสดุ Flash Express\nหรือกรอกที่อยู่จัดส่งฟรี",
            "btn_text": "เช็กสถานะ ➔", "btn_fg": "#1D4ED8",
            "type": "delivery"
        },
        # Col 1, Row 1: Satien Care
        {
            "col": 1, "row": 1,
            "c_top": (236, 72, 153), "c_bot": (190, 24, 93), # Pink to Magenta
            "border": "#FBCFE8", "border_w": 3,
            "tag": "🛠️ SATIEN CARE",
            "tag_bg": "#831843", "tag_fg": "#FCE7F3",
            "title": "บริการหลังการขาย",
            "sub": "แว่นหลวม ไม่สบายตา ซ่อมฟรี\nติดต่อ คุณเสถียร ได้เลย",
            "btn_text": "โทรหาคุณเสถียร 📞", "btn_fg": "#BE185D",
            "type": "care"
        },
        # Col 2, Row 1: Call Store
        {
            "col": 2, "row": 1,
            "c_top": (244, 63, 94), "c_bot": (185, 28, 28), # Rose to Crimson
            "border": "#FECDD3", "border_w": 3,
            "tag": "📞 CALL STORE",
            "tag_bg": "#881337", "tag_fg": "#FFE4E6",
            "title": "โทรติดต่อร้าน",
            "sub": "• คุณนก: 085-433-6699\n• คุณเสถียร: 092-393-7770",
            "btn_text": "โทรหาร้าน ➔", "btn_fg": "#B91C1C",
            "type": "call"
        }
    ]

    # Load mascot
    mascot_img = None
    if os.path.exists("owl_mascot.png"):
        mascot_img = Image.open("owl_mascot.png").convert("RGBA")

    for c in cards:
        x1 = margin_x + c["col"] * (card_w + gap_x)
        y1 = margin_y + c["row"] * (card_h + gap_y)
        x2 = x1 + card_w
        y2 = y1 + card_h

        # 1. Draw outer shadow
        shadow = Image.new('RGBA', (card_w + 30, card_h + 30), (0, 0, 0, 0))
        s_draw = ImageDraw.Draw(shadow)
        s_draw.rounded_rectangle([15, 15, card_w + 15, card_h + 15], radius=40, fill=(0, 0, 0, 110))
        shadow = shadow.filter(ImageFilter.GaussianBlur(15))
        img.paste(shadow, (x1 - 15, y1 - 15), shadow)

        # 2. Draw gradient card
        card_img = Image.new('RGBA', (card_w, card_h), (0, 0, 0, 0))
        c_draw = ImageDraw.Draw(card_img)
        c_top = c["c_top"]
        c_bot = c["c_bot"]
        for y in range(card_h):
            ratio = y / float(card_h)
            r = int(c_top[0] * (1 - ratio) + c_bot[0] * ratio)
            g = int(c_top[1] * (1 - ratio) + c_bot[1] * ratio)
            b = int(c_top[2] * (1 - ratio) + c_bot[2] * ratio)
            c_draw.line([(0, y), (card_w, y)], fill=(r, g, b, 255))

        # Card mask with rounded rectangle
        mask = Image.new('L', (card_w, card_h), 0)
        m_draw = ImageDraw.Draw(mask)
        m_draw.rounded_rectangle([0, 0, card_w, card_h], radius=38, fill=255)

        # Subtle card top gloss highlight
        gloss = Image.new('RGBA', (card_w, card_h // 2), (255, 255, 255, 25))
        card_img.paste(gloss, (0, 0), gloss)

        img.paste(card_img, (x1, y1), mask)

        # Draw card border
        draw.rounded_rectangle([x1, y1, x2, y2], radius=38, outline=c["border"], width=c["border_w"])

        # 3. Floating Category Tag at top
        tag_text = c["tag"]
        tb = font_tag.getbbox(tag_text)
        tw = tb[2] - tb[0]
        th = tb[3] - tb[1]
        tag_box_w = tw + 46
        tag_box_h = 56
        tag_x = x1 + 35
        tag_y = y1 + 35
        draw.rounded_rectangle([tag_x, tag_y, tag_x + tag_box_w, tag_y + tag_box_h], radius=28, fill=c["tag_bg"], outline=c["border"], width=2)
        draw.text((tag_x + 23, tag_y + (tag_box_h - th) // 2 - 3), tag_text, fill=c["tag_fg"], font=font_tag)

        # 4. Draw Mascot / Graphics inside card
        if c["type"] == "care" and mascot_img:
            # Place Owl Mascot at right of title
            m_scaled = mascot_img.resize((210, 268), Image.Resampling.LANCZOS)
            img.paste(m_scaled, (x2 - 240, y1 + 105), m_scaled)
        elif c["type"] == "promo":
            # Draw sleek glasses graphic + 990.- badge
            gx = x2 - 270
            gy = y1 + 120
            # Glasses frames
            draw.rounded_rectangle([gx, gy, gx+105, gy+80], radius=26, outline="#FFFFFF", width=6)
            draw.rounded_rectangle([gx+125, gy, gx+230, gy+80], radius=26, outline="#FFFFFF", width=6)
            draw.line([(gx+105, gy+38), (gx+125, gy+38)], fill="#FFFFFF", width=6)
            # Golden price star badge
            draw.rounded_rectangle([gx+35, gy+100, gx+200, gy+155], radius=20, fill="#FEF08A", outline="#CA8A04", width=3)
            font_price = ImageFont.truetype(font_bold_path, 34)
            draw.text((gx+52, gy+110), "เริ่ม 990.-", fill="#991B1B", font=font_price)
        elif c["type"] == "maps":
            # Map Pin icon
            mx = x2 - 210
            my = y1 + 125
            draw.ellipse([mx+25, my, mx+135, my+110], fill="#FFFFFF", outline="#047857", width=4)
            draw.polygon([(mx+35, my+75), (mx+80, my+175), (mx+125, my+75)], fill="#FFFFFF")
            draw.ellipse([mx+58, my+32, mx+102, my+76], fill="#059669")
        elif c["type"] == "booth":
            # Tent / Booth Icon
            bx = x2 - 225
            by = y1 + 125
            draw.polygon([(bx+85, by), (bx+10, by+120), (bx+160, by+120)], fill="#FFFFFF", outline="#C2410C", width=3)
            draw.polygon([(bx+85, by), (bx+45, by+120), (bx+125, by+120)], fill="#FED7AA")
            draw.rectangle([bx+30, by+120, bx+140, by+165], fill="#FFFFFF", outline="#C2410C", width=3)
        elif c["type"] == "delivery":
            # Delivery Box / Truck
            dx = x2 - 225
            dy = y1 + 125
            draw.rectangle([dx+10, dy+35, dx+115, dy+120], fill="#FFFFFF", outline="#1E3A8A", width=4)
            draw.polygon([(dx+115, dy+55), (dx+160, dy+85), (dx+160, dy+120), (dx+115, dy+120)], fill="#FFFFFF", outline="#1E3A8A", width=4)
            draw.ellipse([dx+30, dy+110, dx+65, dy+145], fill="#1E3A8A")
            draw.ellipse([dx+110, dy+110, dx+145, dy+145], fill="#1E3A8A")
        elif c["type"] == "call":
            # Phone icon
            px = x2 - 215
            py = y1 + 125
            draw.rounded_rectangle([px+30, py+10, px+130, py+170], radius=24, fill="#FFFFFF", outline="#881337", width=4)
            draw.rectangle([px+45, py+35, px+115, py+135], fill="#FFE4E6")
            draw.ellipse([px+70, py+145, px+90, py+165], fill="#881337")

        # 5. Title & Subtitle
        tx = x1 + 40
        ty = y1 + 125
        # Title with drop shadow
        draw.text((tx+3, ty+3), c["title"], fill="#00000045", font=font_title)
        draw.text((tx, ty), c["title"], fill="#FFFFFF", font=font_title)

        # Subtitle
        sy = ty + 105
        f_sub = font_sub if len(c["sub"]) < 50 else font_sub_sm
        draw.multiline_text((tx+2, sy+2), c["sub"], fill="#00000045", font=f_sub, spacing=14)
        draw.multiline_text((tx, sy), c["sub"], fill="#FFFFFF", font=f_sub, spacing=14)

        # 6. Glossy Pill Button at Bottom
        bx1 = x1 + 40
        by1 = y2 - 145
        bx2 = x2 - 40
        by2 = y2 - 45
        # Button shadow
        draw.rounded_rectangle([bx1+2, by1+5, bx2+2, by2+5], radius=32, fill="#00000035")
        # White button base
        draw.rounded_rectangle([bx1, by1, bx2, by2], radius=32, fill="#FFFFFF", outline="#E2E8F0", width=2)
        # Gloss top highlight
        draw.rounded_rectangle([bx1+8, by1+4, bx2-8, by1+24], radius=16, fill="#FFFFFF80")
        # Button text centered
        btn_txt = c["btn_text"]
        btn_bbox = font_btn.getbbox(btn_txt)
        btw = btn_bbox[2] - btn_bbox[0]
        bth = btn_bbox[3] - btn_bbox[1]
        btx = bx1 + (bx2 - bx1 - btw) // 2
        bty = by1 + (by2 - by1 - bth) // 2 - 4
        draw.text((btx, bty), btn_txt, fill=c["btn_fg"], font=font_btn)

    # Save final JPG under 1MB
    out_path = os.path.join(os.getcwd(), "rich_menu_commercial_promo.jpg")
    img.save(out_path, "JPEG", quality=90, optimize=True)
    print(f"Commercial Promotion Rich Menu created successfully at: {out_path} ({os.path.getsize(out_path)/1024:.1f} KB)")

if __name__ == "__main__":
    create_rich_menu()
