# 🇲🇦 Moroccan Footballers Dashboard

An interactive dashboard to analyze Moroccan footballers: age, market value, clubs, nationalities, international caps and more. Data is collected with web scraping from Transfermarkt, then cleaned and explored in a Streamlit app.

> **Status:** work in progress. The Transfermarkt scraper works; the Streamlit dashboard is the next step.

## Tech stack

- **Python 3.10+**
- **Playwright**: browser automation for scraping
- **BeautifulSoup + lxml**: HTML parsing
- **pandas**: data cleaning and analysis
- **Streamlit + Plotly**: interactive dashboard

## Project structure

```
dashboard-marocains/
├── scrapers/
│   └── transfermarkt.py     # scrapes Moroccan players from Transfermarkt
├── data/                    # generated CSV files (ignored by git)
├── requirements.txt
├── .gitignore
└── README.md
```

## Data collected

For each player, the scraper extracts:

| Column | Description |
|---|---|
| `Number` | Shirt number |
| `Player`, `Player_ID`, `Profile_URL` | Name, Transfermarkt ID and profile link |
| `Position` | Playing position |
| `Date_of_Birth`, `Age` | Date of birth and age |
| `Nationalities` | All nationalities (dual nationals included) |
| `Club` | Current club |
| `Height_m` | Height in meters |
| `National_Team_Status`, `National_Team` | National team status and team |
| `International_Matches` | Number of international caps |
| `Market_Value` | Market value in euros |

## Installation

```bash
git clone https://github.com/YOUR_USERNAME/dashboard-marocains.git
cd dashboard-marocains

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install -r requirements.txt
playwright install chromium
```

On Linux, if Chromium fails to start, install its system dependencies:
```bash
sudo venv/bin/playwright install-deps chromium
```

## Usage

```bash
python scrapers/transfermarkt.py
```

A browser window opens on Transfermarkt's advanced player search. Then:

1. Accept the cookie popup.
2. Set **Citizenship = Morocco** (optionally a minimum market value) and click **Search**.
3. Wait for the results, then press **Enter** in the terminal.

The scraper clicks through the result pages and saves everything to `data/transfermarkt_raw.csv`.

## Roadmap

- [x] Transfermarkt scraper (profile, club, market value, caps)
- [ ] Data cleaning and validation
- [ ] Performance stats (appearances, goals, assists, minutes)
- [ ] Streamlit dashboard: filters, KPIs, rankings, scatter plots, player comparison
- [ ] Automate the search form so the scraper runs without manual steps

## Notes

- **FBref was dropped** as a data source. It lost its advanced statistics in 2026 and blocks automated browsers behind a human-verification check.
- Scraping is slow on purpose (pauses between requests) to stay polite to the server.
- Check Transfermarkt's terms of use before reusing or redistributing the data. This project is for educational purposes.

## Author

**Ilyas Kibbou**
AI & Big Data Engineer
