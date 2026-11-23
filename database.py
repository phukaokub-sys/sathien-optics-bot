import sqlite3
import os
from datetime import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), "sathien_optics.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cursor = conn.cursor()

    # 1. Orders table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_no TEXT UNIQUE,
        line_user_id TEXT,
        customer_name TEXT,
        phone TEXT,
        address TEXT,
        order_details TEXT,
        status TEXT DEFAULT 'รับคำสั่งตัดแล้ว',
        tracking_no TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 2. Booth Schedule table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS booth_schedules (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date_range TEXT,
        location TEXT,
        note TEXT,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 3. Prescriptions & Family Eye Exam table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS prescriptions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        line_user_id TEXT,
        phone TEXT,
        customer_name TEXT,
        patient_name TEXT,
        relation TEXT DEFAULT 'เจ้าของบัญชี',
        exam_date TEXT,
        sph_r TEXT,
        cyl_r TEXT,
        axis_r TEXT,
        add_r TEXT,
        sph_l TEXT,
        cyl_l TEXT,
        axis_l TEXT,
        add_l TEXT,
        pd TEXT,
        image_url TEXT,
        notes TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Auto migrate columns if table was created in older version
    cursor.execute("PRAGMA table_info(prescriptions)")
    existing_cols = [c[1] for c in cursor.fetchall()]
    new_cols = [
        ("line_user_id", "TEXT"),
        ("patient_name", "TEXT"),
        ("relation", "TEXT DEFAULT 'เจ้าของบัญชี'"),
        ("sph_r", "TEXT"),
        ("cyl_r", "TEXT"),
        ("axis_r", "TEXT"),
        ("add_r", "TEXT"),
        ("sph_l", "TEXT"),
        ("cyl_l", "TEXT"),
        ("axis_l", "TEXT"),
        ("add_l", "TEXT"),
        ("pd", "TEXT"),
        ("notes", "TEXT"),
    ]
    for col_name, col_type in new_cols:
        if col_name not in existing_cols:
            cursor.execute(f"ALTER TABLE prescriptions ADD COLUMN {col_name} {col_type}")

    # 5. Promotions table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS promotions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT,
        price TEXT,
        tag TEXT,
        color TEXT DEFAULT '#EA580C',
        details TEXT,
        is_active INTEGER DEFAULT 1,
        sort_order INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Seed default promotions if empty
    cursor.execute("SELECT COUNT(*) FROM promotions")
    if cursor.fetchone()[0] == 0:
        default_promos = [
            ("ชุดตัดแว่นเริ่มต้น", "990", "🔥 โปรสุดคุ้ม ยอดนิยม", "#EA580C", 
             "✨ กรอบแว่นแฟชั่น น้ำหนักเบา (เลือกได้ทั้งร้าน)\n✨ เลนส์ Multicoat สารเคลือบตัดแสงสะท้อน\n✨ ป้องกันรอยขีดข่วน + ภาพคมชัดสบายตา\n✨ ตรวจวัดสายตาฟรีด้วยระบบคอมพิวเตอร์\n🎁 ฟรีกล่องใส่แว่น + ผ้าเช็ดเลนส์ไมโครไฟเบอร์", 1, 1),
            ("ชุดถนอมสายตา Blue Block", "1,490", "💻 สำหรับคนทำงานหน้าจอ", "#2563EB", 
             "✨ กรอบแว่น TR90 ยืดหยุ่น ทนทาน ไม่บีบขมับ\n✨ เลนส์กรองแสงสีฟ้า 100% จากจอคอมและมือถือ\n✨ ลดอาการตาล้า แสบตา ปวดศีรษะจากการจ้องจอนาน\n✨ ตรวจวัดสายตาฟรีด้วยระบบคอมพิวเตอร์\n🎁 ฟรีกล่องใส่แว่น + ผ้าเช็ดเลนส์ไมโครไฟเบอร์", 1, 2),
            ("ชุดออกแดดเปลี่ยนสี Auto", "1,990", "☀️ 2-in-1 แว่นสายตา+กันแดด", "#7C3AED", 
             "✨ ในร่มเป็นเลนส์ใส ออกแดดปรับเข้มเป็นกันแดดอัตโนมัติ\n✨ ป้องกันรังสี UV400 ได้ 100% ปกป้องจอประสาทตา\n✨ ตัดแสงสะท้อน สบายตาทุกสภาพแสง ไม่ต้องสลับแว่น\n✨ ตรวจวัดสายตาฟรีด้วยระบบคอมพิวเตอร์\n🎁 ฟรีกล่องใส่แว่น + ผ้าเช็ดเลนส์ไมโครไฟเบอร์", 1, 3),
            ("ชุดเลนส์โปรเกรสซีฟ", "3,500", "👑 สบายตา มองใกล้-ไกลไร้รอยต่อ", "#BE185D", 
             "✨ สำหรับผู้มีสายตายาวตามวัย (40+) มองใกล้-ไกลครบในอันเดียว\n✨ เลนส์ไร้รอยต่อ บุคลิกภาพดี ไม่ต้องคอยถอดแว่นเข้า-ออก\n✨ ปรับฟิตติ้งโครงสร้างเลนส์เฉพาะบุคคลโดย คุณเสถียร\n✨ รับประกันความสบายตา ดัดทรง ปรับแต่งฟรีตลอดชีพ\n🎁 ฟรีกล่องใส่แว่นพรีเมียม + ผ้าไมโครไฟเบอร์", 1, 4)
        ]
        cursor.executemany("""
        INSERT INTO promotions (title, price, tag, color, details, is_active, sort_order)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """, default_promos)

    # 4. Line users table (Tracks active LINE users for easy auto-linking)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS line_users (
        user_id TEXT PRIMARY KEY,
        display_name TEXT,
        phone TEXT,
        last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Seed default booth schedule if empty
    cursor.execute("SELECT COUNT(*) FROM booth_schedules")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO booth_schedules (date_range, location, note, is_active)
        VALUES ('สัปดาห์นี้', 'ศูนย์ราชการเฉลิมพระเกียรติฯ อาคาร B (ร้านประจำ ชั้นล่าง ตรงข้าม AIS)', 'เปิดวันจันทร์ - ศุกร์ 08:30 - 15:30 น.', 1)
        """)

    conn.commit()
    conn.close()
    print("Database initialized successfully at:", DB_PATH)

# LINE User tracking functions
def record_line_user(user_id, display_name="", phone=""):
    if not user_id:
        return
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO line_users (user_id, display_name, phone, last_seen)
    VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    ON CONFLICT(user_id) DO UPDATE SET
        display_name = CASE WHEN excluded.display_name != '' THEN excluded.display_name ELSE display_name END,
        phone = CASE WHEN excluded.phone != '' THEN excluded.phone ELSE phone END,
        last_seen = CURRENT_TIMESTAMP
    """, (user_id, display_name, phone))
    conn.commit()
    conn.close()

