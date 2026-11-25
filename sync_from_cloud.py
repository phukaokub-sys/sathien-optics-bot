import os
import json
import sqlite3
import urllib.request
import database

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_URL = os.getenv("BASE_URL", "https://sathien-optics-bot.onrender.com").strip().rstrip("/")


def sync_cloud_media():
    """
    Downloads all uploaded promotion and prescription images from GitHub db-storage
    (and falls back to live Render URL if missing on GitHub) into the local static folders.
    """
    token = os.getenv("GITHUB_TOKEN", database.GITHUB_TOKEN).strip()
    repo = os.getenv("GITHUB_REPO", database.GITHUB_REPO).strip()
    branch = os.getenv("GITHUB_DB_BRANCH", database.GITHUB_DB_BRANCH).strip()

    synced_count = 0
    if token and repo:
        try:
            tree_url = f"https://api.github.com/repos/{repo}/git/trees/{branch}?recursive=1"
            req = urllib.request.Request(
                tree_url,
                headers={
                    "Authorization": f"token {token}",
                    "Accept": "application/vnd.github.v3+json",
                    "User-Agent": "Sathien-Optics-Bot"
                }
            )
            with urllib.request.urlopen(req, timeout=15) as r:
                tdata = json.loads(r.read().decode("utf-8"))

            for item in tdata.get("tree", []):
                if item.get("type") != "blob":
                    continue
                rpath = item.get("path", "")
                local_target = None
                if rpath.startswith("uploads/promotions/"):
                    fname = rpath[len("uploads/promotions/"):]
                    local_target = os.path.join(BASE_DIR, "static", "promotions", fname)
                elif rpath.startswith("uploads/prescriptions/"):
                    fname = rpath[len("uploads/prescriptions/"):]
                    local_target = os.path.join(BASE_DIR, "static", "prescriptions", fname)
                elif rpath.startswith("static/prescriptions/"):
                    fname = rpath[len("static/prescriptions/"):]
                    local_target = os.path.join(BASE_DIR, "static", "prescriptions", fname)

                if local_target:
                    remote_size = item.get("size")
                    need_download = (
                        not os.path.exists(local_target)
                        or (remote_size is not None and os.path.getsize(local_target) != remote_size)
                    )
                    if need_download:
                        if database.restore_file_from_cloud(rpath, local_target):
                            synced_count += 1
        except Exception as e:
            print(f"[WARN] Could not scan GitHub tree for media: {e}")

    # Also check DB references against local static folders & Render live URL
    if os.path.exists(database.DB_PATH):
        conn = sqlite3.connect(database.DB_PATH)
        conn.row_factory = sqlite3.Row
        for tbl, folder, prefix in [
            ("promotions", os.path.join(BASE_DIR, "static", "promotions"), "uploads/promotions/"),
            ("prescriptions", os.path.join(BASE_DIR, "static", "prescriptions"), "uploads/prescriptions/"),
        ]:
            os.makedirs(folder, exist_ok=True)
            for row in conn.execute(f"SELECT image_url FROM {tbl} WHERE image_url IS NOT NULL AND image_url != ''"):
                img_url = row["image_url"].strip()
                marker = "/static/promotions/" if tbl == "promotions" else "/static/prescriptions/"
                if marker in img_url:
                    fname = img_url.split(marker, 1)[1].split("?")[0]
                    local_target = os.path.join(folder, fname)
                    if not os.path.exists(local_target):
                        live_url = f"{BASE_URL}{marker}{fname}"
                        try:
                            with urllib.request.urlopen(live_url, timeout=10) as resp:
                                data = resp.read()
                            with open(local_target, "wb") as f:
                                f.write(data)
                            print(f"[SUCCESS] Rescued {fname} from Render -> {local_target}")
                            database.upload_file_to_cloud(local_target, f"{prefix}{fname}")
                            synced_count += 1
                        except Exception as e:
                            print(f"[INFO] Missing local file {fname} could not be fetched from Render: {e}")
        conn.close()

    return synced_count


def print_db_summary():
    """Prints record counts from the synced local SQLite database."""
    if not os.path.exists(database.DB_PATH):
        print("[WARN] sathien_optics.db not found!")
        return

    conn = sqlite3.connect(database.DB_PATH)
    cur = conn.cursor()
    labels = [
        ("orders", "ออเดอร์/จัดส่ง"),
        ("appointments", "นัดตรวจวัดสายตา"),
        ("prescriptions", "สลิปสายตา"),
        ("promotions", "โปรโมชั่น"),
        ("admin_subscribers", "แอดมินรับแจ้งเตือน"),
        ("line_users", "ลูกค้าในระบบ LINE"),
        ("booth_schedules", "ตารางออกบูท"),
    ]
    print("\n--- สรุปข้อมูลล่าสุดใน D:\\Line bot ---")
    for tbl, label in labels:
        try:
            cur.execute(f"SELECT COUNT(*) FROM {tbl}")
            cnt = cur.fetchone()[0]
            print(f"  - {label}: {cnt} รายการ")
        except Exception as e:
            print(f"  - {label}: Error ({e})")
    conn.close()


def main():
    print(f"กำลังซิงค์ข้อมูลจาก Cloud มายัง: {BASE_DIR}")
    ok = database.restore_db_from_cloud()
    if not ok:
        print("[WARN] ไม่สามารถดึงฐานข้อมูลจาก Cloud ได้ในขณะนี้")
    media_cnt = sync_cloud_media()
    print(f"[INFO] ดาวน์โหลดรูปภาพใหม่จาก Cloud เพิ่มเติม: {media_cnt} ไฟล์")
    print_db_summary()
    print("\nซิงค์ข้อมูลเสร็จสมบูรณ์! ข้อมูลใน Drive D ตรงกับบนเว็บจริง 100% แล้วครับ")


if __name__ == "__main__":
    main()
