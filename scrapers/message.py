from playwright.sync_api import sync_playwright
import random
import time
import csv

def random_delay(min_sec=2, max_sec=5):
    time.sleep(random.uniform(min_sec, max_sec))

def get_random_user_agent():
    agents = ["Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"]
    return random.choice(agents)

moroccan_players = []

def run(p):
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(user_agent=get_random_user_agent())
    page = context.new_page()

    for i in range(1, 11):
        try:
            page.goto(f"https://www.transfermarkt.com/detailsuche/spielerdetail/suche/55017926/page/{i}", timeout=0)
            random_delay()

            players = page.query_selector_all(
                "#yw0 > table > tbody > tr > td:nth-child(2) > table > tbody > tr:nth-child(1) > td.hauptlink > a"
            )

            for player in players:
                name = player.inner_text().strip()
                href = player.get_attribute("href")
                if name and href:
                    moroccan_players.append({"name": name, "url": f"https://www.transfermarkt.com{href}"})

        except Exception as e:
            print(f"Error on page {i}: {e}")

    browser.close()

with sync_playwright() as p:
    run(p)
    print(moroccan_players)
    with open("moroccan_players.csv", "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=["name", "url"])
        writer.writeheader()
        writer.writerows(moroccan_players)