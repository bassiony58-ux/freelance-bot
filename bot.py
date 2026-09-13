import os
import json
import requests
from bs4 import BeautifulSoup

SEEN_FILE = "seen_projects.json"
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "freelancealert")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "ar,en-US;q=0.9,en;q=0.8"
}

# الكلمات المفتاحية لقسم البرمجة والذكاء الاصطناعي
TARGET_KEYWORDS = [
    'برمج', 'موقع', 'تطبيق', 'تطوير', 'ويب', 'بايثون', 'php', 
    'كود', 'ai', 'ذكاء', 'اصطناعي', 'شات', 'بوت', 'api', 
    'داتا', 'خوارزم', 'متجر', 'ووردبريس', 'سكربت', 'نظام', 'سيستم'
]

def load_seen():
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    return set()

def save_seen(seen):
    with open(SEEN_FILE, "w", encoding="utf-8") as f:
        json.dump(list(seen), f, ensure_ascii=False)

def send_notification(title, message, url):
    try:
        headers = {
            "Title": title.encode('utf-8'),
            "Click": url,
            "Tags": "computer,robot"
        }
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=message.encode('utf-8'), headers=headers, timeout=10)
    except Exception as e:
        print("Error sending:", e)

def is_target_project(title):
    title_lower = title.lower()
    for kw in TARGET_KEYWORDS:
        if kw in title_lower:
            return True
    return False

def fetch_mostaql():
    projects = []
    try:
        res = requests.get("https://mostaql.com/projects", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'mostaql.com/project/' in href and not href.endswith('/bids'):
                title = link.text.strip()
                if title and len(title) > 5:
                    p_id = href.split('/')[-1].split('-')[0]
                    projects.append({'id': f"mostaql_{p_id}", 'title': title, 'url': href, 'platform': 'مستقل'})
    except Exception as e:
        pass
    return projects

def fetch_nafezly():
    projects = []
    try:
        res = requests.get("https://nafezly.com/projects", headers=HEADERS, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            href = link['href']
            # تم حل مشكلة نفذلي وتحديث الرابط
            if '/project/' in href and 'nafezly.com' in href:
                title = link.text.strip()
                if title and len(title) > 5:
                    p_id = href.split('/')[-1]
                    if '-' in p_id and p_id.split('-')[0].isdigit():
                        projects.append({'id': f"nafezly_{p_id.split('-')[0]}", 'title': title, 'url': href, 'platform': 'نفذلي'})
    except Exception as e:
        pass
    return projects

def main():
    seen = load_seen()
    is_first = len(seen) == 0
    all_p = fetch_mostaql() + fetch_nafezly()
    
    new_found = False
    for p in all_p:
        if p['id'] not in seen:
            new_found = True
            seen.add(p['id'])
            
            # إذا كان المشروع يحتوي على كلمات برمجة/ذكاء اصطناعي سيتم إرساله
            if not is_first and is_target_project(p['title']):
                send_notification(f"💻 مشروع برمجة جديد ({p['platform']})", p['title'], p['url'])
                
    if new_found:
        save_seen(seen)

if __name__ == "__main__":
    main()
