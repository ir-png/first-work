import streamlit as st
import pandas as pd
import altair as alt

# ==========================================
# 1. PAGE SETUP & CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="VastSurvive Analytics",
    page_icon="",
    layout="wide"
)

st.title("VastSurvive Data Analytics Dashboard")
st.markdown("---")

# ==========================================
# 2. LOAD & CHRONOLOGICALLY SORT DATASET
# ==========================================
# FIXED: Relative path ensures it works both locally and deployed on the cloud
file_path = "vastsurvive.xlsx"

@st.cache_data
def load_data():
    df = pd.read_excel(file_path)
    df.columns = df.columns.str.strip()
    
    # Target the first column (the date/reporting period column)
    date_col_name = df.columns[0]
    df[date_col_name] = df[date_col_name].astype(str).str.strip()
    
    # --- CHRONOLOGICAL SORTING TRICK ---
    # Extract the first number from text like "Days 1-3" or dates to sort chronologically
    df['sort_key'] = df[date_col_name].str.extract(r'(\d+)').astype(float)
    df = df.sort_values(by='sort_key', ascending=True).drop(columns=['sort_key'])
    # -----------------------------------
    
    return df, date_col_name

try:
    df, date_col = load_data()
    metrics = ["New users", "materials", "Projects"]

    # ==========================================
    # 3. HIGH-LEVEL KPI HIGHLIGHTS
    # ==========================================
    st.subheader("Platform Performance Summary")
    
    kpi1, kpi2, kpi3 = st.columns(3)
    with kpi1:
        st.metric(label="Total New Users", value=f"{int(df['New users'].sum()):,}")
    with kpi2:
        st.metric(label="Total Materials Uploaded", value=f"{int(df['materials'].sum()):,}")
    with kpi3:
        st.metric(label="Total Projects Uploaded", value=f"{int(df['Projects'].sum()):,}")
        
    st.markdown("---")

    # ==========================================
    # 4. INTERACTIVE CHRONOLOGICAL BAR CHART
    # ==========================================
    st.subheader("Trend Timelines Across Intervals")
    
    selected_metric = st.selectbox(
        "Select a specific metric to visualize tracking growth:", 
        options=metrics
    )
    
    chart_data = df[[date_col, selected_metric]]
    
    # Base chart encoding mapping the X and Y coordinates
    # CUSTOMIZATION: labelAngle=-90 rotates labels to be completely vertical
    base_chart = alt.Chart(chart_data).encode(
        x=alt.X(f"{date_col}:N", title="Reporting Period", axis=alt.Axis(labelAngle=-90), sort=df[date_col].tolist()),
        y=alt.Y(f"{selected_metric}:Q", title=selected_metric)
    )
    
    # 1. Customizing the Bars (Color, Hover effects)
    bars = base_chart.mark_bar(
        color="#1c83e1",
        cornerRadiusTopLeft=4,
        cornerRadiusTopRight=4
    ).encode(
        tooltip=[date_col, selected_metric]
    )
    
    # 2. Customizing Data Numbers on Top of Bars
    text_labels = base_chart.mark_text(
        align='center',
        baseline='bottom',
        dy=-5,  # Shifts the text slightly above the bar
        color='#333333',
        fontWeight='bold'
    ).encode(
        text=alt.Text(f"{selected_metric}:Q", format=".0f")
    )
    
    # Layering bars and text labels together
    final_chart = alt.layer(bars, text_labels).properties(
        width="container",
        height=450
    )
    
    st.altair_chart(final_chart, use_container_width=True)

    st.markdown("---")

    # ==========================================
    # 5. BUSINESS INTELLIGENCE MATRICES & EXPORTS
    # ==========================================
    col_left, col_right = st.columns(2)
    
    with col_left:
        st.subheader("Descriptive Statistics Matrix")
        st.dataframe(df[metrics].describe().round(2), use_container_width=True)
        
        if st.button("Export Statistics Summary to Excel"):
            df[metrics].describe().to_excel("vastsurvive_statistics.xlsx")
            st.success("Descriptive statistics exported successfully!")

    with col_right:
        st.subheader("Metric Correlation Analysis")
        correlation = df[metrics].corr()
        st.dataframe(correlation.round(2), use_container_width=True)
        
        if st.button("Export Correlation Matrix to Excel"):
            correlation.to_excel("vastsurvive_correlation.xlsx")
            st.success("Correlation matrix exported successfully!")

    st.markdown("---")

    # ==========================================
    # 6. GRANULAR AUDIT LOG TABLE
    # ==========================================
    st.subheader("Full Historical Reporting Ledger")
    st.markdown("Scroll or sort through rows to audit reporting interval entries:")
    st.dataframe(df, use_container_width=True, hide_index=True)

except Exception as e:
    st.error(f"Failed to load the dataset. Error Details: {e}")
