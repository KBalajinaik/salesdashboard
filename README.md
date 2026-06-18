# Enterprise Sales Analysis Dashboard 📊

Welcome to the **Enterprise Sales Analysis Dashboard** project! This project has been built from scratch as a professional-grade Business Intelligence (BI) tool. It handles data engineering (generating synthetic data), data cleaning (addressing duplicate values, missing records, data validation, and outliers), and full-stack dashboard implementation (using Streamlit and interactive charts).

Whether you are an expert data analyst or a beginner Data Science student, this document will guide you through the folder structure, execution, installation, deployment, and explain **every single line of code** in simple language.

---

## 📂 Project Folder Structure
Here is how our project files are organized inside the `sales_dashboard/` directory:

```
sales_dashboard/
│
├── data/
│   ├── generate_data.py     # Generates raw sales data with built-in imperfections
│   ├── clean_data.py        # Cleans raw data and saves it to CSV & SQLite DB
│   ├── sales_raw.csv        # Generated raw dataset (10,000+ rows) [AUTO-GENERATED]
│   ├── sales_clean.csv      # Generated clean dataset (11,003 rows) [AUTO-GENERATED]
│   └── sales.db             # Local SQLite database of cleaned sales data [AUTO-GENERATED]
│
├── dashboard/
│   ├── kpis.py              # Logic for computing business metrics (sales, profit, growth)
│   └── plots.py             # Custom Plotly, Matplotlib, and Seaborn visualizations
│
├── assets/
│   └── style.css            # Custom CSS style for premium fonts and hover KPI cards
│
├── reports/                 # Directory reserved for downloaded/exported summary reports
│
├── app.py                   # Main Streamlit web application (entry point)
├── requirements.txt         # List of external Python dependencies
└── README.md                # This study guide and project documentation
```

---

## ⚙️ Installation Guide

Follow these steps to set up the environment and run the application on your computer:

### Prerequisites
1. **Python**: Ensure you have Python 3.8 or higher installed on your computer.
2. **Terminal/Command Prompt**: Open PowerShell, Command Prompt, or terminal.

### Step 1: Clone or Copy the Files
Place all folders (`data`, `dashboard`, `assets`, `reports`) and files (`app.py`, `requirements.txt`, `README.md`) into a directory of your choice, for example: `C:\web development\sales_dashboard`.

### Step 2: Install Dependencies
To install all required libraries, navigate to your directory in the terminal and run:
```bash
pip install -r requirements.txt
```
*Note: If you have the `uv` tool installed, you can execute commands faster using `uv pip install -r requirements.txt`.*

---

## 🚀 Execution Guide

You can run the dashboard with a single command! Streamlit will automatically detect that the database is missing, run the data pipeline (generation and cleaning) for you, and start the app:

```bash
streamlit run app.py
```

If you prefer to run the steps manually:
1. **Generate Raw Data**:
   ```bash
   python data/generate_data.py
   ```
2. **Clean Data & Load to SQLite**:
   ```bash
   python data/clean_data.py
   ```
3. **Launch Dashboard**:
   ```bash
   streamlit run app.py
   ```

---

## 🌐 Deployment Guide

