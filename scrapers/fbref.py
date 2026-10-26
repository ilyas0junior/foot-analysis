from io import StringIO
import pandas as pd
from playwright.sync_api import sync_playwright

url = "https://fbref.com/en/comps/13/stats/Ligue-1-Stats"
SEARCH_URL = "https://www.transfermarkt.com/detailsuche/spielerdetail/suche"

def get_table(page):
    """Wait for the stats table, then turn it into a pandas DataFrame."""
    page.wait_for_selector("table#stats_standard", timeout=180000)    
    html = page.inner_html("table#stats_standard")
    return pd.read_html(StringIO(f"<table>{html}</table>"))[0]

def flatten_columns(df):
    """Turn two-level headers like ('Playing Time', 'Min')"""    
    new_cols = []
    for top, sub in df.columns:
        if str(top).startswith("Unnamed"):
            new_cols.append(sub)
        else:
            new_cols.append(f"{top}_{sub}")
    df.columns = new_cols
    return df

def keep_moroccans(df):
    """Remove repeated header rows, then keep only players whose nation contains MAR"""
    df = df[df["Player"] != "Player"]
    return df[df["Nation"].astype(str).str.contains("MAR")].copy()

if __name__ == "__main__":
    with sync_playwright() as p:
        context = p.chromium.launch_persistent_context(
            "data/brave_profile",                      # a new profile, separate from the old one
            executable_path="/usr/bin/brave-browser",  # use the path you found
            headless=False,
)
        page = context.new_page()
        page.goto(url, wait_until="domcontentloaded")

        input("Solve the check by hand, wait until you SEE the stats table, "
              "then press Enter here... ")

        print("Title:", page.title())
        ids = page.eval_on_selector_all("table", "els => els.map(e => e.id)")
        print("Table ids:", ids)

        context.close()