import sqlite3
import os
import json
import base64
import threading
import urllib.request
import urllib.error
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.path.join(os.path.dirname(__file__), "sathien_optics.db")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "").strip()
GITHUB_REPO = os.getenv("GITHUB_REPO", "").strip()
GITHUB_DB_BRANCH = os.getenv("GITHUB_DB_BRANCH", "db-storage").strip()

def restore_db_from_cloud():
    """
    Downloads the persistent database file from GitHub cloud storage branch on startup.
    This prevents database wipeout when Render spins up a new container or redeploys!
    """
    token = os.getenv("GITHUB_TOKEN", GITHUB_TOKEN).strip()
    repo = os.getenv("GITHUB_REPO", GITHUB_REPO).strip()
    branch = os.getenv("GITHUB_DB_BRANCH", GITHUB_DB_BRANCH).strip()

    if not token or not repo:
        print("[INFO] Cloud DB persistence not configured (GITHUB_TOKEN/GITHUB_REPO unset). Using local SQLite.")
        return False

    try:
        url = f"https://api.github.com/repos/{repo}/contents/sathien_optics.db?ref={branch}"
        req = urllib.request.Request(
            url,
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Sathien-Optics-Bot"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            raw_b64 = data.get("content", "")
            if raw_b64:
                db_bytes = base64.b64decode(raw_b64)
                with open(DB_PATH, "wb") as f:
                    f.write(db_bytes)
                print(f"[SUCCESS] Restored {len(db_bytes)} bytes of sathien_optics.db from cloud branch '{branch}'!")
                return True
    except urllib.error.HTTPError as he:
        if he.code == 404:
            print(f"[INFO] Cloud branch '{branch}' has no sathien_optics.db yet. Initializing fresh.")
        else:
            print(f"[WARN] HTTP {he.code} while restoring database from cloud: {he}")
    except Exception as e:
        print(f"[WARN] Could not restore database from cloud: {e}")

    return False


def backup_db_to_cloud():
    """
    Uploads the latest SQLite database file to GitHub cloud storage branch.
    """
    token = os.getenv("GITHUB_TOKEN", GITHUB_TOKEN).strip()
    repo = os.getenv("GITHUB_REPO", GITHUB_REPO).strip()
    branch = os.getenv("GITHUB_DB_BRANCH", GITHUB_DB_BRANCH).strip()

    if not token or not repo or not os.path.exists(DB_PATH):
        return False

    try:
        # 1. Read local DB
        with open(DB_PATH, "rb") as f:
            content_b64 = base64.b64encode(f.read()).decode("utf-8")

        # 2. Get current SHA if file exists
        sha = None
        get_url = f"https://api.github.com/repos/{repo}/contents/sathien_optics.db?ref={branch}"
        get_req = urllib.request.Request(
            get_url,
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Sathien-Optics-Bot"
            }
        )
        try:
            with urllib.request.urlopen(get_req, timeout=8) as r:
                meta = json.loads(r.read().decode("utf-8"))
                sha = meta.get("sha")
        except urllib.error.HTTPError as he:
            if he.code != 404:
                print(f"[WARN] Error fetching remote SHA for backup: {he.code}")

        # 3. Put file to GitHub
        payload = {
            "message": "Automated SQLite database cloud backup [skip ci]",
            "content": content_b64,
            "branch": branch
        }
        if sha:
            payload["sha"] = sha

        put_url = f"https://api.github.com/repos/{repo}/contents/sathien_optics.db"
        put_req = urllib.request.Request(
            put_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json",
                "User-Agent": "Sathien-Optics-Bot"
            },
            method="PUT"
        )
        with urllib.request.urlopen(put_req, timeout=12) as r:
            res = json.loads(r.read().decode("utf-8"))
            commit_sha = res.get("commit", {}).get("sha", "")[:8]
            print(f"[SUCCESS] Database backed up to cloud branch '{branch}' (Commit: {commit_sha})")
            return True
    except Exception as e:
        print(f"[WARN] Failed to backup database to cloud: {e}")
        return False


