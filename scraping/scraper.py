import requests
from bs4 import BeautifulSoup
import json
import time
import os

BASE_URL = "https://www.shl.com/solutions/products/product-catalog/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# ---------- SAFE REQUEST WRAPPER ----------
def fetch_page(url, retries=4):
    for attempt in range(retries):
        try:
            res = requests.get(url, headers=HEADERS, timeout=50)
            res.raise_for_status()
            return res.text
        except Exception as e:
            print(f"[WARN] Fetch retry {attempt+1}/{retries} for {url} ({e})")
            time.sleep(2)
    print(f"[ERROR] Failed to load page → {url}")
    return ""


# ---------- SCRAPE TABLE ----------
def scrape_table(table):
    assessments = []
    rows = table.find_all("tr")[1:]  # skip header

    for row in rows:
        cols = row.find_all("td")
        if len(cols) < 4:
            continue

        name_tag = cols[0].find("a")
        if not name_tag:
            continue

        name = name_tag.text.strip()
        url = "https://www.shl.com" + name_tag["href"]

        remote = "Yes" if cols[1].find("span", class_="catalogue__circle -yes") else "No"
        adaptive = "Yes" if cols[2].find("span", class_="catalogue__circle -yes") else "No"

        keys = cols[3].find_all("span", class_="product-catalogue__key")
        test_type = ", ".join(k.text.strip() for k in keys)

        assessments.append({
            "name": name,
            "url": url,
            "duration": "N/A",
            "test_type": test_type,
            "remote_testing": remote,
            "adaptive_irt": adaptive
        })

    return assessments


# ---------- PAGINATION SCRAPER ----------
def scrape_pages(type_param, label, max_pages=45):
    all_items = []

    for page_start in range(0, max_pages * 12, 12):
        url = f"{BASE_URL}?start={page_start}&type={type_param}"
        print(f"[{label}] Scraping: {url}")

        html = fetch_page(url)
        if not html:
            continue

        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table")

        # RETRY EMPTY TABLE (Cloudflare)
        if not table:
            print(f"[{label}] Empty table. Retrying...")
            time.sleep(2)
            html = fetch_page(url)
            soup = BeautifulSoup(html, "html.parser")
            table = soup.find("table")

            if not table:
                print(f"[{label}] Still empty → skipping page, but NOT stopping.")
                continue

        items = scrape_table(table)
        if items:
            all_items.extend(items)
        else:
            print(f"[{label}] No rows found → continuing.")

        time.sleep(1.2)

    return all_items


# ---------- MAIN SCRAPER ----------
def scrape_catalog():
    print("Scraping ONLY Individual Test Solutions (type=1)...")

    # scrape extended pagination to guarantee ≥ 377 items
    ind = scrape_pages(type_param=1, label="Individual", max_pages=45)

    # Ensure directory
    os.makedirs("data", exist_ok=True)

    # Save
    with open("data/shl_links.json", "w", encoding="utf-8") as f:
        json.dump(ind, f, indent=2)

    print(f"Saved {len(ind)} Individual Tests → data/shl_links.json")
    return ind


if __name__ == "__main__":
    scrape_catalog()
