import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import matplotlib.pyplot as plt
from pathlib import Path

# 1. Page configuration
st.set_page_config(
    page_title="Navratri Culture Dashboard",
    page_icon="🪔",
    layout="wide"
)

# 2. Custom CSS
st.markdown("""
<style>
.stApp {
    background-color: #fff8f0;
}
h1, h2, h3 {
    color: #8B008B;
}
div[data-testid="stMetric"] {
    background-color: white;
    padding: 14px;
    border-radius: 12px;
    border: 1px solid #f0c4a0;
}
</style>
""", unsafe_allow_html=True)

# 3. Header
st.title("🪔 Navratri: A Journey of Faith & Culture")
st.write(
    "Explore Navratri participation, Garba and Dandiya "
    "preferences, cultural traditions and festival spending."
)

st.divider()

# 4. Load CSV dataset
DATA_FILE = (
    Path(__file__).parent
    / "Navratri_Culture_Survey_500_Persons.csv"
)

@st.cache_data
def load_data(file_path):
    df = pd.read_csv(file_path)

    # Clean column names and text values
    df.columns = df.columns.str.strip()

    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    return df

if not DATA_FILE.exists():
    st.error(
        "Dataset not found. Keep the CSV file in the "
        "same folder as app.py."
    )
    st.stop()

try:
    df = load_data(DATA_FILE)
except Exception as e:
    st.error(f"Dataset loading failed: {e}")
    st.stop()

# Validate required columns
required_columns = [
    "Respondent_ID",
    "Festival_Year",
    "Age_Group",
    "Region",
    "City",
    "Preferred_Activity",
    "Favorite_Navratri_Day",
    "Days_Participated",
    "Attendance_Location",
    "Estimated_Spending_INR",
    "Celebrates_With_Family",
    "Cultural_Connection_Impact"
]

missing = [
    col for col in required_columns
    if col not in df.columns
]

if missing:
    st.error(f"Missing columns: {missing}")
    st.stop()

# 5. Sidebar filters
st.sidebar.title("🔎 Dashboard Filters")

regions = ["All"] + sorted(
    df["Region"].dropna().unique().tolist()
)
selected_region = st.sidebar.selectbox(
    "Select Region", regions
)

years = ["All"] + sorted(
    df["Festival_Year"].dropna().unique().tolist()
)
selected_year = st.sidebar.selectbox(
    "Select Festival Year", years
)

activities = ["All"] + sorted(
    df["Preferred_Activity"].dropna().unique().tolist()
)
selected_activity = st.sidebar.selectbox(
    "Select Preferred Activity", activities
)

age_groups = ["All"] + sorted(
    df["Age_Group"].dropna().unique().tolist()
)
selected_age = st.sidebar.selectbox(
    "Select Age Group", age_groups
)

# Apply filters
filtered = df.copy()

if selected_region != "All":
    filtered = filtered[
        filtered["Region"] == selected_region
    ]

if selected_year != "All":
    filtered = filtered[
        filtered["Festival_Year"] == selected_year
    ]

if selected_activity != "All":
    filtered = filtered[
        filtered["Preferred_Activity"] == selected_activity
    ]

if selected_age != "All":
    filtered = filtered[
        filtered["Age_Group"] == selected_age
    ]

if filtered.empty:
    st.warning("No records match these filters.")
    st.stop()

# 6. KPI cards
st.subheader("📊 Survey Overview")

total_people = filtered["Respondent_ID"].nunique()
avg_days = filtered["Days_Participated"].mean()
avg_spending = filtered["Estimated_Spending_INR"].mean()
total_cities = filtered["City"].nunique()

c1, c2, c3, c4 = st.columns(4)

c1.metric("👥 Respondents", f"{total_people:,}")
c2.metric("🪔 Average Days", f"{avg_days:.1f}")
c3.metric("💰 Average Spending", f"₹{avg_spending:,.0f}")
c4.metric("🏙️ Cities", f"{total_cities:,}")

st.caption(
    "All metrics describe the survey records after applying filters."
)

st.divider()

# 7. Tabs
tab1, tab2, tab3, tab4 = st.tabs([
    "🎶 Activities",
    "🇮🇳 Regional Analysis",
    "💰 Spending",
    "🪔 Culture & Participation"
])

