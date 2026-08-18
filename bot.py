import os
import json
import requests
from bs4 import BeautifulSoup

SEEN_FILE = "seen_projects.json"
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "freelancealert")

def load_seen():
    try:
        with open(SEEN_FILE, "r", encoding="utf-8") as f:
            return set(json.load(f))
    except:
        return set()

def save_seen(seen):
    try:
        with open(SEEN_FILE, "w", encoding="utf-8") as f:
            json.dump(list(seen), f)
    except:
        pass

def send_notification(title, message, url):
    try:
        headers = {
            "Title": title.encode('utf-8'),
            "Click": url,
            "Tags": "moneybag,loudspeaker"
        }
        requests.post(f"https://ntfy.sh/{NTFY_TOPIC}", data=message.encode('utf-8'), headers=headers)
        print("تم إرسال الإشعار!")
    except Exception as e:
        print("خطأ إشعار:", e)

def fetch_mostaql():
    projects = []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get("https://mostaql.com/projects", headers=headers, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'mostaql.com/project/' in href and not href.endswith('/bids'):
                    title = link.text.strip()
                    if title and len(title) > 5:
                        p_id = href.split('/')[-1].split('-')[0]
                        projects.append({'id': f"mostaql_{p_id}", 'title': title, 'url': href, 'platform': 'مستقل'})
    except Exception as e:
        print("خطأ مستقل:", e)
    return projects

def fetch_nafezly():
    projects = []
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        res = requests.get("https://nafezly.com/projects", headers=headers, timeout=15)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, 'html.parser')
            for link in soup.find_all('a', href=True):
                href = link['href']
                if 'nafezly.com/u/' in href and '/project/' in href:
                    title = link.text.strip()
                    if title and len(title) > 5:
                        p_id = href.split('/')[-1]
                        projects.append({'id': f"nafezly_{p_id}", 'title': title, 'url': href, 'platform': 'نفذلي'})
    except Exception as e:
        print("خطأ نفذلي:", e)
    return projects

def main():
    seen = load_seen()
    is_first = len(seen) == 0
    
    print("جاري الفحص...")
    all_p = fetch_mostaql() + fetch_nafezly()
    new_found = False
    
    for p in all_p:
        if p['id'] not in seen:
            new_found = True
            seen.add(p['id'])
            if not is_first:
                send_notification(f"مشروع جديد على {p['platform']}", p['title'], p['url'])
                
    if new_found:
        save_seen(seen)
        print("تم الحفظ.")
    else:
        print("لا جديد.")

if __name__ == "__main__":
    main()
