import pandas as pd

RAW = "data/transfermarkt_raw.csv"
OUT = "data/players_clean.csv"

POSITION_GROUPS = {
    "Goalkeeper":"Goalkeeper",
    "Centre-Back":"Defender",
    "Left-Back":"Defender",
    "Right-Back":"Defender",
    "Defensive Midfield":"Midfielder",
    "Central Midfield":"Midfielder",
    "Attacking Midfield":"Midfielder",
    "Left Midfield":"Midfielder",
    "Right Midfield":"Midfielder",
    "Left Winger":"Attacker",
    "Right Winger":"Attacker",
    "Centre-Forward":"Attacker",
    "Second Striker":"Attacker",
    "none":"none",
}

def intl_status(text):
    """Turn the messy status text into onr clean category."""
    text = str()
    if text.startswith("Not national team player"):
        return "Never capped"
    if "Not current" in text:
        return "Former international"
    if "Current national team player" in text:
        return "Current international"
    if "Resigned" in text:
        return "Resigned"
    return "Unknown"