def async_backup_db():
    """
    Triggers asynchronous backup in a daemon thread so it never blocks web requests.
    """
    threading.Thread(target=backup_db_to_cloud, daemon=True).start()


def upload_file_to_cloud(local_filepath, remote_path):
    """
    Uploads any media file (image/slip/promo) to the persistent GitHub cloud branch 'db-storage'.
    Returns the permanent public raw URL or None.
    """
    token = os.getenv("GITHUB_TOKEN", GITHUB_TOKEN).strip()
    repo = os.getenv("GITHUB_REPO", GITHUB_REPO).strip()
    branch = os.getenv("GITHUB_DB_BRANCH", GITHUB_DB_BRANCH).strip()

    if not token or not repo or not os.path.exists(local_filepath):
        return None

    try:
        with open(local_filepath, "rb") as f:
            content_b64 = base64.b64encode(f.read()).decode("utf-8")

        # 1. Check if remote file exists to obtain sha
        sha = None
        get_url = f"https://api.github.com/repos/{repo}/contents/{remote_path}?ref={branch}"
        get_req = urllib.request.Request(
            get_url,
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
                "User-Agent": "Sathien-Optics-Bot"
            }
        )
        try:
            with urllib.request.urlopen(get_req, timeout=8) as r:
                meta = json.loads(r.read().decode("utf-8"))
                sha = meta.get("sha")
        except urllib.error.HTTPError as he:
            if he.code != 404:
                print(f"[WARN] Error fetching remote SHA for {remote_path}: {he.code}")

        # 2. Put file to GitHub
        payload = {
            "message": f"Upload cloud media {remote_path} [skip ci]",
            "content": content_b64,
            "branch": branch
        }
        if sha:
            payload["sha"] = sha

        put_url = f"https://api.github.com/repos/{repo}/contents/{remote_path}"
        put_req = urllib.request.Request(
            put_url,
            data=json.dumps(payload).encode("utf-8"),
            headers={
                "Authorization": f"token {token}",
                "Accept": "application/vnd.github.v3+json",
                "Content-Type": "application/json",
                "User-Agent": "Sathien-Optics-Bot"
            },
            method="PUT"
        )
        with urllib.request.urlopen(put_req, timeout=15) as r:
            res = json.loads(r.read().decode("utf-8"))
            download_url = res.get("content", {}).get("download_url") or f"https://raw.githubusercontent.com/{repo}/{branch}/{remote_path}"
            print(f"[SUCCESS] Uploaded {remote_path} to cloud branch '{branch}' -> {download_url}")
            return download_url
    except Exception as e:
        print(f"[WARN] Failed to upload {remote_path} to cloud: {e}")
        return None


def async_upload_file_to_cloud(local_filepath, remote_path):
    """
    Triggers asynchronous media upload in background thread.
    """
    threading.Thread(target=upload_file_to_cloud, args=(local_filepath, remote_path), daemon=True).start()


