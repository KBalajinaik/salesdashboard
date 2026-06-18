"""
app.py
------
Main Streamlit application for the Sales Analysis Dashboard.
Loads clean data from SQLite, configures dynamic filtering in the sidebar,
implements the custom CSS design system, renders KPI cards and charts,
and supports advanced export and search features.
"""

import os
import sqlite3
import pandas as pd
import streamlit as st

# Import helpers
from dashboard.kpis import calculate_kpi_metrics
from dashboard.plots import (
    plot_sales_revenue_trend,
    plot_sales_trend_by_period,
    plot_top_products,
    plot_category_sales,
    plot_subcategory_sales,
    plot_top_customers,
    plot_customer_purchase_frequency,
    plot_customer_contribution,
    plot_region_sales,
    plot_state_sales,
    plot_city_sales,
    plot_profit_by_category,
    plot_profit_by_region,
    plot_discount_impact_scatter,
    plot_discount_distribution,
    plot_payment_usage,
    plot_revenue_by_payment,
    plot_correlation_heatmap
)

# --- 1. App Configuration & Setup ---
st.set_page_config(
    page_title="Enterprise Sales Analysis Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Function to load and inject custom CSS
def local_css(file_name):
    if os.path.exists(file_name):
        with open(file_name) as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
    else:
        # Fallback inline CSS if stylesheet file is missing
        st.markdown("""
        <style>
            .kpi-card { background-color: #f8f9fa; border: 1px solid #e9ecef; border-radius: 12px; padding: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.04); }
            .kpi-title { font-size: 0.875rem; color: #6b7280; text-transform: uppercase; }
            .kpi-value { font-size: 1.75rem; font-weight: 700; color: #111827; }
        </style>
        """, unsafe_allow_html=True)

local_css("assets/style.css")

# --- 2. Data Loading (with automatic data generation if database is missing) ---
@st.cache_data(show_spinner="Connecting to database...")
def load_data_from_db():
    db_path = "data/sales.db"
    
    # If the database or clean data is missing, run the scripts automatically
    if not os.path.exists(db_path) or not os.path.exists("data/sales_clean.csv"):
        st.info("Database or cleaned data not found. Initializing data pipeline...")
        from data.generate_data import generate_sales_data
        from data.clean_data import clean_and_validate_data
        
        raw_path = generate_sales_data()
        clean_and_validate_data(raw_path)
        st.success("Data generation and cleaning pipeline complete!")
        
    conn = sqlite3.connect(db_path)
    df = pd.read_sql("SELECT * FROM sales", conn)
    conn.close()
    
    # Cast date back to datetime objects
    df["Order_Date"] = pd.to_datetime(df["Order_Date"])
    return df

try:
    df_raw = load_data_from_db()
except Exception as e:
    st.error(f"Error loading database: {e}")
    st.info("Generating fallback local dataset for display...")
    # Trigger local fallback generation and load
    from data.generate_data import generate_sales_data
    from data.clean_data import clean_and_validate_data
    raw_path = generate_sales_data()
    clean_and_validate_data(raw_path)
    df_raw = load_data_from_db()

# Create a copy for cleaning/filtering operations
full_df = df_raw.copy()

# --- 3. Sidebar Navigation & Layout ---
st.sidebar.markdown("<h2 style='text-align: center; color: #4f46e5; font-family: Outfit;'>📊 Enterprise BI</h2>", unsafe_allow_html=True)
st.sidebar.markdown("---")

st.sidebar.subheader("Navigation")
menu_selection = st.sidebar.radio(
    "Choose Dashboard View",
    options=[
        "Executive Summary",
        "Sales Analysis",
        "Product Analysis",
        "Customer Analysis",
        "Regional Analysis",
        "Profit Analysis",
        "Discount Analysis",
        "Payment Analysis"
    ]
)

st.sidebar.markdown("---")
st.sidebar.subheader("Filter Panel")

# --- 4. Dynamic Interactive Filters ---

# A. Date Filter
min_date = full_df["Order_Date"].min().date()
max_date = full_df["Order_Date"].max().date()
date_range = st.sidebar.date_input(
    "Date Range Selection",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# B. Region Selection
regions = sorted(full_df["Region"].unique())
selected_regions = st.sidebar.multiselect("Select Region(s)", options=regions, default=[])

# C. State Selection (updates dynamically based on selected regions)
if selected_regions:
    available_states = sorted(full_df[full_df["Region"].isin(selected_regions)]["State"].unique())
else:
    available_states = sorted(full_df["State"].unique())
selected_states = st.sidebar.multiselect("Select State(s)", options=available_states, default=[])

# D. Category Selection
categories = sorted(full_df["Category"].unique())
selected_categories = st.sidebar.multiselect("Select Category(s)", options=categories, default=[])

# E. Payment Mode Selection
payment_modes = sorted(full_df["Payment_Mode"].unique())
selected_payments = st.sidebar.multiselect("Select Payment Mode(s)", options=payment_modes, default=[])

# F. Search Query (Global Search Box)
st.sidebar.markdown("---")
st.sidebar.subheader("Search & Analytics")
search_query = st.sidebar.text_input("Search Product / Customer", placeholder="Type keywords...")

# --- 5. Apply Active Filters to DataFrame ---
filtered_df = full_df.copy()

# Date range filtering
if isinstance(date_range, tuple) and len(date_range) == 2:
    start_dt, end_dt = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
    filtered_df = filtered_df[(filtered_df["Order_Date"] >= start_dt) & (filtered_df["Order_Date"] <= end_dt)]

# Region filtering
if selected_regions:
    filtered_df = filtered_df[filtered_df["Region"].isin(selected_regions)]

# State filtering
if selected_states:
    filtered_df = filtered_df[filtered_df["State"].isin(selected_states)]

# Category filtering
if selected_categories:
    filtered_df = filtered_df[filtered_df["Category"].isin(selected_categories)]

# Payment mode filtering
if selected_payments:
    filtered_df = filtered_df[filtered_df["Payment_Mode"].isin(selected_payments)]

# Search box filtering
if search_query:
    query = search_query.lower()
    search_mask = (
        filtered_df["Product_Name"].str.lower().str.contains(query, na=False) |
        filtered_df["Customer_Name"].str.lower().str.contains(query, na=False) |
        filtered_df["Order_ID"].str.lower().str.contains(query, na=False)
    )
    filtered_df = filtered_df[search_mask]

# --- 6. Metrics Calculation (KPIs) ---
kpis = calculate_kpi_metrics(filtered_df, full_df)

def format_inr(value, decimals=2):
    try:
        value = float(value)
    except (TypeError, ValueError):
        value = 0.0

    sign = "-" if value < 0 else ""
    value = abs(value)
    whole_part = int(value)
    decimal_part = value - whole_part
    whole_str = f"{whole_part:,}"

    if "," in whole_str:
        whole_str = whole_str[:-3] + "," + whole_str[-3:]

    return f"{sign}₹{whole_str}.{decimal_part:.{decimals}f}"

# Helper function to render modern KPI cards in columns
def render_kpi_card(title, value, delta_val, suffix=""):
    delta_class = "delta-positive" if delta_val >= 0 else "delta-negative"
    delta_arrow = "▲" if delta_val >= 0 else "▼"
    
    card_html = f"""
    <div class="kpi-card">
        <div class="kpi-title">{title}</div>
        <div class="kpi-value">{value}{suffix}</div>
        <div class="kpi-delta {delta_class}">
            <span>{delta_arrow} {abs(delta_val):.1f}%</span> <span style='color: #6b7280; font-weight: normal; font-size: 0.75rem;'>vs. prior period</span>
        </div>
    </div>
    """
    st.markdown(card_html, unsafe_allow_html=True)

# --- 7. Header and UI Dashboard Sections ---

st.title(f"📊 Sales Analysis Dashboard: {menu_selection}")
st.markdown(f"**Data Coverage:** Selected period contains **{len(filtered_df):,}** records / total transactions.")

# Show Warning if filter returns empty dataset
if filtered_df.empty:
    st.warning("⚠️ No data matches the current selected filters. Please adjust your filters in the sidebar.")
else:
    # Render KPIs at the top of the dashboard pages
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    kpi_col5, kpi_col6, kpi_col7, kpi_col8 = st.columns(4)
    
    with kpi_col1:
        render_kpi_card("Total Sales (Revenue)", format_inr(kpis['total_sales']), kpis['growth_rate'])
    with kpi_col2:
        render_kpi_card("Total Revenue", format_inr(kpis['total_revenue']), kpis['growth_rate'])
    with kpi_col3:
        render_kpi_card("Total Profit", format_inr(kpis['total_profit']), kpis['growth_rate'])
    with kpi_col4:
        # Profit Margin doesn't have a direct YoY growth, so we display it absolute
        render_kpi_card("Profit Margin", f"{kpis['profit_margin']:.1f}", kpis['growth_rate'], suffix="%")
    with kpi_col5:
        render_kpi_card("Total Orders", f"{kpis['total_orders']:,}", kpis['growth_rate'])
    with kpi_col6:
        render_kpi_card("Average Order Value", format_inr(kpis['aov']), kpis['growth_rate'])
    with kpi_col7:
        render_kpi_card("Unique Customers", f"{kpis['num_customers']:,}", kpis['growth_rate'])
    with kpi_col8:
        # Growth Rate itself
        render_kpi_card("Period Growth Rate", f"{kpis['growth_rate']:.1f}", kpis['growth_rate'], suffix="%")

    st.markdown("---")

    # SECTION 1: Executive Summary
    if menu_selection == "Executive Summary":
        col_summary_1, col_summary_2 = st.columns([2, 1])
        with col_summary_1:
            st.plotly_chart(plot_sales_revenue_trend(filtered_df), use_container_width=True)
        with col_summary_2:
            st.markdown("### Executive Summary Analytics")
            st.markdown(f"""
            **Key Insights from the Selected Dataset:**
            - **Sales Performance:** Total revenue stands at **{format_inr(kpis['total_sales'])}** with an overall net profit of **{format_inr(kpis['total_profit'])}**, operating at a **{kpis['profit_margin']:.1f}%** profit margin.
            - **Order Volume:** Business owners processed **{kpis['total_orders']:,}** unique orders with an average value of **{format_inr(kpis['aov'])}** per basket.
            - **Customer Retention:** The business served **{kpis['num_customers']:,}** distinct buyers over the period.
            """)
            
            # Show numerical correlation matrix heatmap (Seaborn requirement)
            st.markdown("#### Operational Correlation Matrix")
            heatmap_buf = plot_correlation_heatmap(filtered_df)
            st.image(heatmap_buf, caption="Correlation Matrix of Numerical Sales Indicators", width="stretch")

    # SECTION 2: Sales Analysis
    elif menu_selection == "Sales Analysis":
        sales_tab_daily, sales_tab_weekly, sales_tab_monthly, sales_tab_yearly = st.tabs([
            "📅 Daily Trend", "📆 Weekly Trend", "🗓️ Monthly Trend", "📅 Yearly Trend"
        ])
        with sales_tab_daily:
            st.plotly_chart(plot_sales_trend_by_period(filtered_df, 'daily'), use_container_width=True)
        with sales_tab_weekly:
            st.plotly_chart(plot_sales_trend_by_period(filtered_df, 'weekly'), use_container_width=True)
        with sales_tab_monthly:
            st.plotly_chart(plot_sales_trend_by_period(filtered_df, 'monthly'), use_container_width=True)
        with sales_tab_yearly:
            st.plotly_chart(plot_sales_trend_by_period(filtered_df, 'yearly'), use_container_width=True)

    # SECTION 3: Product Analysis
    elif menu_selection == "Product Analysis":
        col_prod_1, col_prod_2 = st.columns(2)
        with col_prod_1:
            st.plotly_chart(plot_top_products(filtered_df, 'Sales', top_n=10, ascending=True), use_container_width=True)
        with col_prod_2:
            st.plotly_chart(plot_top_products(filtered_df, 'Profit', top_n=10, ascending=True), use_container_width=True)
            
        col_prod_3, col_prod_4 = st.columns(2)
        with col_prod_3:
            st.plotly_chart(plot_top_products(filtered_df, 'Sales', top_n=10, ascending=False), use_container_width=True)
        with col_prod_4:
            st.plotly_chart(plot_category_sales(filtered_df), use_container_width=True)
            
        st.plotly_chart(plot_subcategory_sales(filtered_df), use_container_width=True)

    # SECTION 4: Customer Analysis
    elif menu_selection == "Customer Analysis":
        col_cust_1, col_cust_2 = st.columns(2)
        with col_cust_1:
            st.plotly_chart(plot_top_customers(filtered_df), use_container_width=True)
        with col_cust_2:
            st.plotly_chart(plot_customer_purchase_frequency(filtered_df), use_container_width=True)
            
        st.plotly_chart(plot_customer_contribution(filtered_df), use_container_width=True)

    # SECTION 5: Regional Analysis
    elif menu_selection == "Regional Analysis":
        col_reg_1, col_reg_2 = st.columns(2)
        with col_reg_1:
            st.plotly_chart(plot_region_sales(filtered_df), use_container_width=True)
        with col_reg_2:
            st.plotly_chart(plot_state_sales(filtered_df), use_container_width=True)
            
        st.plotly_chart(plot_city_sales(filtered_df), use_container_width=True)

    # SECTION 6: Profit Analysis
    elif menu_selection == "Profit Analysis":
        col_prof_1, col_prof_2 = st.columns(2)
        with col_prof_1:
            st.plotly_chart(plot_profit_by_category(filtered_df), use_container_width=True)
        with col_prof_2:
            st.plotly_chart(plot_profit_by_region(filtered_df), use_container_width=True)

    # SECTION 7: Discount Analysis
    elif menu_selection == "Discount Analysis":
        col_disc_1, col_disc_2 = st.columns(2)
        with col_disc_1:
            st.plotly_chart(plot_discount_impact_scatter(filtered_df), use_container_width=True)
        with col_disc_2:
            st.plotly_chart(plot_discount_distribution(filtered_df), use_container_width=True)

    # SECTION 8: Payment Analysis
    elif menu_selection == "Payment Analysis":
        col_pay_1, col_pay_2 = st.columns(2)
        with col_pay_1:
            st.plotly_chart(plot_payment_usage(filtered_df), use_container_width=True)
        with col_pay_2:
            st.plotly_chart(plot_revenue_by_payment(filtered_df), use_container_width=True)

    # --- 8. Exporting & Report Generation Panel ---
    st.markdown("---")
    st.subheader("📥 Export & Report Controls")
    
    exp_col1, exp_col2 = st.columns(2)
    
    with exp_col1:
        st.markdown("**Export Current View Filtered Dataset**")
        csv_data = filtered_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="💾 Download Filtered Data as CSV",
            data=csv_data,
            file_name="sales_filtered_export.csv",
            mime="text/csv"
        )
        
    with exp_col2:
        st.markdown("**Download Business Performance Summary Report**")
        # Build a markdown report based on current filters and KPIs
        report_md = f"""# Sales Performance Executive Report
Generated on: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive KPI Metrics
- **Total Revenue (Sales):** {format_inr(kpis['total_sales'])}
- **Total Net Profit:** {format_inr(kpis['total_profit'])}
- **Profit Margin:** {kpis['profit_margin']:.2f}%
- **Total Orders Placed:** {kpis['total_orders']:,}
- **Average Order Value:** {format_inr(kpis['aov'])}
- **Active Customers:** {kpis['num_customers']:,}
- **Growth Performance (Period-over-Period):** {kpis['growth_rate']:.2f}%

## Filter Context Applied
- Date Range: {date_range}
- Selected Regions: {selected_regions if selected_regions else 'All Regions'}
- Selected Categories: {selected_categories if selected_categories else 'All Categories'}
- Search Keywords: "{search_query if search_query else 'None'}"

## Business Overview Remarks
The sales pipeline yielded a total revenue of {format_inr(kpis['total_sales'])} over the audited timeframe. 
The average order size was {format_inr(kpis['aov'])} and operations achieved a net margin of {kpis['profit_margin']:.2f}%. 

Report generated by Enterprise BI Sales Analysis Dashboard.
"""
        st.download_button(
            label="📄 Download Summary Report (Markdown)",
            data=report_md,
            file_name="Sales_Summary_Report.md",
            mime="text/markdown"
        )
