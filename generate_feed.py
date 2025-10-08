from playwright.sync_api import sync_playwright
from datetime import datetime
import html

CATEGORY_URL = "https://www.a-zmanga.net/archives/category/%e4%b8%80%e8%88%ac%e6%bc%ab%e7%94%bb"
OUTPUT_FILE = "feed.xml"

def fetch_posts():
    items = []
    with sync_playwright() as p:
        # Launch headless browser
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        # Set realistic User-Agent to reduce blocking
        page.set_extra_http_headers({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        })
        
        # Increase timeout to 60 seconds
        page.goto(CATEGORY_URL, timeout=60000)
        page.wait_for_selector("article")  # Wait for manga posts to load
        
        posts = page.query_selector_all("article")
        for post in posts:
            a_tag = post.query_selector("h2 a, h3 a")
            if not a_tag:
                continue
            title = html.escape(a_tag.inner_text().strip())
            link = a_tag.get_attribute("href")
            
            time_tag = post.query_selector("time")
            pub_date = time_tag.get_attribute("datetime") if time_tag else datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")
            
            items.append({"title": title, "link": link, "pub_date": pub_date})
        
        browser.close()
    return items

def build_rss(items):
    rss_items = ""
    for it in items:
        rss_items += f"""
    <item>
      <title>{it['title']}</title>
      <link>{it['link']}</link>
      <guid isPermaLink="true">{it['link']}</guid>
      <pubDate>{it['pub_date']}</pubDate>
    </item>"""
    
    rss = f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
<channel>
  <title>A-Z Manga Feed</title>
  <link>{CATEGORY_URL}</link>
  <description>Latest updates from 一般漫画</description>
  <lastBuildDate>{datetime.utcnow().strftime("%a, %d %b %Y %H:%M:%S +0000")}</lastBuildDate>
  {rss_items}
</channel>
</rss>"""
    return rss

if __name__ == "__main__":
    posts = fetch_posts()
    rss_xml = build_rss(posts)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write(rss_xml)
    print(f"✅ Generated {OUTPUT_FILE} with {len(posts)} items")