# TAB 1: Activities
with tab1:
    st.subheader("Garba, Dandiya and Other Preferences")

    activity_counts = (
        filtered["Preferred_Activity"]
        .value_counts()
        .rename_axis("Activity")
        .reset_index(name="Respondents")
    )

    col1, col2 = st.columns(2)

    with col1:
        fig = px.bar(
            activity_counts,
            x="Activity",
            y="Respondents",
            color="Activity",
            title="Preferred Festival Activities",
            text="Respondents"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.pie(
            activity_counts,
            names="Activity",
            values="Respondents",
            hole=0.45,
            title="Activity Preference Share"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Favorite Navratri Day")

    day_counts = (
        filtered["Favorite_Navratri_Day"]
        .value_counts()
        .rename_axis("Day")
        .reset_index(name="Respondents")
    )

    fig = px.bar(
        day_counts,
        x="Day",
        y="Respondents",
        color="Respondents",
        title="Most Favorite Navratri Days"
    )
    st.plotly_chart(fig, use_container_width=True)

# TAB 2: Regional analysis
with tab2:
    st.subheader("Navratri Preferences Across Regions")

    col1, col2 = st.columns(2)

    with col1:
        region_counts = (
            filtered["Region"]
            .value_counts()
            .rename_axis("Region")
            .reset_index(name="Respondents")
        )

        fig = px.pie(
            region_counts,
            names="Region",
            values="Respondents",
            hole=0.4,
            title="Respondents by Region"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        city_counts = (
            filtered["City"]
            .value_counts()
            .head(15)
            .rename_axis("City")
            .reset_index(name="Respondents")
        )

        fig = px.bar(
            city_counts,
            x="Respondents",
            y="City",
            orientation="h",
            title="Top 15 Cities by Respondents"
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Region-wise Activity Preferences")

    cross_tab = pd.crosstab(
        filtered["Region"],
        filtered["Preferred_Activity"]
    )

    fig = px.imshow(
        cross_tab,
        text_auto=True,
        aspect="auto",
        title="Region vs Preferred Activity",
        labels={
            "x": "Activity",
            "y": "Region",
            "color": "Respondents"
        }
    )
    st.plotly_chart(fig, use_container_width=True)

# TAB 3: Spending analysis
with tab3:
    st.subheader("Festival Spending Patterns")

    col1, col2 = st.columns(2)

    with col1:
        spending_counts = (
            filtered["Spending_Category_INR"]
            .value_counts()
            .rename_axis("Spending Category")
            .reset_index(name="Respondents")
        )

        fig = px.bar(
            spending_counts,
            x="Spending Category",
            y="Respondents",
            color="Spending Category",
            title="Spending Categories"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig = px.histogram(
            filtered,
            x="Estimated_Spending_INR",
            nbins=15,
            title="Estimated Spending Distribution",
            labels={"Estimated_Spending_INR": "Spending (INR)"}
        )
        st.plotly_chart(fig, use_container_width=True)

    st.subheader("Spending by Activity")

    fig = px.box(
        filtered,
        x="Preferred_Activity",
        y="Estimated_Spending_INR",
        color="Preferred_Activity",
        title="Estimated Spending Across Activities"
    )
    st.plotly_chart(fig, use_container_width=True)

# TAB 4: Culture and participation
with tab4:
    st.subheader("Participation and Cultural Connection")

    col1, col2 = st.columns(2)

    with col1:
        participation = (
            filtered["Days_Participated"]
            .value_counts()
            .sort_index()
            .rename_axis("Days Participated")
            .reset_index(name="Respondents")
        )

        fig = px.bar(
            participation,
            x="Days Participated",
            y="Respondents",
            title="Festival Participation by Number of Days"
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        family_counts = (
            filtered["Celebrates_With_Family"]
            .value_counts()
            .rename_axis("Family Celebration")
            .reset_index(name="Respondents")
        )

        fig = px.pie(
            family_counts,
            names="Family Celebration",
            values="Respondents",
            hole=0.4,
            title="Celebration with Family"
        )
        st.plotly_chart(fig, use_container_width=True)

    impact_counts = (
        filtered["Cultural_Connection_Impact"]
        .value_counts()
        .rename_axis("Cultural Impact")
        .reset_index(name="Respondents")
    )

    fig = px.bar(
        impact_counts,
        x="Cultural Impact",
        y="Respondents",
        color="Cultural Impact",
        title="Reported Impact on Cultural Connection"
    )
    st.plotly_chart(fig, use_container_width=True)

    st.subheader("Survey Data")

    st.dataframe(
        filtered,
        use_container_width=True,
        hide_index=True
    )

# 8. Statistical summary
st.divider()
st.subheader("📈 Statistical Summary")

numeric_values = filtered[
    ["Days_Participated", "Estimated_Spending_INR"]
]

summary = numeric_values.agg(
    ["mean", "median", "min", "max"]
).round(2)

st.dataframe(summary, use_container_width=True)

# 9. Matplotlib histogram
st.subheader("📊 Participation Distribution")

fig, ax = plt.subplots(figsize=(9, 4))

ax.hist(
    filtered["Days_Participated"].dropna(),
    bins=range(0, 11),
    edgecolor="black"
)

ax.set_title("Distribution of Navratri Participation Days")
ax.set_xlabel("Days Participated")
ax.set_ylabel("Number of Respondents")
ax.set_xticks(range(0, 10))

st.pyplot(fig)
plt.close(fig)

# 10. Download filtered data
st.divider()
st.subheader("⬇️ Download Survey Data")

csv_data = filtered.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download Filtered Data (CSV)",
    data=csv_data,
    file_name="navratri_culture_filtered.csv",
    mime="text/csv"
)

st.caption(
    "Built with Python, Pandas, NumPy, Matplotlib, "
    "Plotly and Streamlit."
)