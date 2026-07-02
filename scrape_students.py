"""
Scrape all 3000 students from the Amazon ML Summer School 2026 selection test
results on Unstop and save to CSV.

API: https://unstop.com/api/public/live-leaderboard/439416/assessmentnewround
"""

import csv
import json
import time
import urllib.request
import urllib.error

API_URL = "https://unstop.com/api/public/live-leaderboard/439416/assessmentnewround"
PER_PAGE = 30
OUTPUT_FILE = "amlss_2026_students.csv"


def fetch_page(page: int) -> dict:
    """Fetch a single page of results from the API."""
    url = f"{API_URL}?page={page}&per_page={PER_PAGE}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read().decode())


def main():
    # First request to get total count
    print("Fetching page 1 to get total count...")
    first = fetch_page(1)
    total = first["data"]["total"]
    last_page = first["data"]["last_page"]
    print(f"Total students: {total}, Pages: {last_page}")

    all_students = []

    for page in range(1, last_page + 1):
        try:
            if page == 1:
                data = first  # reuse first request
            else:
                data = fetch_page(page)

            entries = data["data"]["data"]
            for entry in entries:
                player = entry["team"]["players"][0]
                all_students.append({
                    "S.No": len(all_students) + 1,
                    "Name": player["name"],
                    "Institute": player["organisation"],
                    "Profile URL": f"https://unstop.com{player['profile_url']}",
                })

            print(f"  Page {page:>3}/{last_page} — {len(entries)} students (total so far: {len(all_students)})")

            # Small delay to be polite to the server
            if page < last_page:
                time.sleep(0.3)

        except (urllib.error.URLError, urllib.error.HTTPError) as e:
            print(f"  ERROR on page {page}: {e}. Retrying in 3s...")
            time.sleep(3)
            try:
                data = fetch_page(page)
                entries = data["data"]["data"]
                for entry in entries:
                    player = entry["team"]["players"][0]
                    all_students.append({
                        "S.No": len(all_students) + 1,
                        "Name": player["name"],
                        "Institute": player["organisation"],
                        "Profile URL": f"https://unstop.com{player['profile_url']}",
                    })
                print(f"  Page {page:>3}/{last_page} — {len(entries)} students (retry OK)")
            except Exception as e2:
                print(f"  FAILED page {page}: {e2}")

    # Write to CSV
    with open(OUTPUT_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["S.No", "Name", "Institute", "Profile URL"])
        writer.writeheader()
        writer.writerows(all_students)

    print(f"\n✅ Done! Saved {len(all_students)} students to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
