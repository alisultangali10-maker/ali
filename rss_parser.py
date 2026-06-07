import feedparser
from datetime import datetime, timezone
import requests
from bs4 import BeautifulSoup
import os
import uuid
import re
from app.models import News, Category
from app import create_app, db

RSS_FEEDS = {
    'Tengrinews.kz': 'https://tengrinews.kz/news.rss',
    'Nur.kz': 'https://www.nur.kz/rss/',
    'Zakon.kz': 'https://www.zakon.kz/rss/',
    'Inform.kz': 'https://www.inform.kz/inform.rss',
    'Kapital.kz': 'https://kapital.kz/rss/all/index.xml',
    'Kazpravda.kz': 'https://kazpravda.kz/rss',
    # International / Extra
    'BBC World': 'http://feeds.bbci.co.uk/news/world/rss.xml',
    'The Verge (Tech)': 'https://www.theverge.com/rss/index.xml',
    'Motor1 (Auto)': 'https://www.motor1.com/rss/articles/all/'
}

CATEGORY_KEYWORDS = {
    'cat_politics': ['парламент', 'депутат', 'президент', 'токаев', 'правительство', 'министр', 'акимат', 'закон', 'политика', 'выборы', 'референдум', 'white house', 'biden', 'trump', 'senate'],
    'cat_sport': ['спорт', 'матч', 'футбол', 'хоккей', 'бокс', 'олимпиада', 'чемпионат', 'гол', 'кубок', 'турнир', 'головкин', 'теннис', 'fifa', 'nba', 'uefa'],
    'cat_economy': ['тенге', 'финансы', 'банки', 'нефть', 'экономика', 'бизнес', 'налоги', 'курс', 'инвестиции', 'ввп', 'акции', 'криптовалюта', 'bitcoin', 'fed', 'stock market'],
    'cat_tech': ['it', 'технологии', 'смартфон', 'интернет', 'apple', 'google', 'разработка', 'связь', 'цифровизация', 'искусственный интеллект', 'ai', 'samsung', 'microsoft', 'software'],
    'cat_auto': ['авто', 'машина', 'двигатель', 'тесла', 'bmw', 'mercedes', 'toyota', 'электромобиль', 'гибрид', 'car', 'vehicle', 'automotive', 'tesla', 'ford'],
    'cat_world': ['мир', 'оон', 'сша', 'европа', 'китай', 'россия', 'израиль', 'украина', 'геополитика', 'world', 'international', 'global'],
    'cat_culture': ['культура', 'кино', 'музыка', 'фестиваль', 'театр', 'выставка', 'искусство', 'звезды', 'шоу-бизнес', 'culture', 'entertainment', 'music', 'cinema'],
    'cat_general': ['news', 'update', 'новости']
}

def determine_category(title, content, source_name):
    """Categorize news based on text and source."""
    # Priority sources
    if 'Verge' in source_name: return 'cat_tech'
    if 'Motor1' in source_name: return 'cat_auto'
    if 'Sport' in source_name: return 'cat_sport'
    
    text = (title + " " + content).lower()
    for cat_code, keywords in CATEGORY_KEYWORDS.items():
        if any(word in text for word in keywords):
            return cat_code
    return 'cat_general'

def get_image_from_rss_entry(entry):
    if 'links' in entry:
        for link in entry.links:
            if 'image' in link.get('type', ''): return link.get('href')
    if 'media_content' in entry:
        for media in entry.media_content:
            if 'url' in media: return media['url']
    summary = entry.get('summary', '')
    if '<img' in summary:
        match = re.search(r'src="([^"]+)"', summary)
        if match: return match.group(1)
    return None

def download_image(image_url, upload_folder):
    try:
        if not image_url:
            return None

        if image_url.startswith('//'):
            image_url = 'https:' + image_url

        headers = {
            'User-Agent': 'Mozilla/5.0'
        }

        session = requests.Session()
        session.trust_env = False

        # 🔥 RETRY (ВАЖНО)
        response = None

        
        for i in range(3):
            try:
                response = session.get(
                    image_url,
                    headers=headers,
                    timeout=20,
                    verify=False,
                    allow_redirects=True
                )

                print("DOWNLOADING:", image_url)
                print("STATUS =", response.status_code)
                print("CONTENT-TYPE =", response.headers.get("content-type"))

                content_type = response.headers.get('content-type', '').lower()

                # ❌ неудачные ответы
                if response.status_code != 200:
                    continue

                content_type = (response.headers.get('content-type') or '').lower()

                if 'text/html' in content_type:
                    continue

                if 'image' not in content_type:
                    continue

                if len(response.content) < 5000:
                    continue

                # ✅ всё ок — выходим
                break

            except Exception as e:
                print(f"[RETRY {i+1}] {e}")
                response = None

        # если ничего не скачалось
        if not response:
            return None

        content_type = response.headers.get('content-type', '').lower()

        if not content_type.startswith('image'):
            return None

        if 'png' in content_type:
            ext = 'png'
        elif 'webp' in content_type:
            ext = 'webp'
        elif 'jpeg' in content_type or 'jpg' in content_type:
            ext = 'jpg'
        else:
            ext = 'jpg'

        filename = f"news_{uuid.uuid4().hex[:12]}.{ext}"
        filepath = os.path.join(upload_folder, filename)

        from PIL import Image
        import io

        try:
            img = Image.open(io.BytesIO(response.content))
            img.verify()
        except Exception:
            return None

        with open(filepath, 'wb') as f:
            f.write(response.content)

        print("SAVED:", filename)
        return filename


    except Exception as e:
        print("IMAGE ERROR:", e)
        return None

