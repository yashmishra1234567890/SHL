import requests
import json
import re
import pandas as pd
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import time
import os

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# ---------- SAFE REQUEST ----------
def safe_get(url, retries=5, delay=3):
    for attempt in range(retries):
        try:
            res = requests.get(url, headers=HEADERS, timeout=50)
            res.raise_for_status()
            return res
        except Exception as e:
            print(f"[WARN] Retry {attempt+1}/{retries} → {url} ({e})")
            time.sleep(delay)

    print(f"[ERROR] Skipping → {url}")
    return None


# ---------- PARSE DETAILS ----------
def fetch_details(assessment):
    url = assessment["url"]
    res = safe_get(url)

    if not res:
        return assessment

    soup = BeautifulSoup(res.text, "html.parser")

    try:
        sections = soup.find_all("div", class_="product-detail__section")
        for sec in sections:
            txt = sec.get_text(" ", strip=True).lower()

            match = re.search(r"(\d+)\s*(min|minute)", txt)
            if match:
                assessment["duration"] = f"{match.group(1)} minutes"
                break

    except Exception as e:
        print(f"[ERROR] Could not parse → {url} ({e})")

    return assessment


# ---------- PARSE ALL ----------
def parse_all():
    # Load JSON
    try:
        with open("data/shl_links.json", "r", encoding="utf-8") as f:
            assessments = json.load(f)
    except Exception as e:
        print("ERROR: Missing shl_links.json")
        print("Run scraper.py first")
        return

    print(f"Parsing details for {len(assessments)} assessments...")

    final = []

    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(fetch_details, a) for a in assessments]

        for i, fut in enumerate(as_completed(futures), start=1):
            final.append(fut.result())
            if i % 20 == 0:
                print(f"Progress: {i}/{len(assessments)}")

    os.makedirs("data/processed", exist_ok=True)

    df = pd.DataFrame(final)
    df.to_csv("data/processed/shl_catalog_clean.csv", index=False)

    print(f"Saved {len(df)} rows → data/processed/shl_catalog_clean.csv")


if __name__ == "__main__":
    parse_all()