### Deploying to Streamlit Community Cloud (Free & Easy)
1. **Upload to GitHub**: Push this entire project folder to a GitHub repository (e.g. `yourname/sales-analysis-dashboard`). Make sure `requirements.txt` is in the root directory.
2. **Sign In**: Go to [Streamlit Share](https://share.streamlit.io/) and log in with your GitHub account.
3. **Deploy App**:
   - Click "New App".
   - Select your repository (`yourname/sales-analysis-dashboard`), branch (`main`), and main file path (`app.py`).
   - Click **Deploy**.
Streamlit will provision a server, install dependencies from `requirements.txt`, compile your synthetic data, and launch your dashboard live on the web!

---

## 📖 Line-by-Line Code Explanations

Here is a simple, student-friendly explanation of how every file and every line of code works:

---

### 1. `requirements.txt`
[requirements.txt](file:///c:/web/development/sales_dashboard/requirements.txt) lists all the external libraries we need to install:
- **`streamlit`**: The framework used to build the interactive web dashboard.
- **`pandas`**: The core data analysis library used to load, clean, and manipulate tabular data.
- **`numpy`**: A library for numerical calculations.
- **`plotly`**: A library for drawing modern, interactive charts.
- **`matplotlib` & `seaborn`**: Libraries used to generate static charts like the correlation matrix.
- **`openpyxl`**: Allows Python to read and write Excel files.

---

### 2. `data/generate_data.py`
[generate_data.py](file:///c:/web/development/sales_dashboard/data/generate_data.py) creates our dataset. Here is how it works under the hood:

- **Lines 1-10**: Import required libraries: `random` and `numpy` for generating numbers, `pandas` for handling datasets, and `datetime`/`timedelta` to work with dates.
- **Lines 12-14**: Set seed values: `np.random.seed(42)` ensures that every time we run the script, we get the exact same random values. This is called reproducibility.
- **Lines 16-104 (Product Catalog & Geo Rules)**: We define product pricing profiles. For example, a laptop has a price of $1200 and a cost ratio of 0.75 (meaning the cost to manufacture is 75% of the sales price, i.e., $900). We also map US Regions to States, and States to Cities.
- **Lines 105-135 (Temporal Rules)**: We model seasonality factors. Q4 (November & December) has a multiplier of 1.3 to 1.6 to simulate holiday shopping peaks. We also simulate ~15% yearly business growth from 2023 to 2026.
- **Lines 136-192 (Loop to Generate Records)**:
  - We loop `11,000` times. In each loop, we randomly pick a date, a customer, and a product.
  - We calculate:
    - `Sales = Unit_Price * Quantity * (1 - Discount)` (Revenue generated).
    - `Cost = Unit_Cost * Quantity` (What the business spent).
    - `Profit = Sales - Cost` (Earnings).
- **Lines 195-225 (Injecting Faulty Data)**: To prove our data cleaning script works, we intentionally break some data:
  - We duplicate 1.5% of the rows using `df.loc[]` and `pd.concat()`.
  - We inject `NaN` (null/empty values) into names, quantities, discounts, and payment methods.
  - We inject massive outlier prices (e.g. multiplying a price by 10 to make a $10 printer cost $100).
- **Lines 226-237**: Save the messy data to `data/sales_raw.csv`.

---

### 3. `data/clean_data.py`
[clean_data.py](file:///c:/web/development/sales_dashboard/data/clean_data.py) cleans the raw CSV file and populates the SQLite database:

- **Lines 18-20**: Load the raw dataset from `data/sales_raw.csv`.
- **Lines 23-41 (Handling Missing Values)**:
  - `df["Customer_Name"].fillna("Unknown Customer")`: Replaces empty customer names with a default fallback.
  - `df["Quantity"].fillna(1)`: If quantity is blank, we assume they bought 1.
  - `df["Discount"].fillna(0.0)`: Empty discounts are replaced with 0.
  - `df["Payment_Mode"].fillna(mode)`: Empty payment modes are filled with the most common payment method (the "mode").
- **Lines 43-46 (Drop Duplicates)**:
  - `df.drop_duplicates()`: Finds identical rows and keeps only one, throwing away duplicates.
- **Lines 48-60 (Type Casting)**:
  - `pd.to_datetime(df["Order_Date"])`: Converts date strings into Python datetime objects, allowing chronological sorting.
  - `df["Quantity"].astype(int)` and other lines convert the text/floats to correct computer representations.
- **Lines 62-85 (Outlier Correction)**:
  - We use the **Interquartile Range (IQR)** method grouped by product subcategory.
  - IQR is calculated as: `IQR = Q3 - Q1` (the middle 50% of the data).
  - Any price above `Q3 + 3.0 * IQR` is identified as an extreme outlier.
  - We overwrite outlier prices with the median price for that subcategory using `df.loc[]`.
- **Lines 87-109 (Metric Validation)**:
  - Since we changed quantities, discounts, and prices, the arithmetic calculations might be broken.
  - We recalculate: `Sales = Unit_Price * Quantity * (1 - Discount)` and `Profit = Sales - Cost` for all rows to guarantee 100% database integrity.
- **Lines 111-135 (Load to SQLite)**:
  - `sqlite3.connect("data/sales.db")`: Creates a local SQLite database file.
  - `df_sql.to_sql("sales", conn, ...)`: Automatically creates a database table named `sales` and inserts all rows.
  - `CREATE INDEX`: Creates database indexes on `Order_Date`, `Region`, and `Category` to make SQL queries run super fast in the future.

---

### 4. `dashboard/kpis.py`
[kpis.py](file:///c:/web/development/sales_dashboard/dashboard/kpis.py) computes key statistics:

- **Lines 11-28**: Basic aggregations:
  - `Sales.sum()` for Total Sales.
  - `Order_ID.nunique()` for unique orders.
  - `Profit.sum()` for Total Profit.
  - `Customer_ID.nunique()` for active customer count.
- **Lines 31-70 (Period-over-Period Growth)**:
  - Dynamically finds the duration of the current filter (e.g. 30 days).
  - Finds the start/end dates of the preceding period of the exact same length (e.g. the 30 days before that).
  - Calculates the sales in that prior period.
  - Growth Rate is computed as: `((Current Sales - Prior Sales) / Prior Sales) * 100`.

---

### 5. `dashboard/plots.py`
[plots.py](file:///c:/web/development/sales_dashboard/dashboard/plots.py) creates interactive Plotly and Seaborn visual graphs:

- **Lines 14-29 (Theme Configuration)**:
  - We set a professional Indigo and Emerald color palette.
- **Lines 31-60 (`apply_layout_theme`)**:
  - Automatically configures styling: transparent backgrounds, neat fonts (Inter & Outfit), grid lines, and custom legends.
- **Lines 64-94 (Monthly Trends)**:
  - `go.Scatter(..., fill='tozeroy')`: Draws filled Area charts for monthly sales and profit trends.
- **Lines 119-142 (Top Products)**:
  - `px.bar(..., orientation='h')`: Generates horizontal bar charts. We sort in reverse order using `iloc[::-1]` so the best-performing item sits at the very top.
- **Lines 144-173 (Categories)**:
  - `px.pie(..., hole=0.4)`: Draws a donut chart showing category distribution.
- **Lines 177-226 (Customers & Pareto)**:
  - Plots top customers and draws a Pareto 80/20 Contribution line. It shows what percentage of total sales is driven by what percentage of customers.
- **Lines 281-314 (Profit Margin Scatter)**:
  - Draws a scatter plot where the X-axis is Sales, Y-axis is Profit, and color represents Discount Rate. It clearly shows how higher discounts pull profits down into negative numbers.
- **Lines 347-378 (`plot_correlation_heatmap`)**:
  - Uses `seaborn.heatmap` on numerical columns.
  - `io.BytesIO()`: Saves the Matplotlib chart into a virtual computer memory buffer rather than saving a file to the hard drive, and returns it so Streamlit can draw it.

---

### 6. `assets/style.css`
[style.css](file:///c:/web/development/sales_dashboard/assets/style.css) injects premium styling:

- **Line 4**: Imports the clean fonts **Inter** and **Outfit** from Google Fonts.
- **Lines 16-37 (`.kpi-card`)**:
  - Designs rounded corners (`border-radius: 12px`).
  - Adds shadows (`box-shadow`) and smooth animation transitions (`transition: all 0.3s`).
  - `.kpi-card:hover`: Moves the cards up slightly (`translateY(-4px)`) and turns the border indigo when you hover over them with your mouse.
- **Lines 63-79**: Includes a media query (`@media prefers-color-scheme: dark`) to automatically change background cards to a slate-gray when users run Streamlit in Dark Mode.

---

### 7. `app.py`
[app.py](file:///c:/web/development/sales_dashboard/app.py) links everything together into a Streamlit web interface:

- **Lines 32-37**: Sets the page title to "Enterprise Sales Analysis Dashboard" and uses wide-mode layout.
- **Lines 40-54 (local_css)**: Reads our `style.css` file and writes it into the webpage inside `<style>` tags.
- **Lines 57-81 (load_data_from_db)**:
  - `@st.cache_data`: Caches the database load. This means Streamlit will load the data from SQLite once and save it in memory. It won't re-read the database files every time you click a button, making the app run 10x faster.
  - If database is missing, it runs the generation and cleaning scripts automatically.
- **Lines 93-138 (Sidebar Filter Panel)**:
  - `st.sidebar.multiselect()` and `st.sidebar.date_input()` create side widgets.
  - State filter changes dynamically based on the selected regions (`df[df["Region"].isin(selected_regions)]["State"]`).
- **Lines 141-172 (Applying Filters)**:
  - Filters the dataset step-by-step using Python Boolean masks (e.g. `filtered_df[filtered_df["Region"].isin(selected_regions)]`).
- **Lines 185-197 (`render_kpi_card`)**:
  - Standardizes the layout of metric cards by writing inline HTML that matches the styles in `style.css`.
- **Lines 201-314 (Tab/Menu Navigation)**:
  - Uses `if menu_selection == "Executive Summary":` and similar checks to dynamically show the correct charts and tabs for the requested section.
- **Lines 318-361 (Exports & Downloads)**:
  - `filtered_df.to_csv()`: Converts the currently filtered table to a CSV string.
  - `st.download_button`: Allows business owners to download the filtered table as a `.csv` file or download a Markdown performance report summarizing all calculated KPIs.

---

## 🎓 Summary of Learnings for Students
By reviewing this project, you will learn:
1. **Data Pipeline Architecture**: How raw data flows from a raw generator into a cleaning and validation pipeline, and then into an SQLite database.
2. **Database Integration**: How to query tables using Python and set database indexes for faster lookup.
3. **Interactive Visualizations**: How to implement dynamic Plotly charts that respond to user filters.
4. **Professional UI Customization**: How to override default Streamlit themes with custom CSS to build a premium visual experience.
