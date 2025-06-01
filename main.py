# main.py - v5.1 (Final Formatting Fix)
from flask import Flask
import threading
import time
from time import sleep
import requests
from bs4 import BeautifulSoup
from requests import get as telegram_get
import os
import json

# --- CONFIGURATION (Part 1: Get from Replit Secrets) ---
BOT_TOKEN = os.environ.get('BOT_TOKEN')
GROUPS_IDS_STR = os.environ.get('GROUPS_IDS')
PROXY_IP = os.environ.get('PROXY_IP')
PROXY_PORT = os.environ.get('PROXY_PORT')

if GROUPS_IDS_STR:
    GROUPS_IDS = tuple(item.strip() for item in GROUPS_IDS_STR.split(','))
else:
    GROUPS_IDS = ()

# --- CONFIGURATION (Part 2: Load from config.json file) ---
try:
    with open('config.json', 'r') as f:
        config = json.load(f)
    UNIVERSITY_ANNOUNCEMENT_URL = config['university_url']
    LOOP_TIME = config['loop_time_seconds']
    BOT_OWNER_ID = str(config['bot_owner_id'])
    print("Configuration from config.json loaded successfully.")
except Exception as e:
    print(f"WARNING: Could not load config.json. Using fallback defaults. Error: {e}")
    UNIVERSITY_ANNOUNCEMENT_URL = "https://fmi.univ-tiaret.dz/index.php"
    LOOP_TIME = 900
    BOT_OWNER_ID = None

