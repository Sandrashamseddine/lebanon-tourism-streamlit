
import streamlit as st
import pandas as pd
import plotly.express as px

# --------------------------------------------------
# PAGE SETUP
# --------------------------------------------------

st.set_page_config(
    page_title="Lebanon Tourism Data Explorer",
    page_icon="🌍",
    layout="wide"
)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------

import glob

csv_files = glob.glob("/content/*.csv")

if not csv_files:
    st.error("CSV file not found. Please upload the dataset to Colab.")
    st.stop()

df = pd.read_csv(csv_files[0])

# Clean text fields
df["Town"] = df["Town"].astype(str).str.strip()

# Create readable Area names from refArea
def clean_area(url):
    area = str(url).split("/page/")[-1]

    # Remove common suffixes
    area = area.replace("_Governorate", "")
    area = area.replace("_", " ")

    # Fix district/resource URLs
    if "resource/" in area:
        area = area.split("resource/")[-1]

    # Clean encoding issues
    replacements = {
        "â": "-",
        "Ã©": "é",
        "Ã": "A"
    }

    for old, new in replacements.items():
        area = area.replace(old, new)

    return area.strip()

df["Area"] = df["refArea"].apply(clean_area)

# --------------------------------------------------
# TITLE AND CONTEXT
# --------------------------------------------------

st.title("🌍 Lebanon Tourism Data Explorer")

st.markdown(
    """
    This interactive dashboard explores tourism patterns across Lebanese areas
    and towns using the Lebanon Tourism dataset.

    The visualizations focus on two questions:
    - How does the average Tourism Index vary across areas?
    - How is the number of restaurants related to the Tourism Index?
    """
)

st.divider()

# --------------------------------------------------
# INTERACTION 1: AREA
# --------------------------------------------------

st.subheader("🔎 Explore the Data")

areas = sorted(df["Area"].dropna().unique())

selected_area = st.selectbox(
    "Select an area:",
    areas,
    index=0
)

# --------------------------------------------------
# INTERACTION 2: TOWN
# Linked to Area selection
# --------------------------------------------------

area_data = df[df["Area"] == selected_area].copy()

towns = sorted(area_data["Town"].dropna().unique())

selected_towns = st.multiselect(
    "Select town(s):",
    towns,
    default=towns[:min(5, len(towns))]
)

# If no towns are selected, use all towns in the selected area
if selected_towns:
    filtered_data = area_data[
        area_data["Town"].isin(selected_towns)
    ].copy()
else:
    filtered_data = area_data.copy()

# --------------------------------------------------
# DESIGN JUSTIFICATION 1
# --------------------------------------------------

with st.expander("Why use an Area dropdown?"):
    st.write(
        """
        The Area dropdown helps the user answer the question:
        “How does tourism vary across different areas?”

        A dropdown was chosen instead of displaying every area at once
        because it reduces clutter and allows the user to focus on one
        area at a time. This supports the course concept of focusing
        attention by limiting the amount of information shown at once.
        """
    )

# --------------------------------------------------
# DESIGN JUSTIFICATION 2
# --------------------------------------------------

with st.expander("Why use a linked Town multiselect?"):
    st.write(
        """
        The Town multiselect helps the user answer the question:
        “Which towns within this area should I examine more closely?”

        A multiselect was chosen because it allows users to compare
        several towns without forcing them to examine every town
        individually. The options are linked to the Area selection,
        which reduces clutter and supports drill-down analysis.
        """
    )

st.divider()

# --------------------------------------------------
# KEY INSIGHTS
# --------------------------------------------------

st.subheader("💡 Key Insights")

col1, col2 = st.columns(2)

with col1:
    st.info(
        """
        **Area-level insight**

        The Tourism Index varies considerably across the areas in the
        dataset. In the original analysis, Tripoli District had the
        highest average Tourism Index, while Beqaa had the lowest.
        """
    )

with col2:
    st.info(
        """
        **Restaurant insight**

        The original analysis found a positive relationship between the
        number of restaurants and the Tourism Index. Towns with more
        restaurants generally tend to have higher Tourism Index values,
        although restaurants alone do not completely explain the index.
        """
    )

st.divider()

# --------------------------------------------------
# VISUALIZATION 1
# --------------------------------------------------

st.subheader("📊 Average Tourism Index by Area")

# Calculate averages across the full dataset
area_summary = (
    df.groupby("Area", as_index=False)["Tourism Index"]
    .mean()
    .sort_values("Tourism Index", ascending=False)
)

# Highlight the selected area
fig1 = px.bar(
    area_summary,
    x="Area",
    y="Tourism Index",
    title="Average Tourism Index Across Areas",
    labels={
        "Area": "Area",
        "Tourism Index": "Average Tourism Index"
    },
    hover_data={
        "Tourism Index": ":.2f"
    }
)

fig1.update_layout(
    xaxis_tickangle=-45,
    height=500
)

st.plotly_chart(fig1, use_container_width=True)

# --------------------------------------------------
# VISUALIZATION 2
# --------------------------------------------------

st.subheader(
    f"🍽️ Restaurants and Tourism Index — {selected_area}"
)

if len(filtered_data) > 0:

    fig2 = px.scatter(
        filtered_data,
        x="Total number of restaurants",
        y="Tourism Index",
        hover_name="Town",
        size="Total number of restaurants",
        title=f"Restaurants vs. Tourism Index in {selected_area}",
        labels={
            "Total number of restaurants": "Number of Restaurants",
            "Tourism Index": "Tourism Index"
        }
    )

    fig2.update_layout(height=500)

    st.plotly_chart(fig2, use_container_width=True)

else:

    st.warning("Please select at least one town to display the visualization.")

# --------------------------------------------------
# SELECTED DATA SUMMARY
# --------------------------------------------------

st.divider()

st.subheader("📋 Selected Data Summary")

col1, col2, col3 = st.columns(3)

with col1:
    st.metric(
        "Selected Area",
        selected_area
    )

with col2:
    st.metric(
        "Towns Selected",
        len(selected_towns) if selected_towns else len(towns)
    )

with col3:
    st.metric(
        "Average Tourism Index",
        f"{filtered_data['Tourism Index'].mean():.2f}"
        if len(filtered_data) > 0
        else "N/A"
    )

st.caption(
    "Source: Lebanon Tourism dataset used in the Data Visualization assignment."
)
