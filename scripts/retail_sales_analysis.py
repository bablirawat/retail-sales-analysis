import os
import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Paths
# Dynamic base path so script works anywhere when cloned
script_dir = os.path.dirname(os.path.abspath(__file__))
base_dir = os.path.dirname(script_dir)
data_path = os.path.join(base_dir, "data", "retail_sales_data.csv")
vis_dir = os.path.join(base_dir, "visualizations")
report_dir = os.path.join(base_dir, "reports")

print("1. Loading dataset...")
df = pd.read_csv(data_path)
print(f"Dataset shape: {df.shape}")

print("\n2. Data Preprocessing & Feature Engineering...")
df["Order_Date"] = pd.to_datetime(df["Order_Date"])
df["Year"] = df["Order_Date"].dt.year
df["Month"] = df["Order_Date"].dt.month
df["Month_Name"] = df["Order_Date"].dt.strftime("%b")
df["Day_Name"] = df["Order_Date"].dt.day_name()

# Check missing values
missing = df.isnull().sum()
print("Missing values per column:\n", missing)

# Core Business Metrics
total_revenue = df["Total_Revenue"].sum()
total_orders = len(df)
total_quantity = df["Quantity"].sum()
aov = total_revenue / total_orders

print("\n--- EXECUTIVE SUMMARY METRICS ---")
print(f"Total Revenue:       INR {total_revenue:,.2f}")
print(f"Total Orders:        {total_orders:,}")
print(f"Total Units Sold:    {total_quantity:,}")
print(f"Average Order Value: INR {aov:,.2f}")

# 3. Monthly Sales Analysis
monthly = df.groupby(["Month", "Month_Name"]).agg(
    Revenue=("Total_Revenue", "sum"),
    Orders=("Order_ID", "count"),
    Units=("Quantity", "sum")
).reset_index().sort_values("Month")

# 4. Category Analysis
category_perf = df.groupby("Product_Category").agg(
    Revenue=("Total_Revenue", "sum"),
    Orders=("Order_ID", "count"),
    Units_Sold=("Quantity", "sum")
).reset_index().sort_values("Revenue", ascending=False)
category_perf["Revenue_Share_%"] = (category_perf["Revenue"] / total_revenue) * 100

# 5. Top 10 Products by Revenue
top_products = df.groupby(["Product_Category", "Product_Name"]).agg(
    Revenue=("Total_Revenue", "sum"),
    Units_Sold=("Quantity", "sum")
).reset_index().sort_values("Revenue", ascending=False).head(10)

# 6. Regional Analysis
regional_perf = df.groupby("Region").agg(
    Revenue=("Total_Revenue", "sum"),
    Orders=("Order_ID", "count")
).reset_index().sort_values("Revenue", ascending=False)

# 7. Visualizations
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b']

# Chart 1: Monthly Sales Trend
fig, ax1 = plt.subplots(figsize=(10, 5))
ax1.plot(monthly["Month_Name"], monthly["Revenue"] / 1000, marker='o', color='#1b4965', linewidth=2.5, markersize=7)
ax1.set_title("Monthly Revenue Trend (2025)", fontsize=14, fontweight='bold', pad=15)
ax1.set_xlabel("Month", fontsize=11, fontweight='bold')
ax1.set_ylabel("Revenue (in Thousands Rs. )", fontsize=11, fontweight='bold')
ax1.grid(True, linestyle='--', alpha=0.6)
for i, txt in enumerate(monthly["Revenue"] / 1000):
    ax1.annotate(f"Rs. {txt:.0f}K", (monthly["Month_Name"].iloc[i], txt + 8), ha='center', fontsize=9)
plt.tight_layout()
plt.savefig(os.path.join(vis_dir, "monthly_sales_trend.png"), dpi=200)
plt.close()
print("Saved monthly_sales_trend.png")

# Chart 2: Category Revenue Breakdown
plt.figure(figsize=(9, 5))
bars = plt.barh(category_perf["Product_Category"], category_perf["Revenue"] / 1000, color='#2b6cb0', edgecolor='black')
plt.title("Revenue by Product Category", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Revenue (in Thousands Rs. )", fontsize=11, fontweight='bold')
plt.gca().invert_yaxis()
for bar in bars:
    w = bar.get_width()
    plt.text(w + 10, bar.get_y() + bar.get_height()/2, f"Rs. {w:.1f}K", va='center', fontsize=9, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(vis_dir, "category_revenue_distribution.png"), dpi=200)
plt.close()
print("Saved category_revenue_distribution.png")

# Chart 3: Regional Revenue Performance
plt.figure(figsize=(8, 5))
bars = plt.bar(regional_perf["Region"], regional_perf["Revenue"] / 1000, color='#319795', edgecolor='black', width=0.55)
plt.title("Sales Revenue by Region", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Region", fontsize=11, fontweight='bold')
plt.ylabel("Revenue (in Thousands Rs. )", fontsize=11, fontweight='bold')
for bar in bars:
    h = bar.get_height()
    plt.text(bar.get_x() + bar.get_width()/2, h + 8, f"Rs. {h:.1f}K", ha='center', fontsize=9, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(vis_dir, "regional_sales_performance.png"), dpi=200)
plt.close()
print("Saved regional_sales_performance.png")

# Chart 4: Top 8 Products by Revenue
top8 = top_products.head(8)
plt.figure(figsize=(10, 5))
bars = plt.barh(top8["Product_Name"], top8["Revenue"] / 1000, color='#dd6b20', edgecolor='black')
plt.title("Top 8 Revenue-Generating Products", fontsize=14, fontweight='bold', pad=15)
plt.xlabel("Revenue (in Thousands Rs. )", fontsize=11, fontweight='bold')
plt.gca().invert_yaxis()
for bar in bars:
    w = bar.get_width()
    plt.text(w + 5, bar.get_y() + bar.get_height()/2, f"Rs. {w:.1f}K", va='center', fontsize=9, fontweight='bold')
plt.tight_layout()
plt.savefig(os.path.join(vis_dir, "top_products_bar_chart.png"), dpi=200)
plt.close()
print("Saved top_products_bar_chart.png")

# 8. Export Excel Summary Report
excel_path = os.path.join(report_dir, "Retail_Sales_Summary_Report.xlsx")
with pd.ExcelWriter(excel_path, engine="openpyxl") as writer:
    monthly.to_excel(writer, sheet_name="Monthly_Trends", index=False)
    category_perf.to_excel(writer, sheet_name="Category_Summary", index=False)
    regional_perf.to_excel(writer, sheet_name="Regional_Summary", index=False)
    top_products.to_excel(writer, sheet_name="Top_Products", index=False)
    df.head(500).to_excel(writer, sheet_name="Sample_Raw_Data", index=False)

print(f"Exported Excel Summary Report to {excel_path}!")

# 9. Test SQLite Database execution for SQL queries
conn = sqlite3.connect(":memory:")
df.to_sql("retail_sales", conn, index=False, if_exists="replace")

sql_test = """
SELECT Product_Category, 
       COUNT(Order_ID) AS Total_Orders,
       SUM(Quantity) AS Total_Units,
       ROUND(SUM(Total_Revenue), 2) AS Category_Revenue
FROM retail_sales
GROUP BY Product_Category
ORDER BY Category_Revenue DESC;
"""
res = pd.read_sql_query(sql_test, conn)
print("\n--- SQL Query Result Sample (Category Summary) ---")
print(res)

conn.close()
print("\nAll Python analyses and visualizations finished successfully!")
