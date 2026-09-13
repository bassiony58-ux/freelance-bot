import os
import json
import requests
from bs4 import BeautifulSoup

SEEN_FILE = "seen_projects.json"
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "freelancealert")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Accept-Language": "ar,en-US;q=0.9,en;q=0.8",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
}

def load_seen():
    try:
        if os.path.exists(SEEN_FILE):
            with open(SEEN_FILE, "r", encoding="utf-8") as f:
                return set(json.load(f))
    except Exception as e:
        print("خطأ قراءة الملف:", e)
    return set()

def save_seen(seen):
    try:
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(list(seen), f, ensure_ascii=False)
    except Exception as e:
        print("خطأ حفظ الملف:", e)

def send_notification(title, message, url):
    try:
        headers = {
            "Title": title.encode('utf-8'),
            "Click": url,
            "Tags": "moneybag,loudspeaker"
        }
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=message.encode('utf-8'), headers=headers, timeout=10)
        print("تم إرسال الإشعار!")
    except Exception as e:
        print("خطأ إرسال الإشعار:", e)

def fetch_mostaql():
    projects = []
    try:
        res = requests.get("https://mostaql.com/projects", headers=HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'mostaql.com/project/' in href and not href.endswith('/bids'):
                    title = link.text.strip()
                    if title and len(title) > 5:
                        p_id = href.split('/')[-1].split('-')[0]
                        projects.append({'id': f"mostaql_{p_id}", 'title': title, 'url': href, 'platform': 'مستقل'})
        else:
            print(f"مستقل أعاد كود استجابة: {res.status_code}")
    except Exception as e:
        print("خطأ فحص مستقل:", e)
    return projects

def fetch_nafezly():
    projects = []
    try:
        res = requests.get("https://nafezly.com/projects", headers=HEADERS, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'nafezly.com/u/' in href and '/project/' in href:
                    title = link.text.strip()
                    if title and len(title) > 5:
                        p_id = href.split('/')[-1]
                        projects.append({'id': f"nafezly_{p_id}", 'title': title, 'url': href, 'platform': 'نفذلي'})
        else:
            print(f"نفذلي أعاد كود استجابة: {res.status_code}")
    except Exception as e:
        print("خطأ فحص نفذلي:", e)
    return projects

def main():
    seen = load_seen()
    is_first = len(seen) == 0
    
    print("جاري فحص المشاريع...")
    all_p = fetch_mostaql() + fetch_nafezly()
    print(f"تم العثور على {len(all_p)} مشروع.")
    
    new_found = False
    for p in all_p:
        if p['id'] not in seen:
            new_found = True
            seen.add(p['id'])
            if not is_first:
                send_notification(f"مشروع جديد على {p['platform']}", p['title'], p['url'])
                
    if new_found:
        save_seen(seen)
        print("تم تحديث المشاريع المحفوظة.")
    else:
        print("لا توجد مشاريع جديدة.")

if __name__ == "__main__":
    main()