def get_latest_line_user():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id FROM line_users ORDER BY last_seen DESC LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row["user_id"] if row else ""

def link_user_phone(phone, user_id):
    if not phone or not user_id:
        return
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE line_users SET phone = ? WHERE user_id = ?", (phone, user_id))
    cursor.execute("UPDATE orders SET line_user_id = ? WHERE phone LIKE ? AND (line_user_id IS NULL OR line_user_id = '')", (user_id, f"%{phone}%"))
    conn.commit()
    conn.close()

# Order functions
def create_order(line_user_id, customer_name, phone, address, order_details=""):
    conn = get_db()
    cursor = conn.cursor()
    order_no = f"SO-{datetime.now().strftime('%y%m%d')}-{phone[-4:] if len(phone) >= 4 else '0000'}"
    
    # If line_user_id is missing, try to auto-resolve from phone or latest active user
    if not line_user_id:
        cursor.execute("SELECT user_id FROM line_users WHERE phone LIKE ? LIMIT 1", (f"%{phone[-8:]}%",))
        row = cursor.fetchone()
        if row:
            line_user_id = row["user_id"]
        else:
            line_user_id = get_latest_line_user()

    cursor.execute("""
    INSERT INTO orders (order_no, line_user_id, customer_name, phone, address, order_details, status)
    VALUES (?, ?, ?, ?, ?, ?, 'กำลังสั่งเลนส์/ตัดประกอบ')
    ON CONFLICT(order_no) DO UPDATE SET
        line_user_id = CASE WHEN excluded.line_user_id != '' THEN excluded.line_user_id ELSE line_user_id END,
        customer_name = excluded.customer_name,
        address = excluded.address,
        updated_at = CURRENT_TIMESTAMP
    """, (order_no, line_user_id, customer_name, phone, address, order_details))
    conn.commit()
    conn.close()
    return order_no

def get_order_by_phone(phone):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders WHERE phone LIKE ? ORDER BY id DESC LIMIT 1", (f"%{phone.strip()}%",))
    row = cursor.fetchone()
    conn.close()
    return dict(row) if row else None