def restore_file_from_cloud(remote_path, local_filepath):
    """
    Fetches a missing file from GitHub 'db-storage' branch and saves locally.
    """
    token = os.getenv("GITHUB_TOKEN", GITHUB_TOKEN).strip()
    repo = os.getenv("GITHUB_REPO", GITHUB_REPO).strip()
    branch = os.getenv("GITHUB_DB_BRANCH", GITHUB_DB_BRANCH).strip()

    if not repo:
        return False

    try:
        raw_url = f"https://raw.githubusercontent.com/{repo}/{branch}/{remote_path}"
        req = urllib.request.Request(
            raw_url,
            headers={
                "Authorization": f"token {token}" if token else "",
                "User-Agent": "Sathien-Optics-Bot"
            }
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = resp.read()
            os.makedirs(os.path.dirname(local_filepath), exist_ok=True)
            with open(local_filepath, "wb") as f:
                f.write(data)
            print(f"[SUCCESS] Restored {len(data)} bytes of {remote_path} from cloud storage!")
            return True
    except Exception as e:
        print(f"[INFO] Could not restore {remote_path} from cloud: {e}")
        return False


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    # Attempt restore from cloud storage before opening db
    restore_db_from_cloud()

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
        image_url TEXT,
        is_active INTEGER DEFAULT 1,
        sort_order INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Migration for promotions image_url column
    try:
        cursor.execute("ALTER TABLE promotions ADD COLUMN image_url TEXT")
    except Exception:
        pass

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

    # 6. Admin subscribers table (Receives instant LINE push notifications for orders/slips)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS admin_subscribers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        line_user_id TEXT UNIQUE NOT NULL,
        name TEXT DEFAULT 'แอดมิน',
        role TEXT DEFAULT 'ผู้ดูแลร้าน',
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # 7. Appointments table (Home Studio & Gov Center booking)
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        booking_no TEXT UNIQUE,
        line_user_id TEXT,
        customer_name TEXT,
        phone TEXT,
        preferred_location TEXT DEFAULT 'สตูดิโอที่บ้าน (ติวานนท์-รังสิต)',
        booking_date TEXT,
        booking_time TEXT,
        service_type TEXT DEFAULT 'ตรวจวัดสายตาประกอบแว่น',
        notes TEXT,
        status TEXT DEFAULT 'รอยืนยันนัดหมาย',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # Seed default booth schedule if empty
    cursor.execute("SELECT COUNT(*) FROM booth_schedules")
    if cursor.fetchone()[0] == 0:
        cursor.execute("""
        INSERT INTO booth_schedules (date_range, location, note, is_active)
        VALUES ('สัปดาห์นี้', 'ศูนย์ราชการเฉลิมพระเกียรติฯ อาคาร B (ร้านประจำ ชั้นล่าง ตรงข้าม AIS)', 'เปิดวันจันทร์ - ศุกร์ 08:30 - 15:00 น.', 1)
        """)

    # Seed verified shop admins so alerts are delivered immediately
    default_admins = [
        ("Uabb7ed0d05d8b7fc7acfa833b8f35825", "คุณภูเขา (แอดมิน)", "ผู้ดูแลระบบ"),
        ("U1e144d473da3315db0e73ba163ea97f2", "คุณนก (เสถียรการแว่น)", "เจ้าของร้าน/ผู้จัดการ")
    ]
    for uid, adm_name, adm_role in default_admins:
        cursor.execute("""
        INSERT INTO admin_subscribers (line_user_id, name, role, is_active)
        VALUES (?, ?, ?, 1)
        ON CONFLICT(line_user_id) DO UPDATE SET
            name = excluded.name,
            role = excluded.role,
            is_active = 1
        """, (uid, adm_name, adm_role))

    # Clean up dummy test subscribers
    cursor.execute("DELETE FROM admin_subscribers WHERE line_user_id LIKE 'Utest_%'")

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

def get_all_line_users():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT user_id, display_name, phone, last_seen FROM line_users ORDER BY last_seen DESC LIMIT 30")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

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
    async_backup_db()
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
    async_backup_db()

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
    async_backup_db()

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

    # If line_user_id is not provided, try to find from phone only
    if not line_user_id and phone:
        cursor.execute("SELECT user_id FROM line_users WHERE phone LIKE ? LIMIT 1", (f"%{phone[-8:]}%",))
        row = cursor.fetchone()
        if row:
            line_user_id = row["user_id"]
        else:
            line_user_id = ""

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
    async_backup_db()
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
    async_backup_db()

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

def add_promotion(title, price, tag, color="#EA580C", details="", sort_order=0, image_url=""):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO promotions (title, price, tag, color, details, sort_order, image_url, is_active)
    VALUES (?, ?, ?, ?, ?, ?, ?, 1)
    """, (title, price, tag, color, details, sort_order, image_url))
    promo_id = cursor.lastrowid
    conn.commit()
    conn.close()
    async_backup_db()
    return promo_id

def update_promotion(promo_id, title, price, tag, color="#EA580C", details="", sort_order=0, image_url="", is_active=1):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    UPDATE promotions 
    SET title = ?, price = ?, tag = ?, color = ?, details = ?, sort_order = ?, image_url = ?, is_active = ?
    WHERE id = ?
    """, (title, price, tag, color, details, sort_order, image_url, is_active, promo_id))
    conn.commit()
    conn.close()
    async_backup_db()

