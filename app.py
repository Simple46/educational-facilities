import streamlit as st
import pandas as pd
import plotly.express as px


st.set_page_config(
    page_title="Nigeria Educational Facilities Dashboard",
    page_icon="🏫",
    layout="wide"
)


# @st.cache_data
def load_data():
    return pd.read_csv("data/Cleaned_dataset.csv")


df = load_data()


st.title("Educational Facilities in Nigeria")
st.markdown(
    """
    An interactive dashboard for exploring educational facilities,
    student populations, teachers, and infrastructure across Nigeria.
    """
)


# -----------------------------
# SIDEBAR
# -----------------------------

st.sidebar.header("Filters")

facility_types = sorted(
    df["Facility Type Display"].dropna().unique()
)

selected_facility = st.sidebar.multiselect(
    "Facility Type",
    options=facility_types,
    default=facility_types
)


management_types = sorted(
    df["Management"].dropna().unique()
)

selected_management = st.sidebar.multiselect(
    "Management",
    options=management_types,
    default=management_types
)


states = sorted(
    df["State"].dropna().unique()
)

selected_states = st.sidebar.multiselect(
    "State",
    options=states,
    default=states
)


filtered_df = df[
    df["Facility Type Display"].isin(selected_facility)
    & df["Management"].isin(selected_management)
    & df["State"].isin(selected_states)
]


total_schools = len(filtered_df)

total_students = filtered_df["Total Number Of Students"].sum()

avg_students = (
    filtered_df["Total Number Of Students"].mean()
    if total_schools > 0
    else 0
)

electricity_pct = (
    filtered_df["PHCN Electricity"].mean() * 100
    if total_schools > 0
    else 0
)

water_pct = (
    filtered_df["Improved Water Supply"].mean() * 100
    if total_schools > 0
    else 0
)


col1, col2, col3, col4, col5 = st.columns(5)

col1.metric(
    "Total Schools",
    f"{total_schools:,}"
)

col2.metric(
    "Total Students",
    f"{total_students:,.0f}"
)

col3.metric(
    "Avg Students Per School",
    f"{avg_students:,.0f}"
)

col4.metric(
    "Electricity Access",
    f"{electricity_pct:.1f}%"
)

col5.metric(
    "Improved Water",
    f"{water_pct:.1f}%"
)


st.divider()


# -----------------------------
# CHART 1: FACILITY TYPE DISTRIBUTION
# -----------------------------

st.subheader("Facility Type Distribution")

facility_counts = (
    filtered_df["Facility Type Display"]
    .value_counts()
    .reset_index()
)
facility_counts.columns = ["Facility Type", "Count"]

fig1 = px.bar(
    facility_counts,
    x="Facility Type",
    y="Count",
    text="Count",
    color="Facility Type",
    title="Facility Type Distribution",

)
fig1.update_traces(texttemplate="%{text:,}", textposition="outside")
fig1.update_layout(
    height=500,
    xaxis_tickangle=-45,
    showlegend=False,
    yaxis_title="Number of Facilities",
    title_x=0.5
)
st.plotly_chart(fig1, use_container_width=True)


# Chart for student distribution and public vs private


col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Student Population Distribution")

    fig2 = px.histogram(
        filtered_df,
        x="Total Number Of Students",
        nbins=20,
        labels={"Total Number Of Students": "Number of Students"}
    )
    fig2.update_layout(
        height=450,
        yaxis_title="Number of Schools",
        showlegend=False
    )
    st.plotly_chart(fig2, use_container_width=True)