# --- CONFIGURATION (Part 3: Script Defaults) ---
WEB_HEADERS = { 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36' }
REQUEST_TIMEOUT = 20
FILENAME_SEEN_IDS = "seen_announcements.json"
KEYWORD_HASHTAGS = {
    "#Exams": ["examen", "examens", "planning", "rattrapage"],
    "#Results": ["resultat", "résultats", "notes", "affichage"],
    "#Masters": ["master", "masters"],
    "#Doctorate": ["doctorat", "phd"],
    "#Important": ["important", "urgent", "reporté", "تنبيه", "هام"]
}

# --- Flask Web App Part ---
app = Flask(__name__)
@app.route('/')
def home():
    return "Announcement Bot is alive and checking!"
def run_flask_app():
    app.run(host='0.0.0.0', port=8080)

# --- HELPER FUNCTION for HTML ---
def escape_html(text):
    text = str(text)
    text = text.replace('&', '&amp;')
    text = text.replace('<', '&lt;')
    text = text.replace('>', '&gt;')
    return text

# --- Bot's Core Logic ---
def send_telegram_message(text):
    """Sends a message with HTML enabled, using a robust method."""
    if not BOT_TOKEN or not GROUPS_IDS:
        print("Error: BOT_TOKEN or GROUPS_IDS not set.")
        return

    base_url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    for group_id in GROUPS_IDS:
        # Let the requests library handle URL encoding by passing parameters
        params = {
            'chat_id': group_id,
            'text': text,
            'disable_notification': False,
            'parse_mode': 'HTML'
        }
        try:
            response = telegram_get(base_url, params=params, timeout=REQUEST_TIMEOUT)
            if response.status_code != 200:
                print(f"Telegram error for group {group_id}: {response.text}")
        except Exception as E:
            print(f"An error occurred in send_telegram_message: {E}")
        sleep(1)

def load_seen_ids():
    try:
        with open(FILENAME_SEEN_IDS, 'r', encoding='utf-8') as f:
            return set(json.load(f))
    except (FileNotFoundError, json.JSONDecodeError):
        return set()

def save_seen_ids(ids_set):
    with open(FILENAME_SEEN_IDS, 'w', encoding='utf-8') as f:
        json.dump(list(ids_set), f)

def scrape_all_announcements():
    try:
        print(f"Fetching page: {UNIVERSITY_ANNOUNCEMENT_URL}...")
        proxies = None
        if PROXY_IP and PROXY_PORT:
            proxies = {"http": f"http://{PROXY_IP}:{PROXY_PORT}", "https": f"http://{PROXY_IP}:{PROXY_PORT}"}
        response = requests.get(UNIVERSITY_ANNOUNCEMENT_URL, headers=WEB_HEADERS, timeout=REQUEST_TIMEOUT, proxies=proxies)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        found_announcements = []
        all_rows = soup.find_all('tr')
        for row in all_rows:
            cells = row.find_all('td')
            if len(cells) == 2 and cells[0].get('style') == "border: 1px solid #ababab; text-align: center;":
                title_tag = cells[0].find('strong')
                title = title_tag.get_text(strip=True) if title_tag else None
                date_parts = [text.strip() for text in cells[1].find_all(string=True) if text.strip()]
                date_str = date_parts[-1] if date_parts else None
                if title and date_str:
                    content_preview = "\n".join([p.get_text(separator=' ', strip=True) for p in cells[0].find_all('p')])
                    unique_id = f"{title}_{date_str}"
                    found_announcements.append({"id": unique_id, "title": title, "date": date_str, "content_preview": content_preview})
        return found_announcements
    except Exception as e:
        print(f"An error occurred during scraping: {e}")
        return []

# --- MAIN BOT LOGIC ---
def announcement_monitor_task():
    send_telegram_message("📢 <b>Bot v5.1 is starting up...</b>")

    seen_ids = load_seen_ids()
    is_first_run = not seen_ids
    print(f"Loaded {len(seen_ids)} previously seen IDs. Is this a first run? {is_first_run}")

    while True:
        print(f"\n--- Checking for new announcements ({time.strftime('%Y-%m-%d %H:%M:%S')}) ---")
        all_announcements = scrape_all_announcements()
        if not all_announcements:
            sleep(LOOP_TIME)
            continue

        if is_first_run:
            print("First run logic is executing.")
            latest_announcement = all_announcements[0]

            safe_title = escape_html(latest_announcement['title'])
            safe_date = escape_html(latest_announcement['date'])
            hashtags = {escape_html(tag) for tag, keywords in KEYWORD_HASHTAGS.items() for keyword in keywords if keyword in latest_announcement['title'].lower()}

            message = f"📢 <b>Latest Announcement (on Bot Start)</b> 📢\n\n"
            if hashtags: message += f"{' '.join(hashtags)}\n\n"
            message += f"📌 <b>Title:</b> {safe_title}\n"
            message += f"🗓️ <b>Date:</b> {safe_date}\n\n📝 <b>Details:</b>\n"

            preview_lines = latest_announcement['content_preview'].split('\n')
            num_lines_to_send = 0
            for line in preview_lines:
                clean_line = line.strip()
                if clean_line and clean_line.lower() != latest_announcement['title'].lower():
                    message += f"{escape_html(clean_line)}\n"
                    num_lines_to_send += 1
                if num_lines_to_send >= 4: break
            if num_lines_to_send == 0: message += "<i>(Full content on the website)</i>"
            message += f'\n\n<a href="{UNIVERSITY_ANNOUNCEMENT_URL}">Visit the Announcements Page</a>'

            send_telegram_message(message)

            for ann in all_announcements:
                seen_ids.add(ann['id'])
            save_seen_ids(seen_ids)
            is_first_run = False
        else:
            new_announcements_to_send = [ann for ann in all_announcements if ann['id'] not in seen_ids]

            if new_announcements_to_send:
                new_announcements_to_send.reverse()
                for ann in new_announcements_to_send:
                    safe_title = escape_html(ann['title'])
                    safe_date = escape_html(ann['date'])
                    hashtags = {escape_html(tag) for tag, keywords in KEYWORD_HASHTAGS.items() for keyword in keywords if keyword in ann['title'].lower()}

                    message = f"📢 <b>New University Announcement!</b> 📢\n\n"
                    if hashtags: message += f"{' '.join(hashtags)}\n\n"
                    message += f"📌 <b>Title:</b> {safe_title}\n"
                    message += f"🗓️ <b>Date:</b> {safe_date}\n\n📝 <b>Details:</b>\n"

                    preview_lines = ann['content_preview'].split('\n')
                    num_lines_to_send = 0
                    for line in preview_lines:
                        clean_line = line.strip()
                        if clean_line and clean_line.lower() != ann['title'].lower():
                            message += f"{escape_html(clean_line)}\n"
                            num_lines_to_send += 1
                        if num_lines_to_send >= 4: break
                    if len(preview_lines) > num_lines_to_send and num_lines_to_send > 0: message += "…\n"
                    if num_lines_to_send == 0: message += "<i>(Full content on the website)</i>"
                    message += f'\n\n<a href="{UNIVERSITY_ANNOUNCEMENT_URL}">Visit the Announcements Page</a>'

                    send_telegram_message(message)
                    seen_ids.add(ann['id'])
                save_seen_ids(seen_ids)
            else:
                print("No new announcements since last check.")

        print(f"Waiting for {LOOP_TIME} seconds before the next check...")
        sleep(LOOP_TIME)

# --- Main Execution ---
if __name__ == '__main__':
    flask_thread = threading.Thread(target=run_flask_app)
    flask_thread.daemon = True
    flask_thread.start()

    try:
        announcement_monitor_task()
    except Exception as e:
        print(f"FATAL ERROR in main task: {e}")
        if BOT_OWNER_ID:
            error_message = f"🚨 <b>BOT CRASHED!</b> 🚨\n\nFatal error in the main task:\n<code>{escape_html(str(e))}</code>"
            # Use the robust send_telegram_message function to send the error
            send_telegram_message(error_message)