def get_recent_orders():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM orders ORDER BY id DESC LIMIT 20")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_order_status(order_id, status, tracking_no=""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE orders 
    SET status = ?, tracking_no = ?, updated_at = CURRENT_TIMESTAMP
    WHERE id = ?
    """, (status, tracking_no, order_id))
    conn.commit()
    conn.close()

# Booth schedule functions
def get_active_schedules():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM booth_schedules WHERE is_active = 1 ORDER BY id DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_booth_schedule(date_range, location, note=""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO booth_schedules (date_range, location, note, is_active)
    VALUES (?, ?, ?, 1)
    """, (date_range, location, note))
    conn.commit()
    conn.close()

# Prescription & Family Member Eye Exam functions
def add_prescription(line_user_id, phone, customer_name, patient_name, relation, 
                     sph_r="", cyl_r="", axis_r="", add_r="",
                     sph_l="", cyl_l="", axis_l="", add_l="",
                     pd="", image_url="", notes="", exam_date=""):
    conn = get_db()
    cursor = conn.cursor()
    if not exam_date:
        exam_date = datetime.now().strftime("%d/%m/%Y")
    if not patient_name:
        patient_name = customer_name or "คุณลูกค้า"
    if not relation:
        relation = "เจ้าของบัญชี"

    # If line_user_id is not provided, try to find from phone or latest active line user
    if not line_user_id and phone:
        cursor.execute("SELECT user_id FROM line_users WHERE phone LIKE ? LIMIT 1", (f"%{phone[-8:]}%",))
        row = cursor.fetchone()
        if row:
            line_user_id = row["user_id"]
        else:
            line_user_id = get_latest_line_user()

    cursor.execute("""
    INSERT INTO prescriptions (
        line_user_id, phone, customer_name, patient_name, relation, exam_date,
        sph_r, cyl_r, axis_r, add_r,
        sph_l, cyl_l, axis_l, add_l,
        pd, image_url, notes
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        line_user_id, phone, customer_name, patient_name, relation, exam_date,
        sph_r, cyl_r, axis_r, add_r,
        sph_l, cyl_l, axis_l, add_l,
        pd, image_url, notes
    ))
    rx_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return rx_id, line_user_id

def get_prescriptions_by_user(user_id=None, phone=None):
    conn = get_db()
    cursor = conn.cursor()
    # Auto-resolve phone from line_users if phone was not explicitly passed
    if user_id and not phone:
        cursor.execute("SELECT phone FROM line_users WHERE user_id = ?", (user_id,))
        p_row = cursor.fetchone()
        if p_row and p_row["phone"]:
            phone = p_row["phone"]

    rows = []
    if user_id and phone:
        cursor.execute("""
        SELECT * FROM prescriptions 
        WHERE line_user_id = ? OR phone LIKE ? 
        ORDER BY id DESC
        """, (user_id, f"%{phone[-8:]}%"))
        rows = cursor.fetchall()
    elif user_id:
        cursor.execute("""
        SELECT * FROM prescriptions 
        WHERE line_user_id = ? 
        ORDER BY id DESC
        """, (user_id,))
        rows = cursor.fetchall()
    elif phone:
        cursor.execute("""
        SELECT * FROM prescriptions 
        WHERE phone LIKE ? 
        ORDER BY id DESC
        """, (f"%{phone[-8:]}%",))
        rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_prescriptions(limit=30):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM prescriptions ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_prescription(rx_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM prescriptions WHERE id = ?", (rx_id,))
    conn.commit()
    conn.close()

# Promotion functions
def get_active_promotions():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM promotions WHERE is_active = 1 ORDER BY sort_order ASC, id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_promotions():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM promotions ORDER BY sort_order ASC, id ASC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def add_promotion(title, price, tag, color="#EA580C", details="", sort_order=0):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO promotions (title, price, tag, color, details, sort_order, is_active)
    VALUES (?, ?, ?, ?, ?, ?, 1)
    """, (title, price, tag, color, details, sort_order))
    promo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return promo_id

def update_promotion(promo_id, title, price, tag, color="#EA580C", details="", is_active=1):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE promotions 
    SET title = ?, price = ?, tag = ?, color = ?, details = ?, is_active = ?
    WHERE id = ?
    """, (title, price, tag, color, details, is_active, promo_id))
    conn.commit()
    conn.close()

def delete_promotion(promo_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM promotions WHERE id = ?", (promo_id,))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()
