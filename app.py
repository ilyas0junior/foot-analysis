# app.py
# Part A: load the clean data, add sidebar filters, show KPIs and a table.

import pandas as pd
import streamlit as st
import plotly.express as px

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
# Stop early if the filters remove every player
if filtered.empty:
    st.warning("No players match these filters.")
    st.stop()

tab1, tab2, tab3, tab4 = st.tabs(["Top players", "Profile", "Clubs & countries", "Table"])

# ---------- Tab 1: most valuable players ----------
with tab1:
    top = filtered.nlargest(10, "Market_Value_M").sort_values("Market_Value_M")
    fig = px.bar(
        top, x="Market_Value_M", y="Player", orientation="h",
        color="Position_Group", hover_data=["Club", "Age"],
        labels={"Market_Value_M": "Market value (€M)", "Position_Group": "Position"},
        title="Top 10 by market value",
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------- Tab 2: who are these players? ----------
with tab2:
    col1, col2 = st.columns(2)
    with col1:
        fig = px.histogram(filtered, x="Age", nbins=20, title="Age distribution")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        counts = filtered["Position_Group"].value_counts().reset_index()
        counts.columns = ["Position", "Players"]
        fig = px.pie(counts, names="Position", values="Players", title="Players by position")
        st.plotly_chart(fig, use_container_width=True)

    fig = px.scatter(
        filtered, x="Age", y="Market_Value_M", color="Position_Group",
        hover_name="Player", hover_data=["Club"],
        labels={"Market_Value_M": "Market value (€M)", "Position_Group": "Position"},
        title="Age vs market value",
    )
    st.plotly_chart(fig, use_container_width=True)

# ---------- Tab 3: clubs and countries ----------
with tab3:
    col1, col2 = st.columns(2)
    with col1:
        clubs = (filtered.groupby("Club")["Market_Value_M"].sum().nlargest(10).sort_values().reset_index())
        fig = px.bar(clubs, x="Market_Value_M", y="Club", orientation="h",
                     labels={"Market_Value_M": "Total value (€M)"},
                     title="Top 10 clubs by total value of Moroccan players")
        st.plotly_chart(fig, use_container_width=True)
    with col2:
        # "France, Spain" -> two rows, then count each country
        others = (filtered["Other_Nationality"].str.split(", ").explode())
        others = others[others != "None"].value_counts().head(10).sort_values().reset_index()
        others.columns = ["Country", "Players"]
        fig = px.bar(others, x="Players", y="Country", orientation="h",
                     title="Second nationality of dual nationals")
        st.plotly_chart(fig, use_container_width=True)

# ---------- Tab 4: full table ----------
with tab4:
    st.dataframe(
        filtered[["Player", "Position", "Age", "Club", "Other_Nationality","Intl_Status", "International_Matches", "Market_Value_M"]].sort_values("Market_Value_M", ascending=False),
        use_container_width=True,
        hide_index=True,
        column_config={
            "Market_Value_M": st.column_config.NumberColumn("Value (€M)", format="%.2f"),
            "International_Matches": "Caps",
        },
    )