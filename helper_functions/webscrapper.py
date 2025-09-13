import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urldefrag
import json
import re
import os
from concurrent.futures import ThreadPoolExecutor, as_completed

def fetch_html_content(base_url):
    visited = set()
    to_visit = [base_url]
    results = []
    domain = re.sub(r'https?://', '', base_url).strip('/').replace('/', '_')

    while to_visit:
        current_url = to_visit.pop(0)
        if current_url in visited:
            continue
        visited.add(current_url)

        try:
            response = requests.get(current_url, timeout=10)
            if response.status_code != 200:
                continue
            soup = BeautifulSoup(response.text, "html.parser")
            main_content = soup.find("main") or soup.find("article") or soup.body
            text = main_content.get_text(separator="\n", strip=True) if main_content else ""
            results.append({"url": current_url, "content": text})
            print(current_url)

            for a in soup.find_all("a", href=True):
                link = urljoin(base_url, a["href"])
                link, _ = urldefrag(link)  
                if link.startswith(base_url) and link not in visited and link not in to_visit:
                    to_visit.append(link)

        except Exception as e:
            print(f"Error scraping {current_url}: {e}")

    os.makedirs("scraped_data", exist_ok=True)
    with open(f"scraped_data/{domain}.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

with ThreadPoolExecutor(max_workers=20) as executor:
    futures = [
        executor.submit(fetch_html_content, "https://docs.atlan.com/"),
        executor.submit(fetch_html_content, "https://developer.atlan.com/")
    ]
    for future in as_completed(futures):
        try:
            future.result()
        except Exception as e:
            print(f"Error in thread: {e}")