def delete_promotion(promo_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM promotions WHERE id = ?", (promo_id,))
    conn.commit()
    conn.close()
    async_backup_db()

# Admin subscriber functions
def register_admin_subscriber(line_user_id, name="แอดมิน", role="ผู้ดูแลร้าน"):
    if not line_user_id:
        return False
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("""
    INSERT INTO admin_subscribers (line_user_id, name, role, is_active)
    VALUES (?, ?, ?, 1)
    ON CONFLICT(line_user_id) DO UPDATE SET
        name = CASE WHEN excluded.name != '' THEN excluded.name ELSE name END,
        role = CASE WHEN excluded.role != '' THEN excluded.role ELSE role END,
        is_active = 1
    """, (line_user_id, name, role))
    conn.commit()
    conn.close()
    async_backup_db()
    return True

def get_active_admin_subscribers():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, line_user_id, name, role, created_at FROM admin_subscribers WHERE is_active = 1")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def get_all_admin_subscribers():
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, line_user_id, name, role, is_active, created_at FROM admin_subscribers ORDER BY created_at DESC")
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def delete_admin_subscriber(subscriber_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM admin_subscribers WHERE id = ?", (subscriber_id,))
    conn.commit()
    conn.close()
    async_backup_db()

def toggle_admin_subscriber(subscriber_id, is_active):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE admin_subscribers SET is_active = ? WHERE id = ?", (is_active, subscriber_id))
    conn.commit()
    conn.close()
    async_backup_db()

# Appointment functions (Home Studio & Gov Center)
def create_appointment(line_user_id, customer_name, phone, preferred_location, booking_date, booking_time, service_type="ตรวจวัดสายตาประกอบแว่น", notes=""):
    conn = get_db()
    cursor = conn.cursor()
    booking_no = f"AP-{datetime.now().strftime('%y%m%d')}-{phone[-4:] if len(phone) >= 4 else '0000'}"
    
    if not line_user_id and phone:
        cursor.execute("SELECT user_id FROM line_users WHERE phone LIKE ? LIMIT 1", (f"%{phone[-8:]}%",))
        row = cursor.fetchone()
        if row:
            line_user_id = row["user_id"]
        else:
            line_user_id = get_latest_line_user()

    cursor.execute("""
    INSERT INTO appointments (booking_no, line_user_id, customer_name, phone, preferred_location, booking_date, booking_time, service_type, notes, status)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, 'รอยืนยันนัดหมาย')
    """, (booking_no, line_user_id, customer_name, phone, preferred_location, booking_date, booking_time, service_type, notes))
    conn.commit()
    conn.close()
    async_backup_db()
    return booking_no

def get_recent_appointments(limit=30):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM appointments ORDER BY id DESC LIMIT ?", (limit,))
    rows = cursor.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def update_appointment_status(appointment_id, status):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("UPDATE appointments SET status = ? WHERE id = ?", (status, appointment_id))
    conn.commit()
    conn.close()
    async_backup_db()

def delete_appointment(appointment_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM appointments WHERE id = ?", (appointment_id,))
    conn.commit()
    conn.close()
    async_backup_db()

if __name__ == "__main__":
    init_db()