def extract_full_content(url, source_name):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0"
        }

        response = requests.get(url, headers=headers, timeout=15)
        response.encoding = "utf-8"

        soup = BeautifulSoup(response.text, "html.parser")

        content = ""

        # ---------------- IMAGE EXTRACTION ----------------
        image_candidates = []

        meta = soup.find("meta", property="og:image")
        if meta:
            image_candidates.append(meta.get("content"))

        meta = soup.find("meta", attrs={"name": "twitter:image"})
        if meta:
            image_candidates.append(meta.get("content"))

        meta = soup.find("meta", property="og:image:url")
        if meta:
            image_candidates.append(meta.get("content"))

        image_candidates = [
            img for img in image_candidates
            if img and img.startswith("http")
        ]

        image_url = image_candidates[0] if image_candidates else None
        # --------------------------------------------------

        content_selectors = [
            ".content_main_text",
            ".tn-news-content",
            ".article-body",
            ".article-content",
            ".full-text",
            ".content",
            ".article__text",
            ".item-text",
            ".post-content",
            ".c-entry-content",
            "article"
        ]

        content_div = None

        for selector in content_selectors:
            content_div = soup.select_one(selector)
            if content_div:
                break

        if content_div:

            for tag in content_div(["script", "style", "iframe", "aside", "nav"]):
                tag.decompose()

            content = content_div.get_text(separator="\n", strip=True)

        print("FINAL IMAGE URL =", image_url)
        
        return content, image_url
    

    except Exception as e:
        print("[SCRAPER ERROR]", e)
        return "", None


def fetch_rss_feeds():
    print(f"== [{datetime.now()}] GLOBAL NEWS UPDATE ==")
    app = create_app()
    with app.app_context():
        processed = 0
        total_added = 0
        # RUN init_db logic manually if needed (adding new categories if missing
        # However, we assume user runs init_db.py or we do it here
        for c_code in CATEGORY_KEYWORDS.keys():
            if not Category.query.filter_by(code=c_code).first():
                db.session.add(Category(code=c_code))
        db.session.commit()
        
        cats = {c.code: c.id for c in Category.query.all()}
        upload_folder = app.config['UPLOAD_FOLDER']
        print("UPLOAD_FOLDER =", upload_folder)
        
        for source_name, url in RSS_FEEDS.items():
            print(f"> SOURCE: {source_name}")
            try:
                feed = feedparser.parse(url)

                print("STATUS:", getattr(feed, "status", "NONE"))
                print("BOZO:", feed.bozo)

                if feed.bozo:
                    print("ERROR:", feed.bozo_exception)

                for entry in feed.entries:

                    if processed >= 5:
                        break

                    link = entry.get('link')
                    if not link:
                        continue 

                    if News.query.filter_by(original_url=link).first():
                        print("SKIP EXISTS")
                        continue
                    
                    print(f"  * Fetching: {entry.get('title', '')[:40]}...")
                    full_text, web_image = extract_full_content(link, source_name)
                    rss_image = get_image_from_rss_entry(entry)
                    
                    image_url = None

                    candidates = [
                        web_image,
                        rss_image,
                    ]

                    media = entry.get('media_thumbnail')
                    if isinstance(media, list) and media:
                        candidates.append(media[0].get('url'))

                    for url in candidates:
                        if url and isinstance(url, str) and url.startswith("http"):
                            image_url = url
                            break

                    print("RSS IMAGE:", rss_image)
                    print("IMAGE FROM SCRAPER:", web_image)
                    print("WEB IMAGE =", web_image)
                    print("RSS IMAGE =", rss_image)
                    
                    if not full_text:
                        full_text = entry.get('summary', '') or entry.get('description', '')
                        full_text = BeautifulSoup(full_text, "html.parser").text

    


                    print("FINAL IMAGE URL =", image_url)
                    print("IMAGE:", image_url)

                    if not image_url:
                        local_img = None
                    else:
                        local_img = download_image(image_url, upload_folder)
                        
                    print("DOWNLOAD RESULT =", local_img)
                        
                    print("LOCAL IMG =", local_img)
                
                    
                    # Determine source language
                    src_lang = 'ru'
                    if any(x in source_name for x in ['BBC', 'Verge', 'Motor1']):
                        src_lang = 'en'
                    
                    cat_code = determine_category(entry.get('title', ''), full_text, source_name)
                    cat_id = cats.get(cat_code)

                    if not cat_id:
                        cat_id = cats.get('cat_general')
                    
                    title = entry.get('title', '')

                    news_item = News(
                        category_id=cat_id,
                        title_ru=title,
                        title_kk=title,
                        title_en=title,
                        content_ru=full_text,
                        content_kk=full_text,
                        content_en=full_text,
                        summary_ru=full_text[:300],
                        summary_kk=full_text[:300],
                        summary_en=full_text[:300],
                        source_name=source_name,
                        original_url=link,
                        image_filename=local_img,
                        created_at=datetime.now(timezone.utc)
                    )
                    db.session.add(news_item)
                    total_added += 1
                    processed += 1
                db.session.commit()
            except Exception as e:
                print(f"  ! Error {source_name}: {e}")
                db.session.rollback()
        print(f"== FINISHED. ADDED: {total_added} ==")

if __name__ == "__main__":
    fetch_rss_feeds()
