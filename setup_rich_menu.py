import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")
IMAGE_PATH = os.path.join(os.path.dirname(__file__), "rich_menu_luxury_custom_sathien.jpg")

headers_json = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

def setup_rich_menu():
    print("1. Cleaning up old rich menus...")
    list_res = requests.get("https://api.line.me/v2/bot/richmenu/list", headers=headers_json)
    if list_res.status_code == 200:
        for rm in list_res.json().get("richmenus", []):
            rm_id = rm["richMenuId"]
            requests.delete(f"https://api.line.me/v2/bot/richmenu/{rm_id}", headers=headers_json)
            print(f"Deleted old rich menu: {rm_id}")

    print("2. Creating new Luxury Cream/Gold Rich Menu...")
    payload = {
        "size": {"width": 2500, "height": 1686},
        "selected": True,
        "name": "Sathien_Luxury_Cream_Gold_2026",
        "chatBarText": "เมนูหลัก 👓",
        "areas": [
            # Tile 1: โปรโมชั่นพิเศษ (Top-Left)
            {
                "bounds": {"x": 0, "y": 0, "width": 833, "height": 843},
                "action": {"type": "message", "text": "โปรโมชั่น"}
            },
            # Tile 2: พิกัดบูทสัญจร (Top-Middle)
            {
                "bounds": {"x": 833, "y": 0, "width": 834, "height": 843},
                "action": {"type": "message", "text": "พิกัดบูทสัปดาห์นี้"}
            },
            # Tile 3: แผนที่ร้านที่บ้าน / ร้านเสถียร (Top-Right) -> Opens Home Google Maps Directly!
            {
                "bounds": {"x": 1667, "y": 0, "width": 833, "height": 843},
                "action": {
                    "type": "uri",
                    "label": "Google Maps",
                    "uri": "https://maps.app.goo.gl/4PYEPsbsrqpmZeXy6?g_st=al"
                }
            },
            # Tile 4: บริการหลังการขาย (Bottom-Left)
            {
                "bounds": {"x": 0, "y": 843, "width": 833, "height": 843},
                "action": {"type": "message", "text": "บริการหลังการขาย"}
            },
            # Tile 5: เช็กสถานะแว่นตา & ที่อยู่จัดส่ง (Bottom-Middle)
            {
                "bounds": {"x": 833, "y": 843, "width": 834, "height": 843},
                "action": {"type": "message", "text": "ติดตามแว่น / พัสดุ"}
            },
            # Tile 6: โทรติดต่อร้าน (Bottom-Right)
            {
                "bounds": {"x": 1667, "y": 843, "width": 833, "height": 843},
                "action": {"type": "message", "text": "โทรติดต่อร้าน"}
            }
        ]
    }

    create_res = requests.post("https://api.line.me/v2/bot/richmenu", headers=headers_json, json=payload)
    if create_res.status_code != 200:
        print(f"Failed to create rich menu: {create_res.status_code} {create_res.text}")
        return

    rich_menu_id = create_res.json()["richMenuId"]
    print(f"Created Rich Menu ID: {rich_menu_id}")

    print("3. Uploading Bubble Bloom rich menu image...")
    headers_image = {
        "Authorization": f"Bearer {TOKEN}",
        "Content-Type": "image/jpeg"
    }
    with open(IMAGE_PATH, "rb") as f:
        upload_res = requests.post(
            f"https://api-data.line.me/v2/bot/richmenu/{rich_menu_id}/content",
            headers=headers_image,
            data=f
        )
    if upload_res.status_code != 200:
        print(f"Failed to upload image: {upload_res.status_code} {upload_res.text}")
        return
    print("Image uploaded successfully!")

    print("4. Setting as default Rich Menu for all users...")
    set_default_res = requests.post(
        f"https://api.line.me/v2/bot/user/all/richmenu/{rich_menu_id}",
        headers=headers_json
    )
    if set_default_res.status_code != 200:
        print(f"Failed to set default: {set_default_res.status_code} {set_default_res.text}")
        return

    print("SUCCESS! Bubble Bloom Rich Menu is now live as default for all users!")

if __name__ == "__main__":
    setup_rich_menu()