with col_b:
    st.subheader("Public vs Private: Infrastructure Access")

    infra_cols = [
        "PHCN Electricity",
        "Improved Water Supply",
        "Improved Sanitation"
    ]

    infrastructure = (
        filtered_df.groupby("Management")[infra_cols]
        .mean()
        .mul(100)
    )

    infrastructure_plot = infrastructure.reset_index().melt(
        id_vars="Management",
        var_name="Infrastructure",
        value_name="Percentage"
    )

    fig3 = px.bar(
        infrastructure_plot,
        x="Management",
        y="Percentage",
        color="Infrastructure",
        barmode="group",
        text="Percentage",
        labels={
            "Management": "Management Type",
            "Percentage": "Percentage of Schools",
            "Infrastructure": "Infrastructure"
        }
    )
    fig3.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig3.update_layout(
        height=450,
        yaxis=dict(range=[0, 105]),
        title_x=0.5
    )
    st.plotly_chart(fig3, use_container_width=True)


# -----------------------------
# CHARTS 4 & 5: ELECTRICITY BY STATE + WATER & SANITATION BY STATE
# -----------------------------

col_c, col_d = st.columns(2)

with col_c:
    st.subheader("Electricity Access by State")

    elec_by_state = (
        filtered_df.groupby("State")["PHCN Electricity"]
        .mean()
        .mul(100)
        .sort_values(ascending=False)
        .reset_index()
    )
    elec_by_state.columns = ["State", "Electricity Access (%)"]

    fig4 = px.bar(
        elec_by_state,
        x="State",
        y="Electricity Access (%)",
        color="Electricity Access (%)",
        color_continuous_scale="RdYlGn",
        text="Electricity Access (%)"
    )
    fig4.update_traces(texttemplate="%{text:.1f}%", textposition="outside")
    fig4.update_layout(
        height=550,
        xaxis_tickangle=-60,
        coloraxis_showscale=False,
        yaxis=dict(range=[0, 105])
    )
    st.plotly_chart(fig4, use_container_width=True)

with col_d:
    st.subheader("Water & Sanitation by State")

    ws_by_state = (
        filtered_df.groupby("State")[
            ["Improved Water Supply", "Improved Sanitation"]]
        .mean()
        .mul(100)
        .reset_index()
        .melt(
            id_vars="State",
            var_name="Infrastructure",
            value_name="Percentage"
        )
    )

    fig5 = px.bar(
        ws_by_state,
        x="State",
        y="Percentage",
        color="Infrastructure",
        barmode="group"
    )
    fig5.update_layout(
        height=550,
        xaxis_tickangle=-60,
        yaxis=dict(range=[0, 105])
    )
    st.plotly_chart(fig5, use_container_width=True)


# -----------------------------
# CHART 6: GEOGRAPHIC MAP
# -----------------------------

st.subheader("Geographic Distribution of Facilities")

# ⚠️ Check your actual column names for coordinates
LAT_COL = "Latitude"
LON_COL = "Longitude"

if LAT_COL in filtered_df.columns and LON_COL in filtered_df.columns:
    map_df = filtered_df.dropna(subset=[LAT_COL, LON_COL])

    if not map_df.empty:
        fig6 = px.scatter_map(
            map_df,
            lat=LAT_COL,
            lon=LON_COL,
            color="Management",
            hover_name="Facility Type Display"
            if "Facility Type Display" in map_df.columns
            else None,
            hover_data={
                "State": True,
                "Total Number Of Students": True,
                "Facility Name": True,
                LAT_COL: False,
                LON_COL: False
            },
            zoom=5,
            center={"lat": 9.08, "lon": 8.68},
            map_style="open-street-map",
            height=600
        )
        st.plotly_chart(fig6, use_container_width=True)
    else:
        st.info("No coordinate data available for the current filters.")
else:
    st.info("Latitude/Longitude columns not found in the dataset.")


# -----------------------------
# DOWNLOAD FILTERED DATA
# -----------------------------

st.divider()
st.subheader("Export Filtered Data")

csv = filtered_df.to_csv(index=False).encode("utf-8")

st.download_button(
    label="Download filtered data as CSV",
    data=csv,
    file_name="filtered_educational_facilities.csv",
    mime="text/csv"
)
