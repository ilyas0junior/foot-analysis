# app.py
# Part A: load the clean data, add sidebar filters, show KPIs and a table.

import pandas as pd
import streamlit as st

# Must be the first Streamlit command in the script
st.set_page_config(page_title="Moroccan Footballers", page_icon="🇲🇦", layout="wide")


@st.cache_data   # reads the CSV once and remembers it, so the app stays fast
def load_data():
    return pd.read_csv("data/players_clean.csv", parse_dates=["Date_of_Birth"])


df = load_data()

st.title("🇲🇦 Moroccan Footballers Dashboard")
st.caption("Data: Transfermarkt")

# ---------- Sidebar filters ----------
st.sidebar.header("Filters")

positions = st.sidebar.multiselect(
    "Position", sorted(df["Position_Group"].unique()),
    default=sorted(df["Position_Group"].unique()),
)
statuses = st.sidebar.multiselect(
    "International status", sorted(df["Intl_Status"].unique()),
    default=sorted(df["Intl_Status"].unique()),
)
age_min, age_max = int(df["Age"].min()), int(df["Age"].max())
age_range = st.sidebar.slider("Age", age_min, age_max, (age_min, age_max))

only_dual = st.sidebar.checkbox("Dual nationals only")

# ---------- Apply the filters ----------
# Each condition gives True/False per row, and & means "and"
mask = (
    df["Position_Group"].isin(positions)
    & df["Intl_Status"].isin(statuses)
    & df["Age"].between(*age_range)
)
if only_dual:
    mask &= df["Is_Dual_National"]

filtered = df[mask]

# ---------- KPIs ----------
c1, c2, c3, c4 = st.columns(4)
c1.metric("Players", len(filtered))
c2.metric("Average age", f"{filtered['Age'].mean():.1f}" if len(filtered) else "-")
c3.metric("Total value", f"€{filtered['Market_Value_M'].sum():,.0f}M")
c4.metric("Average value", f"€{filtered['Market_Value_M'].mean():.2f}M" if len(filtered) else "-")

# ---------- Table ----------
st.subheader("Players")
st.dataframe(
    filtered[["Player", "Position", "Age", "Club", "Other_Nationality",
              "Intl_Status", "International_Matches", "Market_Value_M"]]
    .sort_values("Market_Value_M", ascending=False),
    use_container_width=True,
    hide_index=True,
)