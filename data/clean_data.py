"""
clean_data.py
-------------
This script performs data cleaning and validation on the raw sales dataset.
Steps:
1. Load raw data from CSV.
2. Handle missing values (impute names, set default discounts/quantities, fill payment mode).
3. Remove duplicate records.
4. Correct data types (dates to datetime, quantities to integer, prices/sales to float).
5. Detect and correct price outliers (using subcategory-based IQR).
6. Validate financial consistency (recalculate Sales, Cost, and Profit to ensure arithmetic integrity).
7. Save the clean dataset back to CSV and export it to an SQLite database (sales.db).
"""

import os
import sqlite3
import pandas as pd
import numpy as np

def clean_and_validate_data(raw_csv_path="data/sales_raw.csv", clean_csv_path="data/sales_clean.csv", db_path="data/sales.db"):
    print(f"Loading raw dataset from '{raw_csv_path}'...")
    if not os.path.exists(raw_csv_path):
        raise FileNotFoundError(f"Raw file {raw_csv_path} not found. Please run generate_data.py first.")
        
    df = pd.read_csv(raw_csv_path)
    initial_shape = df.shape
    print(f"Loaded {initial_shape[0]} rows and {initial_shape[1]} columns.")
    
    # --- 1. Handle Missing Values ---
    print("\n[Step 1] Handling missing values...")
    
    # Customer_Name: fill missing with 'Unknown Customer'
    cust_null_count = df["Customer_Name"].isnull().sum()
    df["Customer_Name"] = df["Customer_Name"].fillna("Unknown Customer")
    
    # Quantity: fill missing with median or 1 (we'll use 1 as it represents a transaction)
    qty_null_count = df["Quantity"].isnull().sum()
    df["Quantity"] = df["Quantity"].fillna(1)
    
    # Discount: fill missing with 0.0
    discount_null_count = df["Discount"].isnull().sum()
    df["Discount"] = df["Discount"].fillna(0.0)
    
    # Payment_Mode: fill missing with mode (most frequent payment mode)
    mode_payment = df["Payment_Mode"].mode()[0] if not df["Payment_Mode"].mode().empty else "Credit Card"
    payment_null_count = df["Payment_Mode"].isnull().sum()
    df["Payment_Mode"] = df["Payment_Mode"].fillna(mode_payment)
    
    print(f" - Customer_Name: filled {cust_null_count} nulls with 'Unknown Customer'")
    print(f" - Quantity: filled {qty_null_count} nulls with 1")
    print(f" - Discount: filled {discount_null_count} nulls with 0.0")
    print(f" - Payment_Mode: filled {payment_null_count} nulls with '{mode_payment}'")

    # --- 2. Remove Duplicate Records ---
    print("\n[Step 2] Removing duplicate records...")
    dup_count = df.duplicated().sum()
    df = df.drop_duplicates().reset_index(drop=True)
    print(f" - Removed {dup_count} duplicate rows. Current row count: {len(df)}")

    # --- 3. Data Type Correction ---
    print("\n[Step 3] Correcting data types...")
    # Convert Order_Date to datetime
    df["Order_Date"] = pd.to_datetime(df["Order_Date"], errors='coerce')
    # If any date parsing failed, drop those rows or fill them
    date_nulls = df["Order_Date"].isnull().sum()
    if date_nulls > 0:
        df = df.dropna(subset=["Order_Date"]).reset_index(drop=True)
        print(f" - Dropped {date_nulls} rows due to invalid dates.")
        
    # Standardize numerical columns
    df["Quantity"] = df["Quantity"].astype(int)
    df["Unit_Price"] = df["Unit_Price"].astype(float)
    df["Sales"] = df["Sales"].astype(float)
    df["Cost"] = df["Cost"].astype(float)
    df["Profit"] = df["Profit"].astype(float)
    df["Discount"] = df["Discount"].astype(float)
    
    print(" - Data types converted successfully.")

    # --- 4. Outlier Detection and Correction ---
    print("\n[Step 4] Outlier detection and correction...")
    # Outliers in Unit_Price: Let's compute IQR for each Sub_Category
    # and cap prices that exceed Q3 + 3 * IQR (extremely high outliers)
    corrected_outliers = 0
    
    for subcat in df["Sub_Category"].unique():
        subcat_mask = df["Sub_Category"] == subcat
        subcat_df = df[subcat_mask]
        
        q1 = subcat_df["Unit_Price"].quantile(0.25)
        q3 = subcat_df["Unit_Price"].quantile(0.75)
        iqr = q3 - q1
        
        # Calculate upper bound. Use 3 * IQR to capture only egregious pricing errors
        upper_bound = q3 + 3.0 * iqr
        
        # If there are items above the upper bound, replace their Unit_Price with the subcategory median
        outlier_mask = subcat_mask & (df["Unit_Price"] > upper_bound)
        outlier_count = outlier_mask.sum()
        
        if outlier_count > 0:
            median_price = subcat_df["Unit_Price"].median()
            df.loc[outlier_mask, "Unit_Price"] = median_price
            corrected_outliers += outlier_count
            
    print(f" - Corrected {corrected_outliers} extreme Unit_Price outliers by replacing them with subcategory median prices.")

    # --- 5. Data Validation & Financial Consistency Recalculation ---
    print("\n[Step 5] Recalculating metrics for financial consistency...")
    # Because we filled missing values (Quantity/Discount) and corrected outliers (Unit_Price),
    # we must ensure that Sales, Cost, and Profit columns are arithmetically sound.
    # We will assume Cost is a product of Quantity and Unit_Cost. Since we don't have Unit_Cost directly in the df,
    # let's estimate it. Typically, Cost / Quantity gives Unit_Cost. Let's clean that:
    # Estimate Cost ratio = Cost / Sales before changes (median per subcategory), or use existing Cost/Quantity.
    # Let's compute:
    # For any row, if the cost ratio is broken or missing, we use the median cost ratio of that subcategory.
    df["Temp_Cost_Ratio"] = df["Cost"] / (df["Unit_Price"] * df["Quantity"])
    df["Temp_Cost_Ratio"] = df["Temp_Cost_Ratio"].replace([np.inf, -np.inf], np.nan).fillna(0.6) # fallback
    
    # Group by subcategory to find median cost ratio
    cost_ratios = df.groupby("Sub_Category")["Temp_Cost_Ratio"].transform("median")
    
    # Recalculate Sales
    df["Sales"] = np.round((df["Unit_Price"] * df["Quantity"]) * (1.0 - df["Discount"]), 2)
    # Recalculate Cost based on the median cost ratio of the subcategory
    df["Cost"] = np.round((df["Unit_Price"] * cost_ratios) * df["Quantity"], 2)
    # Recalculate Profit
    df["Profit"] = np.round(df["Sales"] - df["Cost"], 2)
    
    # Drop temp column
    df = df.drop(columns=["Temp_Cost_Ratio"])
    
    # Validation constraints checks:
    # 1. Quantity must be >= 1
    df.loc[df["Quantity"] < 1, "Quantity"] = 1
    # 2. Discount must be between 0 and 0.8
    df.loc[df["Discount"] < 0, "Discount"] = 0.0
    df.loc[df["Discount"] > 0.8, "Discount"] = 0.8
    
    print(" - Financial rules validated and columns synced: Sales = Unit_Price * Quantity * (1 - Discount), Profit = Sales - Cost.")

    # --- 6. Save Outputs ---
    print("\n[Step 6] Saving cleaned data...")
    # Save CSV
    df.to_csv(clean_csv_path, index=False)
    print(f" - Cleaned CSV saved to '{clean_csv_path}' (Shape: {df.shape})")
    
    # Save to SQLite Database
    print(f" - Loading data into SQLite database at '{db_path}'...")
    conn = sqlite3.connect(db_path)
    
    # Write dataframe to SQL. Overwrite table if exists.
    df_sql = df.copy()
    # SQLite doesn't support datetime directly, so convert date to string for database consistency
    df_sql["Order_Date"] = df_sql["Order_Date"].dt.strftime("%Y-%m-%d")
    
    df_sql.to_sql("sales", conn, if_exists="replace", index=False)
    
    # Create indexes for optimized lookup speeds
    cursor = conn.cursor()
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_order_date ON sales(Order_Date);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_region ON sales(Region);")
    cursor.execute("CREATE INDEX IF NOT EXISTS idx_category ON sales(Category);")
    conn.commit()
    conn.close()
    print(" - SQLite load complete with indexes (table: 'sales').")
    
    print("\nData cleaning pipeline finished successfully!")
    return clean_csv_path, db_path

if __name__ == "__main__":
    clean_and_validate_data()
