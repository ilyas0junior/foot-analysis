# scrapers/transfermarkt.py
import re
import time

import pandas as pd
from bs4 import BeautifulSoup
from playwright.sync_api import sync_playwright

URL = ("https://www.transfermarkt.com/detailsuche/spielerdetail/suche/65728803{page}")   # {page} gets replaced: 1, 2, 3...
UA = ("Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36")
SEARCH_URL = "https://www.transfermarkt.com/detailsuche/spielerdetail/suche"
 

def parse_value(text):
    """'€25.00m' -> 25000000.0 | '€800k' -> 800000.0 | '-' -> 0.0"""
    text = text.replace("€", "").strip().lower()
    match = re.match(r"([\d.,]+)\s*(m|k|th\.)?", text)
    if not match:
        return 0.0
    number = float(match.group(1).replace(",", ""))
    if match.group(2) == "m":
        return number * 1_000_000
    if match.group(2):
        return number * 1_000
    return number


def parse_rows(html):
    """Read one page of HTML, return one dict per player (one per table row)."""
    soup = BeautifulSoup(html, "lxml")
    players = []

    for tr in soup.select("table.items > tbody > tr"):
        # recursive=False: only the 9 direct cells, not those of nested tables
        tds = tr.find_all("td", recursive=False)
        if len(tds) < 9:                       # not a player row, skip it
            continue

        # td[1]: name (link) + position (second row of the nested table)
        name_link = tds[1].select_one("td.hauptlink a")
        if not name_link:
            continue
        href = str(name_link.get("href") or "")
        player_id = href.rstrip("/").split("/")[-1]
        inner = tds[1].select("table.inline-table tr")
        position = inner[1].get_text(strip=True) if len(inner) > 1 else None

        # td[0]: shirt number (text like '22', can be empty)
        number = tds[0].get_text(strip=True)

        # td[2]: '20/05/2003 (23)' -> birth date + age
        dob, age = None, None
        m = re.search(r"(\d{2}/\d{2}/\d{4})\s*\((\d+)\)", tds[2].get_text())
        if m:
            dob = pd.to_datetime(m.group(1), format="%d/%m/%Y").date()
            age = int(m.group(2))

        # td[3]: nationalities are flag images, so we read their titles
        nationalities = [str(img.get("title")) for img in tds[3].select("img")
                         if img.get("title")]

        # td[4]: the club is a logo, so we read its title
        club_img = tds[4].select_one("img")
        club = str(club_img.get("title") or "") if club_img else None

        # td[5]: '1,86 m' -> 1.86 (None if empty)
        height = None
        hm = re.search(r"(\d),(\d{2})", tds[5].get_text())
        if hm:
            height = float(f"{hm.group(1)}.{hm.group(2)}")

        # td[6]: national team status, plus the team's flag if there is one
        nat_text = tds[6].get_text(" ", strip=True)
        nat_img = tds[6].select_one("img")
        national_team = str(nat_img.get("title") or "") if nat_img else None

        # td[7]: international matches, '-' means 0
        caps_text = tds[7].get_text(strip=True)
        caps = int(caps_text) if caps_text.isdigit() else 0

        # td[8]: market value
        value = parse_value(tds[8].get_text())

        players.append({
            "Number": number,
            "Player": name_link.get_text(strip=True),
            "Player_ID": player_id,
            "Profile_URL": "https://www.transfermarkt.com" + href,
            "Position": position,
            "Date_of_Birth": dob,
            "Age": age,
            "Nationalities": ", ".join(nationalities),
            "Club": club,
            "Height_m": height,
            "National_Team_Status": nat_text,
            "National_Team": national_team,
            "International_Matches": caps,
            "Market_Value": value,
        })
    return players


def scrape(max_pages=20, headless=True):
    """Go through the pages until one is empty, return a DataFrame."""
    all_players = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless)
        page = browser.new_context(user_agent=UA).new_page()
        for n in range(1, max_pages + 1):
            page.goto(URL.format(page=n), wait_until="domcontentloaded")
            page.wait_for_timeout(1500)
            batch = parse_rows(page.content())
            if not batch:                                 # empty page = no more players
                break
            all_players += batch
            print(f"Page {n}: {len(batch)} players")
            time.sleep(3)                                 # be polite to the server
        browser.close()
    return pd.DataFrame(all_players).drop_duplicates("Player")


def accept_cookies(page):
    """Click 'Accept' on the consent popup if it appears."""
    try:
        # The popup lives inside an iframe, so we enter it first
        frame = page.frame_locator("iframe[title='SP Consent Message']")
        frame.get_by_role("button", name="ACCEPT ALL").click(timeout=8000)
        print("Cookies accepted")
        page.wait_for_timeout(2000)
    except Exception:
        print("No cookie popup found (or button name differs)")
        
def scrape_results(page, max_pages=5):
    """Parse the current results page, then click through the next pages."""
    all_players = []

    for n in range(1, max_pages + 1):
        batch = parse_rows(page.content())
        all_players += batch
        print(f"Page {n}: {len(batch)} players")

        # Link to the next page: its href ends with /page/<n+1>
        next_link = page.locator(f"a[href$='/page/{n + 1}']").first
        if next_link.count() == 0:       # no such link = last page
            break

        next_link.click()
        page.wait_for_timeout(3000)      # wait for the AJAX update
        time.sleep(2)                    # be polite to the server

    return pd.DataFrame(all_players).drop_duplicates("Player")

def inspect_rows(html, n_rows=3):
    """Print every cell of the first rows: position, CSS class, text, image titles."""
    soup = BeautifulSoup(html, "lxml")
    rows = soup.select("table.items > tbody > tr")
    for tr in rows[:n_rows]:
        print("-" * 60)
        # recursive=False: only the direct cells, not the ones in nested tables
        for i, td in enumerate(tr.find_all("td", recursive=False)):
            text = td.get_text(" ", strip=True)
            titles = [img.get("title") for img in td.select("img") if img.get("title")]
            print(f"td[{i}] class={td.get('class')} | text={text!r} | img titles={titles}")

if __name__ == "__main__":
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            "data/browser_profile", headless=False, user_agent=UA
        )
        page = context.new_page()
        page.goto(SEARCH_URL)

        input("Accept cookies, set Citizenship = Morocco, click Search, "
              "WAIT for the results, then press Enter here... ")

        df = scrape_results(page, max_pages=10)   # raise this for the real run
        print(df.head(10))
        print(len(df), "players total")
        df.to_csv("data/transfermarkt_raw.csv", index=False)
        context.close()