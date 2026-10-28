-- ============================================================================
-- Retail Sales & Customer Performance Analysis
-- Author: Babli
-- Tech Stack: MySQL / PostgreSQL / SQLite
-- Description: Database schema and business intelligence queries for retail analytics
-- ============================================================================

-- 1. Table Creation
CREATE TABLE IF NOT EXISTS retail_sales (
    Order_ID VARCHAR(20) PRIMARY KEY,
    Order_Date DATE NOT NULL,
    Customer_ID VARCHAR(20) NOT NULL,
    Region VARCHAR(50) NOT NULL,
    Product_Category VARCHAR(50) NOT NULL,
    Product_Name VARCHAR(100) NOT NULL,
    Quantity INT NOT NULL,
    Unit_Price DECIMAL(10, 2) NOT NULL,
    Discount_Amount DECIMAL(10, 2) DEFAULT 0.00,
    Total_Revenue DECIMAL(10, 2) NOT NULL,
    Payment_Method VARCHAR(50) NOT NULL
);

-- ============================================================================
-- BUSINESS INTELLIGENCE & ANALYTICAL QUERIES
-- ============================================================================

-- ----------------------------------------------------------------------------
-- Query 1: Overall Business KPIs (Total Revenue, Total Orders, Units, and AOV)
-- Business Objective: Executive overview of retail performance
-- ----------------------------------------------------------------------------
SELECT 
    COUNT(Order_ID) AS Total_Orders,
    COUNT(DISTINCT Customer_ID) AS Total_Unique_Customers,
    SUM(Quantity) AS Total_Units_Sold,
    ROUND(SUM(Total_Revenue), 2) AS Total_Revenue_INR,
    ROUND(AVG(Total_Revenue), 2) AS Average_Order_Value_INR
FROM retail_sales;


-- ----------------------------------------------------------------------------
-- Query 2: Monthly Revenue Trends and Order Volumes
-- Business Objective: Identify seasonal peaks, slow months, and growth patterns
-- ----------------------------------------------------------------------------
SELECT 
    strftime('%Y-%m', Order_Date) AS Sales_Month, -- For MySQL: DATE_FORMAT(Order_Date, '%Y-%m')
    COUNT(Order_ID) AS Total_Orders,
    SUM(Quantity) AS Units_Sold,
    ROUND(SUM(Total_Revenue), 2) AS Monthly_Revenue_INR,
    ROUND(AVG(Total_Revenue), 2) AS Monthly_AOV_INR
FROM retail_sales
GROUP BY Sales_Month
ORDER BY Sales_Month ASC;


-- ----------------------------------------------------------------------------
-- Query 3: Product Category Performance & Revenue Share
-- Business Objective: Determine top-earning categories to guide marketing budget
-- ----------------------------------------------------------------------------
WITH Category_Totals AS (
    SELECT 
        Product_Category,
        COUNT(Order_ID) AS Orders_Count,
        SUM(Quantity) AS Units_Sold,
        SUM(Total_Revenue) AS Total_Category_Revenue
    FROM retail_sales
    GROUP BY Product_Category
)
SELECT 
    Product_Category,
    Orders_Count,
    Units_Sold,
    ROUND(Total_Category_Revenue, 2) AS Category_Revenue_INR,
    ROUND((Total_Category_Revenue / (SELECT SUM(Total_Revenue) FROM retail_sales)) * 100, 2) AS Revenue_Share_Pct
FROM Category_Totals
ORDER BY Category_Revenue_INR DESC;


-- ----------------------------------------------------------------------------
-- Query 4: Top 10 Best-Selling Products by Revenue
-- Business Objective: Pinpoint star products driving the highest sales
-- ----------------------------------------------------------------------------
SELECT 
    Product_Name,
    Product_Category,
    SUM(Quantity) AS Total_Quantity_Sold,
    ROUND(SUM(Total_Revenue), 2) AS Total_Product_Revenue_INR
FROM retail_sales
GROUP BY Product_Name, Product_Category
ORDER BY Total_Product_Revenue_INR DESC
LIMIT 10;


-- ----------------------------------------------------------------------------
-- Query 5: Regional Sales and Customer Penetration
-- Business Objective: Compare territorial performance and discover regional demand
-- ----------------------------------------------------------------------------
SELECT 
    Region,
    COUNT(DISTINCT Customer_ID) AS Regional_Customers,
    COUNT(Order_ID) AS Total_Orders,
    ROUND(SUM(Total_Revenue), 2) AS Regional_Revenue_INR,
    ROUND(AVG(Total_Revenue), 2) AS Regional_AOV_INR
FROM retail_sales
GROUP BY Region
ORDER BY Regional_Revenue_INR DESC;


-- ----------------------------------------------------------------------------
-- Query 6: Customer Segmentation & Repeat Buyers (Customer Lifetime Value)
-- Business Objective: Identify high-value repeat customers for loyalty initiatives
-- ----------------------------------------------------------------------------
SELECT 
    Customer_ID,
    COUNT(Order_ID) AS Total_Purchases,
    SUM(Quantity) AS Total_Items_Bought,
    ROUND(SUM(Total_Revenue), 2) AS Total_Customer_Spend_INR,
    MIN(Order_Date) AS First_Purchase_Date,
    MAX(Order_Date) AS Last_Purchase_Date
FROM retail_sales
GROUP BY Customer_ID
HAVING COUNT(Order_ID) >= 5
ORDER BY Total_Customer_Spend_INR DESC
LIMIT 15;


-- ----------------------------------------------------------------------------
-- Query 7: Payment Method Preferences
-- Business Objective: Analyze transaction settlement channels to minimize drop-offs
-- ----------------------------------------------------------------------------
SELECT 
    Payment_Method,
    COUNT(Order_ID) AS Transactions_Count,
    ROUND(SUM(Total_Revenue), 2) AS Total_Volume_INR,
    ROUND((COUNT(Order_ID) * 100.0 / (SELECT COUNT(*) FROM retail_sales)), 2) AS Transaction_Share_Pct
FROM retail_sales
GROUP BY Payment_Method
ORDER BY Transactions_Count DESC;
