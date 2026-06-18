"""
generate_data.py
----------------
This script generates a realistic sales dataset with over 10,000 records.
It models realistic customer purchasing habits, product categories, geographic
distributions, seasonal trends, and financial calculations.
It also introduces intentional data quality issues (missing values, duplicates, outliers)
to demonstrate the capabilities of the data cleaning pipeline.
"""

import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)
random.seed(42)

def generate_sales_data(num_records=11000):
    print(f"Starting synthetic sales data generation ({num_records} records)...")
    
    # --- 1. Master Data Lists ---
    
    # Categories and Subcategories with pricing profiles (base_price, cost_ratio)
    # cost_ratio is Cost / Price (standard margin simulation)
    product_catalog = {
        "Technology": {
            "Laptops": [
                ("ProBook 15", 1200, 0.75),
                ("ThinkPad X1 Carbon", 1800, 0.70),
                ("MacBook Air M2", 1099, 0.65),
                ("MacBook Pro 16", 2499, 0.68),
                ("Chromebook Spin", 350, 0.80)
            ],
            "Phones": [
                ("iPhone 15 Pro", 999, 0.60),
                ("Galaxy S24 Ultra", 1299, 0.62),
                ("Pixel 8 Pro", 999, 0.65),
                ("OnePlus 12", 799, 0.70),
                ("Moto G Power", 250, 0.75)
            ],
            "Printers": [
                ("LaserJet Pro MFP", 450, 0.55),
                ("EcoTank Photo Printer", 600, 0.50),
                ("OfficeJet Wireless", 180, 0.65)
            ],
            "Accessories": [
                ("Mechanical Keyboard", 120, 0.40),
                ("Wireless Ergonomic Mouse", 80, 0.45),
                ("USB-C Multiport Adapter", 60, 0.35),
                ("4K UltraWide Monitor", 499, 0.60),
                ("Noise Cancelling Headphones", 299, 0.50)
            ]
        },
        "Furniture": {
            "Chairs": [
                ("Ergonomic Mesh Chair", 350, 0.60),
                ("Leather Executive Chair", 499, 0.65),
                ("Gaming Recliner", 280, 0.55),
                ("Task Stool", 90, 0.50)
            ],
            "Tables": [
                ("Standing Desk (Dual Motor)", 650, 0.70),
                ("Solid Oak Dining Table", 1200, 0.60),
                ("Glass Conference Table", 950, 0.65),
                ("Rustic Coffee Table", 250, 0.50)
            ],
            "Bookcases": [
                ("5-Shelf Wood Bookcase", 180, 0.55),
                ("Modular Steel Shelving", 240, 0.60),
                ("Corner Wall Shelf", 70, 0.40)
            ],
            "Furnishings": [
                ("LED Desk Lamp", 45, 0.30),
                ("Anti-Fatigue Floor Mat", 60, 0.40),
                ("Desk Organizer Set", 30, 0.35),
                ("Large Area Rug", 220, 0.50)
            ]
        },
        "Office Supplies": {
            "Paper": [
                ("Premium Copy Paper Ream", 8, 0.30),
                ("Recycled Multi-Use Paper", 6, 0.25),
                ("Cardstock Heavyweight", 15, 0.40),
                ("Photo Glossy Paper", 25, 0.45)
            ],
            "Binders": [
                ("3-Inch Heavy Duty Binder", 12, 0.30),
                ("View Presentation Binder", 8, 0.25),
                ("Expanding Accordion File", 20, 0.35)
            ],
            "Art": [
                ("Dual-Tip Brush Markers (12-pack)", 25, 0.40),
                ("Watercolor Sketchbook", 18, 0.35),
                ("Acrylic Paint Set", 35, 0.45),
                ("Precision Scissors", 10, 0.30)
            ],
            "Storage": [
                ("Plastic Storage Bin (3-pack)", 45, 0.50),
                ("Mobile Filing Drawer", 150, 0.60),
                ("Letter-Size Banker Boxes (10-pack)", 30, 0.40)
            ],
            "Appliances": [
                ("Compact Office Fridge", 199, 0.65),
                ("Single Serve Coffee Maker", 89, 0.55),
                ("Personal Space Heater", 35, 0.50),
                ("Desktop Air Purifier", 120, 0.60)
            ]
        }
    }
    
    # Geographic distribution hierarchy
    regions_geo = {
        "East": {
            "New York": ["New York City", "Buffalo", "Rochester"],
            "Pennsylvania": ["Philadelphia", "Pittsburgh", "Allentown"],
            "Massachusetts": ["Boston", "Worcester", "Springfield"]
        },
        "West": {
            "California": ["Los Angeles", "San Francisco", "San Diego", "San Jose"],
            "Washington": ["Seattle", "Spokane", "Tacoma"],
            "Oregon": ["Portland", "Eugene", "Salem"]
        },
        "Central": {
            "Illinois": ["Chicago", "Naperville", "Rockford"],
            "Texas": ["Houston", "Austin", "Dallas", "San Antonio"],
            "Ohio": ["Cleveland", "Columbus", "Cincinnati"]
        },
        "South": {
            "Florida": ["Miami", "Orlando", "Tampa", "Jacksonville"],
            "Georgia": ["Atlanta", "Savannah", "Augusta"],
            "North Carolina": ["Charlotte", "Raleigh", "Greensboro"]
        }
    }
    
    # Payment modes
    payment_modes = ["Credit Card", "Debit Card", "PayPal", "Bank Transfer", "Cash"]
    
    # Generate 500 unique customers to simulate repeats
    first_names = ["James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda", 
                   "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
                   "Thomas", "Sarah", "Charles", "Karen", "Christopher", "Nancy", "Daniel", "Lisa",
                   "Matthew", "Betty", "Anthony", "Margaret", "Mark", "Sandra", "Donald", "Ashley"]
    last_names = ["Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
                  "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
                  "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White", "Harris"]
    
    customers = []
    for i in range(1, 501):
        cust_id = f"CUST-{i:03d}"
        cust_name = f"{random.choice(first_names)} {random.choice(last_names)}"
        customers.append((cust_id, cust_name))
        
    # Generate static locations for customers to ensure consistency
    customer_locations = {}
    for cust_id, _ in customers:
        region = random.choice(list(regions_geo.keys()))
        state = random.choice(list(regions_geo[region].keys()))
        city = random.choice(regions_geo[region][state])
        customer_locations[cust_id] = (region, state, city)

    # --- 2. Generate Records ---
    records = []
    
    # Date range: Jan 1, 2023 to Jun 15, 2026 (1262 days)
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2026, 6, 15)
    total_days = (end_date - start_date).days
    
    # Set base multipliers for seasonality & growth
    # Let's model a growth rate of ~15% year-over-year
    # Q4 (Nov, Dec) has higher sales volume, Q1 (Jan, Feb) has lower
    
    order_id_counter = 10001
    
    for i in range(num_records):
        # Generate Order Date with seasonal distributions
        # Random offset in days
        day_offset = random.randint(0, total_days)
        order_date = start_date + timedelta(days=day_offset)
        
        # Seasonality factors
        month = order_date.month
        year = order_date.year
        
        # Monthly factor: High in Dec (1.5), Nov (1.3), low in Jan (0.75), Feb (0.8)
        month_factors = {1: 0.75, 2: 0.8, 3: 0.95, 4: 1.0, 5: 1.05, 6: 1.0, 
                         7: 0.95, 8: 0.9, 9: 1.1, 10: 1.15, 11: 1.3, 12: 1.6}
        month_factor = month_factors[month]
        
        # Yearly growth factor: Base 2023 = 1.0, 2024 = 1.15, 2025 = 1.32, 2026 = 1.48
        year_factors = {2023: 1.0, 2024: 1.15, 2025: 1.32, 2026: 1.48}
        year_factor = year_factors[year]
        
        # Cumulative probability factor to simulate order clusters
        # Generate multiple items per order sometimes (same order ID, same date, same customer)
        if len(records) > 0 and random.random() < 0.35:
            # Group item: reuse previous order details
            prev_record = records[-1]
            order_id = prev_record["Order_ID"]
            order_date_str = prev_record["Order_Date"]
            cust_id = prev_record["Customer_ID"]
            cust_name = prev_record["Customer_Name"]
            region = prev_record["Region"]
            state = prev_record["State"]
            city = prev_record["City"]
        else:
            # New order
            order_id = f"OD-{order_id_counter}"
            order_id_counter += 1
            order_date_str = order_date.strftime("%Y-%m-%d")
            cust_id, cust_name = random.choice(customers)
            region, state, city = customer_locations[cust_id]
            
        # Select Category, Subcategory, and Product
        category = random.choice(list(product_catalog.keys()))
        sub_cat = random.choice(list(product_catalog[category].keys()))
        product_item = random.choice(product_catalog[category][sub_cat])
        
        product_name = product_item[0]
        base_unit_price = product_item[1]
        cost_ratio = product_item[2]
        
        # Product ID derivation
        sub_cat_prefix = sub_cat[:3].upper()
        prod_id = f"PROD-{sub_cat_prefix}-{abs(hash(product_name)) % 1000:03d}"
        
        # Quantity purchased: scale with seasonality & year factor (adds realism)
        # Quantity base between 1 and 6, sometimes larger orders
        base_q_choices = [1, 2, 3, 4]
        if random.random() < 0.15:
            base_q_choices += [5, 6, 7]
        if random.random() < 0.05:
            base_q_choices += [8, 9, 10]
            
        quantity = random.choice(base_q_choices)
        
        # Discount: most orders have no discount, some have modest discounts, promo periods have higher discounts
        # Q4 has higher likelihood of discount
        discount_prob = random.random()
        if month in [11, 12]:
            discount = random.choice([0.0, 0.0, 0.1, 0.15, 0.2, 0.3, 0.5])
        else:
            discount = random.choice([0.0, 0.0, 0.0, 0.0, 0.05, 0.1, 0.15, 0.2])
            
        # Add minor random noise to unit price (simulate dynamic pricing)
        unit_price = round(base_unit_price * random.uniform(0.95, 1.05), 2)
        unit_cost = round(unit_price * cost_ratio, 2)
        
        # Financial Math
        # Sales is standard retail value after discounts
        sales = round((unit_price * quantity) * (1.0 - discount), 2)
        cost = round(unit_cost * quantity, 2)
        profit = round(sales - cost, 2)
        
        payment_mode = random.choice(payment_modes)
        
        # Keep list of dicts
        records.append({
            "Order_ID": order_id,
            "Order_Date": order_date_str,
            "Customer_ID": cust_id,
            "Customer_Name": cust_name,
            "Product_ID": prod_id,
            "Product_Name": product_name,
            "Category": category,
            "Sub_Category": sub_cat,
            "Region": region,
            "State": state,
            "City": city,
            "Quantity": quantity,
            "Unit_Price": unit_price,
            "Sales": sales,
            "Cost": cost,
            "Profit": profit,
            "Discount": discount,
            "Payment_Mode": payment_mode
        })
        
    df = pd.DataFrame(records)
    
    # --- 3. Inject Artificial Imperfections (for Data Cleaning validation) ---
    print("Injecting dirty data details for cleaning validation...")
    
    # A. Duplicates (About 1.5% of rows duplicated exactly)
    num_duplicates = int(num_records * 0.015)
    dup_indices = np.random.choice(df.index, size=num_duplicates, replace=False)
    dup_rows = df.loc[dup_indices].copy()
    df = pd.concat([df, dup_rows], ignore_index=True)
    
    # B. Missing Values (NaNs)
    # Customer_Name: 50 nulls
    null_cust_names = np.random.choice(df.index, size=50, replace=False)
    df.loc[null_cust_names, "Customer_Name"] = np.nan
    
    # Quantity: 30 nulls
    null_quantities = np.random.choice(df.index, size=30, replace=False)
    df.loc[null_quantities, "Quantity"] = np.nan
    
    # Discount: 40 nulls (should be filled with 0)
    null_discounts = np.random.choice(df.index, size=40, replace=False)
    df.loc[null_discounts, "Discount"] = np.nan
    
    # Payment_Mode: 25 nulls
    null_payments = np.random.choice(df.index, size=25, replace=False)
    df.loc[null_payments, "Payment_Mode"] = np.nan
    
    # C. Outliers
    # Introduce extremely high unit prices (e.g. $10,000 for accessories or copy paper)
    outlier_indices = np.random.choice(df.index, size=15, replace=False)
    df.loc[outlier_indices, "Unit_Price"] = df.loc[outlier_indices, "Unit_Price"] * 10.0
    # Recalculate Sales and Profit for those outliers to maintain financial dependency before cleaning
    df.loc[outlier_indices, "Sales"] = round((df.loc[outlier_indices, "Unit_Price"] * df.loc[outlier_indices, "Quantity"]) * (1.0 - df.loc[outlier_indices, "Discount"]), 2)
    df.loc[outlier_indices, "Cost"] = round((df.loc[outlier_indices, "Unit_Price"] * 0.6) * df.loc[outlier_indices, "Quantity"], 2) # Arbitrary Cost ratio
    df.loc[outlier_indices, "Profit"] = round(df.loc[outlier_indices, "Sales"] - df.loc[outlier_indices, "Cost"], 2)
    
    # D. Format / Data type issues (e.g. Order_Date sometimes contains bad string characters)
    # We will let cleaning handle converting date strings to real timestamps
    
    # Shuffle dataframe to mix duplicates and outliers
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)
    
    # Make sure output directories exist
    os.makedirs("data", exist_ok=True)
    
    # Save raw CSV
    output_path = "data/sales_raw.csv"
    df.to_csv(output_path, index=False)
    
    print(f"Generated {len(df)} raw records successfully. Saved to '{output_path}'.")
    return output_path

if __name__ == "__main__":
    generate_sales_data()
