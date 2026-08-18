import os
import time
import json
import threading
import requests
from bs4 import BeautifulSoup
from flask import Flask

app = Flask(__name__)

SEEN_PROJECTS_FILE = "/tmp/seen_projects.json"  # مجلد مؤقت في سيرفر Render
NTFY_TOPIC = "freelancealert"  # اسم قناتك على تطبيق ntfy

def load_seen_projects():import os
import time
import json
import requests
from bs4 import BeautifulSoup

SEEN_PROJECTS_FILE = "seen_projects.json"
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "freelancealert")  # سيقرأ اسم قناتك بأمان

def load_seen_projects():
    if os.path.exists(SEEN_PROJECTS_FILE):
        try:
            with open(SEEN_PROJECTS_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_seen_projects(seen_projects):
    try:
        with open(SEEN_PROJECTS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(seen_projects), f)
    except Exception:
        pass

def send_ntfy_notification(title, message, url):
    try:
        headers = {
            "Title": title.encode('utf-8'),
            "Click": url,
            "Tags": "moneybag,loudspeaker"
        }
        response = requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                                 data=message.encode('utf-8'), 
                                 headers=headers)
        if response.status_code == 200:
            print("تم إرسال الإشعار لهاتفك بنجاح!")
    except Exception as e:
        print("خطأ في إرسال الإشعار:", e)

def fetch_mostaql_projects():
    projects = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get("https://mostaql.com/projects", headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if 'mostaql.com/project/' in href and not href.endswith('/bids'):
                    title = link.text.strip()
                    if title and len(title) > 5:
                        project_id = href.split('/')[-1].split('-')[0]
                        projects.append({
                            'id': f"mostaql_{project_id}",
                            'title': title,
                            'url': href,
                            'platform': 'مستقل'
                        })
    except Exception as e:
        print("خطأ مستقل:", e)
    return projects

def fetch_nafezly_projects():
    projects = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get("https://nafezly.com/projects", headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if 'nafezly.com/u/' in href and '/project/' in href:
                    title = link.text.strip()
                    if title and len(title) > 5:
                        project_id = href.split('/')[-1]
                        projects.append({
                            'id': f"nafezly_{project_id}",
                            'title': title,
                            'url': href,
                            'platform': 'نفذلي'
                        })
    except Exception as e:
        print("خطأ نفذلي:", e)
    return projects

def main():
    seen_projects = load_seen_projects()
    is_first_run = len(seen_projects) == 0
    
    print("جاري فحص المشاريع...")
    mostaql_projects = fetch_mostaql_projects()
    nafezly_projects = fetch_nafezly_projects()
    all_projects = mostaql_projects + nafezly_projects
    
    new_projects_found = False
    for p in all_projects:
        if p['id'] not in seen_projects:
            new_projects_found = True
            seen_projects.add(p['id'])
            
            if not is_first_run:
                send_ntfy_notification(f"مشروع جديد على {p['platform']}", p['title'], p['url'])
                
    if new_projects_found:
        save_seen_projects(seen_projects)
        print("تم حفظ المشاريع الجديدة.")
    else:
        print("لا توجد مشاريع جديدة.")

if __name__ == "__main__":
    main()
    if os.path.exists(SEEN_PROJECTS_FILE):
        try:
            with open(SEEN_PROJECTS_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
        except Exception:
            return set()
    return set()

def save_seen_projects(seen_projects):
    try:
        with open(SEEN_PROJECTS_FILE, "w", encoding="utf-8") as f:
            json.dump(list(seen_projects), f)
    except Exception:
        pass

def send_ntfy_notification(title, message, url):
    try:
        headers = {
            "Title": title.encode('utf-8'),
            "Click": url,
            "Tags": "moneybag,loudspeaker"
        }
        response = requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", 
                                 data=message.encode('utf-8'), 
                                 headers=headers)
        if response.status_code == 200:
            print("تم إرسال الإشعار لهاتفك بنجاح!")
    except Exception as e:
        print("خطأ في إرسال الإشعار:", e)

def fetch_mostaql_projects():
    projects = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get("https://mostaql.com/projects", headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if 'mostaql.com/project/' in href and not href.endswith('/bids'):
                    title = link.text.strip()
                    if title and len(title) > 5:
                        project_id = href.split('/')[-1].split('-')[0]
                        projects.append({
                            'id': f"mostaql_{project_id}",
                            'title': title,
                            'url': href,
                            'platform': 'مستقل'
                        })
    except Exception as e:
        print("خطأ مستقل:", e)
    return projects

def fetch_nafezly_projects():
    projects = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        response = requests.get("https://nafezly.com/projects", headers=headers, timeout=15)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            links = soup.find_all('a', href=True)
            for link in links:
                href = link['href']
                if 'nafezly.com/u/' in href and '/project/' in href:
                    title = link.text.strip()
                    if title and len(title) > 5:
                        project_id = href.split('/')[-1]
                        projects.append({
                            'id': f"nafezly_{project_id}",
                            'title': title,
                            'url': href,
                            'platform': 'نفذلي'
                        })
    except Exception as e:
        print("خطأ نفذلي:", e)
    return projects

def bot_loop():
    seen_projects = load_seen_projects()
    is_first_run = len(seen_projects) == 0
    
    print("البوت يعمل الآن ويراقب المشاريع...")
    send_ntfy_notification("البوت يعمل بنجاح! 🚀", "بدأت المراقبة على خادم Render مجاناً.", "https://mostaql.com/projects")
    
    while True:
        print("جاري فحص المشاريع...")
        mostaql_projects = fetch_mostaql_projects()
        nafezly_projects = fetch_nafezly_projects()
        all_projects = mostaql_projects + nafezly_projects
        
        new_projects_found = False
        for p in all_projects:
            if p['id'] not in seen_projects:
                new_projects_found = True
                seen_projects.add(p['id'])
                
                if not is_first_run:
                    send_ntfy_notification(f"مشروع جديد على {p['platform']}", p['title'], p['url'])
                
        if new_projects_found:
            save_seen_projects(seen_projects)
            
        is_first_run = False 
        time.sleep(120)

# تشغيل البوت في الخلفية
threading.Thread(target=bot_loop, daemon=True).start()

@app.route('/')
def home():
    return "Bot is running perfectly!"

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
