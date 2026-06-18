"""
plots.py
--------
This module contains functions to generate interactive Plotly and Seaborn visualizations.
Each chart is customized with professional color schemes, clean fonts, transparent backgrounds,
and detailed hover tools.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import numpy as np
import io

# Professional corporate color palette
COLORS = {
    'primary': '#4f46e5',     # Indigo
    'secondary': '#06b6d4',   # Cyan
    'success': '#10b981',     # Emerald Green
    'warning': '#f59e0b',     # Amber
    'danger': '#ef4444',      # Rose Red
    'neutral_dark': '#1e293b',# Slate 800
    'neutral_light': '#f8fafc',# Slate 50
    'gray_text': '#6b7280',   # Cool Gray
    'grid': '#e2e8f0',        # Slate 200
    'seq_colors': ['#4f46e5', '#6366f1', '#818cf8', '#a5b4fc', '#c7d2fe', '#e0e7ff'],
    'qual_colors': ['#4f46e5', '#10b981', '#f59e0b', '#ef4444', '#06b6d4', '#8b5cf6', '#ec4899', '#3b82f6']
}

def apply_layout_theme(fig):
    """
    Applies custom styling to Plotly figures for a premium, clean look.
    """
    fig.update_layout(
        font_family="Inter, sans-serif",
        title_font_family="Outfit, sans-serif",
        title_font_size=18,
        title_font_color=COLORS['neutral_dark'],
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent paper
        plot_bgcolor='rgba(0,0,0,0)',   # Transparent plot
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin=dict(t=50, l=40, r=40, b=40)
    )
    fig.update_xaxes(
        showgrid=False,
        linecolor=COLORS['grid'],
        tickfont=dict(color=COLORS['gray_text'])
    )
    fig.update_yaxes(
        showgrid=True,
        gridcolor=COLORS['grid'],
        linecolor=COLORS['grid'],
        tickfont=dict(color=COLORS['gray_text'])
    )
    return fig

# --- 1. Executive Summary & Sales Trends ---

def plot_sales_revenue_trend(df):
    """
    Renders an interactive Area chart showing daily/monthly Sales & Profit.
    """
    # Group by month
    df_temp = df.copy()
    df_temp['Year_Month'] = df_temp['Order_Date'].dt.to_period('M').astype(str)
    monthly_data = df_temp.groupby('Year_Month')[['Sales', 'Profit']].sum().reset_index()
    
    fig = go.Figure()
    # Add Sales Area
    fig.add_trace(go.Scatter(
        x=monthly_data['Year_Month'], y=monthly_data['Sales'],
        mode='lines',
        name='Sales',
        line=dict(color=COLORS['primary'], width=3),
        fill='tozeroy',
        fillcolor='rgba(79, 70, 229, 0.1)'
    ))
    # Add Profit Area
    fig.add_trace(go.Scatter(
        x=monthly_data['Year_Month'], y=monthly_data['Profit'],
        mode='lines',
        name='Profit',
        line=dict(color=COLORS['success'], width=3),
        fill='tozeroy',
        fillcolor='rgba(16, 185, 129, 0.1)'
    ))
    
    fig.update_layout(title_text="Monthly Revenue & Profit Trends")
    return apply_layout_theme(fig)

def plot_sales_trend_by_period(df, period='monthly'):
    """
    Renders Sales trend lines based on Daily, Weekly, Monthly, or Yearly periodicity.
    """
    df_temp = df.copy()
    
    if period == 'daily':
        data = df_temp.groupby('Order_Date')['Sales'].sum().reset_index()
        x_col = 'Order_Date'
        title = "Daily Sales Trend"
    elif period == 'weekly':
        # Group by Week (Year-Week)
        df_temp['Week'] = df_temp['Order_Date'].dt.to_period('W').astype(str)
        data = df_temp.groupby('Week')['Sales'].sum().reset_index()
        x_col = 'Week'
        title = "Weekly Sales Trend"
    elif period == 'monthly':
        df_temp['Month'] = df_temp['Order_Date'].dt.to_period('M').astype(str)
        data = df_temp.groupby('Month')['Sales'].sum().reset_index()
        x_col = 'Month'
        title = "Monthly Sales Trend"
    else:  # yearly
        df_temp['Year'] = df_temp['Order_Date'].dt.year.astype(str)
        data = df_temp.groupby('Year')['Sales'].sum().reset_index()
        x_col = 'Year'
        title = "Yearly Sales Trend"
        
    fig = px.line(data, x=x_col, y='Sales', color_discrete_sequence=[COLORS['primary']])
    fig.update_traces(line=dict(width=3), mode='lines+markers')
    fig.update_layout(title_text=title)
    return apply_layout_theme(fig)

# --- 2. Product Analysis ---

def plot_top_products(df, metric='Sales', top_n=10, ascending=False):
    """
    Renders top products based on Sales (Revenue) or Profit.
    """
    top_products = df.groupby('Product_Name')[metric].sum().reset_index()
    top_products = top_products.sort_values(by=metric, ascending=not ascending).head(top_n)
    
    # Reverse to have the highest value at the top of a horizontal bar chart
    top_products = top_products.iloc[::-1]
    
    color = COLORS['primary'] if metric == 'Sales' else COLORS['success']
    if not ascending: # i.e. worst performing
        color = COLORS['danger']
        
    fig = px.bar(
        top_products, 
        x=metric, 
        y='Product_Name', 
        orientation='h',
        color_discrete_sequence=[color]
    )
    title = f"Top {top_n} Products by {metric}" if ascending else f"Bottom {top_n} Products by {metric}"
    fig.update_layout(title_text=title, margin=dict(l=150))
    return apply_layout_theme(fig)

def plot_category_sales(df):
    """
    Renders a donut chart of Category-wise Sales.
    """
    cat_sales = df.groupby('Category')['Sales'].sum().reset_index()
    fig = px.pie(
        cat_sales, 
        values='Sales', 
        names='Category', 
        hole=0.4,
        color_discrete_sequence=COLORS['qual_colors']
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(title_text="Sales Share by Category")
    return apply_layout_theme(fig)

def plot_subcategory_sales(df):
    """
    Renders a vertical Bar chart of Subcategory-wise Sales.
    """
    sub_sales = df.groupby(['Category', 'Sub_Category'])['Sales'].sum().reset_index()
    sub_sales = sub_sales.sort_values(by='Sales', ascending=False)
    
    fig = px.bar(
        sub_sales, 
        x='Sub_Category', 
        y='Sales', 
        color='Category',
        color_discrete_sequence=COLORS['qual_colors']
    )
    fig.update_layout(title_text="Sales by Product Sub-Category")
    return apply_layout_theme(fig)

# --- 3. Customer Analysis ---

def plot_top_customers(df, top_n=10):
    """
    Renders Top customers by purchase Revenue.
    """
    cust_sales = df.groupby('Customer_Name')[['Sales', 'Quantity']].sum().reset_index()
    cust_sales = cust_sales.sort_values(by='Sales', ascending=False).head(top_n).iloc[::-1]
    
    fig = px.bar(
        cust_sales,
        x='Sales',
        y='Customer_Name',
        orientation='h',
        color='Quantity',
        color_continuous_scale=[[0, '#e0e7ff'], [0.25, '#a5b4fc'], [0.5, '#818cf8'], [0.75, '#6366f1'], [1, '#4f46e5']],
        labels={'Sales': 'Revenue (₹)', 'Quantity': 'Items Bought'}
    )
    fig.update_layout(title_text=f"Top {top_n} Customers by Revenue Contribution")
    return apply_layout_theme(fig)

def plot_customer_purchase_frequency(df):
    """
    Renders customer order frequency (number of orders per customer).
    """
    cust_freq = df.groupby('Customer_Name')['Order_ID'].nunique().reset_index()
    cust_freq.columns = ['Customer_Name', 'Order_Count']
    
    fig = px.histogram(
        cust_freq,
        x='Order_Count',
        nbins=20,
        color_discrete_sequence=[COLORS['secondary']],
        labels={'Order_Count': 'Number of Orders'}
    )
    fig.update_layout(
        title_text="Customer Purchase Frequency (Distribution of Orders per Customer)",
        yaxis_title="Number of Customers"
    )
    return apply_layout_theme(fig)

def plot_customer_contribution(df):
    """
    Renders a Pareto chart / contribution plot of customer revenue.
    """
    cust_contrib = df.groupby('Customer_Name')['Sales'].sum().sort_values(ascending=False).reset_index()
    cust_contrib['Cumulative_Sales'] = cust_contrib['Sales'].cumsum()
    total_sales = cust_contrib['Sales'].sum()
    cust_contrib['Cumulative_Percent'] = (cust_contrib['Cumulative_Sales'] / total_sales) * 100
    cust_contrib['Customer_Percent'] = ((cust_contrib.index + 1) / len(cust_contrib)) * 100
    
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=cust_contrib['Customer_Percent'],
        y=cust_contrib['Cumulative_Percent'],
        mode='lines',
        name='Cumulative Sales %',
        line=dict(color=COLORS['primary'], width=3),
        fill='tozeroy',
        fillcolor='rgba(79, 70, 229, 0.05)'
    ))
    
    # 80/20 rule reference lines
    fig.add_shape(type="line", x0=0, y0=80, x1=100, y1=80, line=dict(color=COLORS['danger'], width=1.5, dash="dash"))
    fig.add_shape(type="line", x0=20, y0=0, x1=20, y1=100, line=dict(color=COLORS['danger'], width=1.5, dash="dash"))
    
    fig.update_layout(
        title_text="Customer Revenue Contribution Curve (80/20 Analysis)",
        xaxis_title="% of Customers (sorted by spend)",
        yaxis_title="% of Total Revenue",
        xaxis_range=[0, 100],
        yaxis_range=[0, 100]
    )
    return apply_layout_theme(fig)

# --- 4. Regional Analysis ---

def plot_region_sales(df):
    """
    Renders Donut chart of Region-wise Sales.
    """
    reg_sales = df.groupby('Region')['Sales'].sum().reset_index()
    fig = px.pie(
        reg_sales,
        values='Sales',
        names='Region',
        hole=0.4,
        color_discrete_sequence=COLORS['qual_colors']
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(title_text="Sales Contribution by Region")
    return apply_layout_theme(fig)

def plot_state_sales(df, top_n=15):
    """
    Renders Top States by Sales.
    """
    state_sales = df.groupby('State')['Sales'].sum().reset_index()
    state_sales = state_sales.sort_values(by='Sales', ascending=False).head(top_n).iloc[::-1]
    
    fig = px.bar(
        state_sales,
        x='Sales',
        y='State',
        orientation='h',
        color_discrete_sequence=[COLORS['primary']]
    )
    fig.update_layout(title_text=f"Top {top_n} States by Sales Volume")
    return apply_layout_theme(fig)

def plot_city_sales(df, top_n=10):
    """
    Renders Top Cities by Sales.
    """
    city_sales = df.groupby(['City', 'State'])['Sales'].sum().reset_index()
    city_sales = city_sales.sort_values(by='Sales', ascending=False).head(top_n)
    
    fig = px.bar(
        city_sales,
        x='City',
        y='Sales',
        color='State',
        color_discrete_sequence=COLORS['qual_colors']
    )
    fig.update_layout(title_text=f"Top {top_n} Cities by Sales Volume")
    return apply_layout_theme(fig)

# --- 5. Profit Analysis ---

def plot_profit_by_category(df):
    """
    Renders Profit and Profit Margin side-by-side per Category.
    """
    cat_profit = df.groupby('Category')[['Sales', 'Profit']].sum().reset_index()
    cat_profit['Profit_Margin'] = (cat_profit['Profit'] / cat_profit['Sales']) * 100
    
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=cat_profit['Category'],
        y=cat_profit['Profit'],
        name='Total Profit (₹)',
        marker_color=COLORS['success'],
        yaxis='y'
    ))
    
    fig.add_trace(go.Scatter(
        x=cat_profit['Category'],
        y=cat_profit['Profit_Margin'],
        name='Profit Margin (%)',
        marker_color=COLORS['primary'],
        line=dict(color=COLORS['primary'], width=3),
        yaxis='y2',
        mode='lines+markers'
    ))
    
    fig.update_layout(
        title_text="Profit vs Margin by Product Category",
        yaxis=dict(title="Total Profit (₹)", side="left"),
        yaxis2=dict(title="Profit Margin (%)", side="right", overlaying="y", range=[0, max(cat_profit['Profit_Margin']) * 1.2])
    )
    return apply_layout_theme(fig)

def plot_profit_by_region(df):
    """
    Renders Grouped Bar chart showing Profit by Region.
    """
    reg_profit = df.groupby(['Region', 'Category'])['Profit'].sum().reset_index()
    fig = px.bar(
        reg_profit,
        x='Region',
        y='Profit',
        color='Category',
        barmode='group',
        color_discrete_sequence=COLORS['qual_colors']
    )
    fig.update_layout(title_text="Profit by Region & Product Category")
    return apply_layout_theme(fig)

# --- 6. Discount Analysis ---

def plot_discount_impact_scatter(df):
    """
    Renders Scatter plot showing Sales vs Profit colored by Discount.
    """
    # Sample down if too large to render smoothly (but 11k is fine for Plotly)
    sample_df = df.sample(n=min(len(df), 2000), random_state=42) if not df.empty else df
    
    fig = px.scatter(
        sample_df,
        x='Sales',
        y='Profit',
        color='Discount',
        size='Quantity',
        color_continuous_scale=px.colors.sequential.RdBu_r,  # Red for discounts (potential profit loss), Blue for high sales
        hover_data=['Product_Name', 'Category'],
        labels={'Discount': 'Discount Rate'}
    )
    fig.update_layout(title_text="Transaction Profitability: Sales vs Profit by Discount Rate")
    return apply_layout_theme(fig)

def plot_discount_distribution(df):
    """
    Renders a bar chart showing the frequency of discount levels applied to transactions.
    """
    disc_data = df.groupby('Discount')['Order_ID'].count().reset_index()
    disc_data.columns = ['Discount_Rate', 'Transaction_Count']
    disc_data['Discount_Rate_Pct'] = (disc_data['Discount_Rate'] * 100).astype(str) + '%'
    
    fig = px.bar(
        disc_data,
        x='Discount_Rate_Pct',
        y='Transaction_Count',
        color_discrete_sequence=[COLORS['warning']],
        labels={'Discount_Rate_Pct': 'Discount Applied (%)', 'Transaction_Count': 'Number of Orders'}
    )
    fig.update_layout(title_text="Distribution of Discounts Applied to Orders")
    return apply_layout_theme(fig)

# --- 7. Payment Analysis ---

def plot_payment_usage(df):
    """
    Renders Donut chart showing Payment Mode share.
    """
    pay_usage = df.groupby('Payment_Mode')['Order_ID'].count().reset_index()
    pay_usage.columns = ['Payment_Mode', 'Order_Count']
    fig = px.pie(
        pay_usage,
        values='Order_Count',
        names='Payment_Mode',
        hole=0.4,
        color_discrete_sequence=COLORS['qual_colors']
    )
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(title_text="Payment Method Usage (Transaction Volume)")
    return apply_layout_theme(fig)

def plot_revenue_by_payment(df):
    """
    Renders vertical Bar chart showing Sales and Profit by Payment Mode.
    """
    pay_rev = df.groupby('Payment_Mode')[['Sales', 'Profit']].sum().reset_index()
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=pay_rev['Payment_Mode'],
        y=pay_rev['Sales'],
        name='Sales Revenue (₹)',
        marker_color=COLORS['primary']
    ))
    fig.add_trace(go.Bar(
        x=pay_rev['Payment_Mode'],
        y=pay_rev['Profit'],
        name='Net Profit (₹)',
        marker_color=COLORS['success']
    ))
    
    fig.update_layout(title_text="Sales and Net Profit by Payment Method", barmode='group')
    return apply_layout_theme(fig)

# --- 8. Seaborn & Matplotlib Heatmap (as required by tech stack) ---

def plot_correlation_heatmap(df):
    """
    Generates a correlation heatmap of numerical columns.
    Attempts to use Seaborn/Matplotlib. If blocked by DLL loading restrictions (like pyexpat),
    falls back to an interactive Plotly heatmap.
    """
    # Select numerical columns
    numeric_df = df[['Quantity', 'Unit_Price', 'Sales', 'Cost', 'Profit', 'Discount']]
    corr_matrix = numeric_df.corr()
    
    try:
        import matplotlib.pyplot as plt
        import seaborn as sns
        
        # Generate plot in a separate figure
        fig, ax = plt.subplots(figsize=(6, 4))
        sns.heatmap(
            corr_matrix, 
            annot=True, 
            cmap='coolwarm', 
            fmt=".2f", 
            linewidths=.5, 
            ax=ax, 
            cbar=True,
            annot_kws={"size": 9}
        )
        plt.title('Correlation Heatmap (Numeric Columns)', fontsize=11, fontweight='bold', pad=10)
        plt.tight_layout()
        
        # Save to buffer
        buf = io.BytesIO()
        plt.savefig(buf, format='png', dpi=300, bbox_inches='tight')
        buf.seek(0)
        plt.close(fig) # close figure to release memory
        return buf
    except (ImportError, Exception):
        # Fallback to Plotly Heatmap
        import plotly.express as px
        fig = px.imshow(
            corr_matrix,
            text_auto=".2f",
            color_continuous_scale="RdBu_r",
            title="Correlation Heatmap (Numeric Columns)",
            labels=dict(color="Correlation")
        )
        fig.update_layout(
            font_family="Inter, sans-serif",
            title_font_family="Outfit, sans-serif",
            title_font_size=16,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            margin=dict(t=40, b=20, l=20, r=20)
        )
        return fig

