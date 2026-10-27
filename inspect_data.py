import pandas as pd

df = pd.read_csv("data/transfermarkt_raw.csv")

print("\n=== SHAPE (rows columns) ===")
print(df.shape)

print("\n=== COLUMNS AND TYPES ===")
print(df.dtypes)

print("\n=== MISSING VALUES PER COLUMN ===")
print(df.isna().sum())

print("\n=== DUPLICATES ===")
print("Duplicate Player_ID:", df["Player_ID"].duplicated().sum())

print("\n=== NUMBERS SUMMARY ===")
print(df[["Age", "Height_m", "International_Matches", "Market_Value"]].describe())

print("\n=== VALUES THAT SHOULD BE CATEGORIES ===")
print(df["Position"].value_counts())
print()
print(df["National_Team_Status"].value_counts().head(10))

print("\n=== PLAYERS WITHOUT MOROCCO IN NATIONALITIES ===")
print((~df["Nationalities"].astype(str).str.contains("Morocco")).sum())