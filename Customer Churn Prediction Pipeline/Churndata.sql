-- ============================================================
-- QUESTION 1: What percentage of customers leave the company?
-- ============================================================

SELECT
    Churn_Label,
    COUNT(*) AS total_customers,
    ROUND(
        COUNT(*) * 100.0 /
        SUM(COUNT(*)) OVER (),
        2
    ) AS churn_percentage
FROM churn_telco
GROUP BY Churn_Label;


-- ============================================================
-- QUESTION 2: Does contract type affect whether customers churn?
-- ============================================================

SELECT
    Contract,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Churn_Label = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(
        SUM(CASE WHEN Churn_Label = 'Yes' THEN 1 ELSE 0 END) * 100.0 /
        COUNT(*),
        2
    ) AS churn_rate
FROM churn_telco
GROUP BY Contract
ORDER BY churn_rate DESC;


-- ============================================================
-- QUESTION 3: Does internet service affect whether customers churn?
-- ============================================================

SELECT
    Internet_Service,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Churn_Label = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(
        SUM(CASE WHEN Churn_Label = 'Yes' THEN 1 ELSE 0 END) * 100.0 /
        COUNT(*),
        2
    ) AS churn_rate
FROM churn_telco
GROUP BY Internet_Service
ORDER BY churn_rate DESC;


-- ============================================================
-- QUESTION 4: Does payment method affect whether customers churn?
-- ============================================================

SELECT
    Payment_Method,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Churn_Label = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(
        SUM(CASE WHEN Churn_Label = 'Yes' THEN 1 ELSE 0 END) * 100.0 /
        COUNT(*),
        2
    ) AS churn_rate
FROM churn_telco
GROUP BY Payment_Method
ORDER BY churn_rate DESC;


-- ============================================================
-- QUESTION 5: Do churned customers pay more each month?
-- ============================================================

SELECT
    Churn_Label,
    ROUND(AVG(Monthly_Charges), 2) AS average_monthly_charge
FROM churn_telco
GROUP BY Churn_Label;


-- ============================================================
-- QUESTION 6: Do customers who stay longer churn less?
-- ============================================================

SELECT
    Churn_Label,
    ROUND(AVG(Tenure_Months), 2) AS average_tenure
FROM churn_telco
GROUP BY Churn_Label;


-- ============================================================
-- QUESTION 7: Are senior citizens more likely to churn?
-- ============================================================

SELECT
    Senior_Citizen,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Churn_Label = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(
        SUM(CASE WHEN Churn_Label = 'Yes' THEN 1 ELSE 0 END) * 100.0 /
        COUNT(*),
        2
    ) AS churn_rate
FROM churn_telco
GROUP BY Senior_Citizen
ORDER BY churn_rate DESC;


-- ============================================================
-- QUESTION 8: Does having a partner reduce churn?
-- ============================================================

SELECT
    Partner,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Churn_Label = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(
        SUM(CASE WHEN Churn_Label = 'Yes' THEN 1 ELSE 0 END) * 100.0 /
        COUNT(*),
        2
    ) AS churn_rate
FROM churn_telco
GROUP BY Partner;


-- ============================================================
-- QUESTION 9: Does having dependents affect customer retention?
-- ============================================================

SELECT
    Dependents,
    COUNT(*) AS total_customers,
    SUM(CASE WHEN Churn_Label = 'Yes' THEN 1 ELSE 0 END) AS churned_customers,
    ROUND(
        SUM(CASE WHEN Churn_Label = 'Yes' THEN 1 ELSE 0 END) * 100.0 /
        COUNT(*),
        2
    ) AS churn_rate
FROM churn_telco
GROUP BY Dependents;


-- ============================================================
-- QUESTION 10: Why are customers leaving?
-- ============================================================

SELECT
    Churn_Reason,
    COUNT(*) AS total_customers
FROM churn_telco
WHERE Churn_Label = 'Yes'
GROUP BY Churn_Reason
ORDER BY total_customers DESC;


-- ============================================================
-- QUESTION 11: Are high-value customers churning?
-- ============================================================

SELECT
    Churn_Label,
    ROUND(AVG(CLTV), 2) AS average_cltv
FROM churn_telco
GROUP BY Churn_Label;


-- ============================================================
-- QUESTION 12: How much monthly revenue is associated with
-- churned and retained customers?
-- ============================================================

SELECT
    Churn_Label,
    ROUND(SUM(Monthly_Charges), 2) AS total_monthly_revenue
FROM churn_telco
GROUP BY Churn_Label;


-- ============================================================
-- QUESTION 13: Who are the highest-paying customers?
-- ============================================================

SELECT
    customer_id,
    Monthly_Charges,
    CLTV
FROM churn_telco
ORDER BY Monthly_Charges DESC
LIMIT 20;


-- ============================================================
-- QUESTION 14: Which customers fit a high-risk profile?
-- ============================================================

SELECT
    customer_id,
    Contract,
    Internet_Service,
    Payment_Method,
    Monthly_Charges,
    Tenure_Months
FROM churn_telco
WHERE Contract = 'Month-to-month'
  AND Internet_Service = 'Fiber optic'
  AND Payment_Method = 'Electronic check';
