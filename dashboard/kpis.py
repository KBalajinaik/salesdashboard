"""
kpis.py
-------
This helper module calculates the Key Performance Indicators (KPIs) for the dashboard.
It supports period-over-period comparison to determine growth rates dynamically based on the active filters.
"""

import pandas as pd
import numpy as np

def calculate_kpi_metrics(df, full_df=None):
    """
    Calculates the 8 core KPIs for the given dataframe.
    If full_df is provided, calculates period-over-period growth compared to the preceding period.
    """
    # 1. Total Sales (Revenue)
    total_sales = float(df["Sales"].sum()) if not df.empty else 0.0
    
    # 2. Total Revenue (in our schema, Revenue = Sales)
    total_revenue = total_sales
    
    # 3. Total Orders
    total_orders = int(df["Order_ID"].nunique()) if not df.empty else 0
    
    # 4. Total Profit
    total_profit = float(df["Profit"].sum()) if not df.empty else 0.0
    
    # 5. Profit Margin
    profit_margin = (total_profit / total_sales * 100) if total_sales > 0 else 0.0
    
    # 6. Average Order Value (AOV)
    # Total revenue divided by number of unique orders
    aov = (total_revenue / total_orders) if total_orders > 0 else 0.0
    
    # 7. Number of Customers
    num_customers = int(df["Customer_ID"].nunique()) if not df.empty else 0
    
    # 8. Growth Rate % (Period-over-Period)
    # We compare sales in the filtered dataframe against sales in the previous equal-length time frame
    growth_rate = 0.0
    
    if full_df is not None and not df.empty and len(df) < len(full_df):
        try:
            # Ensure dates are datetime
            df_dates = pd.to_datetime(df["Order_Date"])
            min_date = df_dates.min()
            max_date = df_dates.max()
            
            period_days = (max_date - min_date).days + 1
            
            # Start and end of the prior period
            prior_end_date = min_date - pd.Timedelta(days=1)
            prior_start_date = prior_end_date - pd.Timedelta(days=period_days - 1)
            
            # Filter the full dataframe for the prior period
            full_dates = pd.to_datetime(full_df["Order_Date"])
            prior_mask = (full_dates >= prior_start_date) & (full_dates <= prior_end_date)
            prior_df = full_df[prior_mask]
            
            prior_sales = float(prior_df["Sales"].sum())
            
            if prior_sales > 0:
                growth_rate = ((total_sales - prior_sales) / prior_sales) * 100
            else:
                growth_rate = 0.0
        except Exception as e:
            # Fallback if date parsing fails
            growth_rate = 0.0
    else:
        # If no full_df or displaying all data, growth rate is calculated year-over-year for the last year
        try:
            df_dates = pd.to_datetime(df["Order_Date"])
            max_year = df_dates.max().year
            
            current_year_sales = df[df_dates.dt.year == max_year]["Sales"].sum()
            prior_year_sales = df[df_dates.dt.year == (max_year - 1)]["Sales"].sum()
            
            if prior_year_sales > 0:
                growth_rate = ((current_year_sales - prior_year_sales) / prior_year_sales) * 100
            else:
                growth_rate = 0.0
        except Exception:
            growth_rate = 0.0

    return {
        "total_revenue": total_revenue,
        "total_sales": total_sales,
        "total_orders": total_orders,
        "total_profit": total_profit,
        "profit_margin": profit_margin,
        "aov": aov,
        "num_customers": num_customers,
        "growth_rate": growth_rate
    }
