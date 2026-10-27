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
    """Turn the messy status text into one clean category."""
    t = " ".join(str(text).split()).lower()    # collapse any odd spaces, lowercase
    if "resigned" in t:
        return "Resigned"
    if "not national team player" in t:
        return "Never capped"
    if "not current" in t:                     # check this BEFORE "current"
        return "Former international"
    if "current national team player" in t:
        return "Current international"
    return "Unknown"


def other_nationality(text):
    """'Morocco, Germany' -> 'Germany' | 'Morocco' -> 'None'"""
    others = [n.strip() for n in str(text).split(",") if n.strip() != "Morocco"]
    return ", ".join(others) or "None"


def clean(df):
    df = df.copy()

    df["Player"] = df["Player"].str.strip()
    df["Date_of_Birth"] = pd.to_datetime(df["Date_of_Birth"], errors="coerce")

    df["Position_Group"] = df["Position"].map(POSITION_GROUPS)
    df["Intl_Status"] = df["National_Team_Status"].map(intl_status)
    df["National_Team"] = df["National_Team"].fillna("None")

    df["Is_Dual_National"] = df["Nationalities"].str.contains(",")
    df["Other_Nationality"] = df["Nationalities"].map(other_nationality)

    df["Market_Value_M"] = (df["Market_Value"] / 1_000_000).round(2)  # millions of euros

    # Shirt number changes with the club and we don't need it
    # National_Team_Status is replaced by Intl_Status
    return df.drop(columns=["Number", "National_Team_Status"])


def validate(df):
    """Print a list of problems, or a green light if there are none."""
    problems = []

    if df["Player_ID"].duplicated().any():
        problems.append("Duplicate Player_ID found")

    unmapped = df.loc[df["Position_Group"].isna(), "Position"].unique()
    if len(unmapped):
        problems.append(f"Positions not in POSITION_GROUPS: {list(unmapped)}")

    if not df["Age"].between(15, 45).all():
        problems.append("Some ages are outside 15-45")

    if not df["Height_m"].dropna().between(1.5, 2.2).all():
        problems.append("Some heights are outside 1.5-2.2 m")

    if (df["Market_Value"] <= 0).any():
        problems.append("Some market values are zero or negative")

    if df["Date_of_Birth"].isna().any():
        problems.append("Some dates of birth could not be read")

    if (df["Intl_Status"] == "Unknown").any():
        problems.append("Some national team statuses are not recognised")

    # Age on the site should match the date of birth (within one year)
    # Age on the site should match the date of birth (whole years, within 1)
    years = (pd.Timestamp.today() - df["Date_of_Birth"]).dt.days // 365.25
    mismatch = df[(years - df["Age"]).abs() > 1]
    if len(mismatch):
        problems.append(f"Age does not match date of birth for {len(mismatch)} players")
        print(mismatch[["Player", "Date_of_Birth", "Age"]].head())

    if problems:
        print("⚠️  PROBLEMS FOUND:")
        for p in problems:
            print("  -", p)
    else:
        print("✅ All checks passed")


if __name__ == "__main__":
    raw = pd.read_csv(RAW)
    df = clean(raw)
    validate(df)

    print("\nPosition groups:\n", df["Position_Group"].value_counts())
    print("\nInternational status:\n", df["Intl_Status"].value_counts())
    print("\nDual nationals:", df["Is_Dual_National"].sum(), "of", len(df))

    df.to_csv(OUT, index=False)
    print(f"\nSaved {len(df)} players to {OUT}")
    print(raw["National_Team_Status"].map(repr).value_counts().head())