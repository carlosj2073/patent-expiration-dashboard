USE Patent_Expiration;

-- Drugs with patents that expire within a year
SELECT trade_name, patent_no, patent_expire_date
FROM patent_product_cleaned
WHERE patent_expire_date BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 12 MONTH)
ORDER BY patent_expire_date;

-- Top 10 companies with upcoming expiration
SELECT applicant_full_name, COUNT(*) AS expiring_patents
FROM patent_product_cleaned
WHERE patent_expire_date < DATE_ADD(CURDATE(), INTERVAL 12 MONTH)
GROUP BY applicant_full_name
ORDER BY expiring_patents DESC
LIMIT 10;

-- Highest Medicare spending among expiring drugs
SELECT 
  UPPER(p.trade_name) AS trade_name, 
  MAX(m.Tot_Spndng_2023) AS total_spending
FROM patent_product_cleaned p
JOIN medicare_part_d m 
  ON UPPER(p.trade_name) = UPPER(m.Brnd_Name)
WHERE p.patent_expire_date < DATE_ADD(CURDATE(), INTERVAL 12 MONTH)
GROUP BY UPPER(p.trade_name)
ORDER BY total_spending DESC
LIMIT 10;

-- Top 10 drugs by CAGR whose patents expire in the next year
SELECT 
  UPPER(p.trade_name) AS trade_name, 
  MAX(m.CAGR_Avg_Spnd_Per_Dsg_Unt_19_23) AS cagr_spending_growth, 
  MIN(p.patent_expire_date) AS earliest_expiration
FROM patent_product_cleaned p
JOIN medicare_part_d m 
  ON UPPER(p.trade_name) = UPPER(m.Brnd_Name)
WHERE p.patent_expire_date < DATE_ADD(CURDATE(), INTERVAL 12 MONTH)
GROUP BY UPPER(p.trade_name)
ORDER BY cagr_spending_growth DESC
LIMIT 10;

-- Drugs in Patent table with no match in medicare data
SELECT DISTINCT trade_name
FROM patent_product_cleaned
WHERE UPPER(trade_name) NOT IN (
    SELECT DISTINCT UPPER(Brnd_Name)
    FROM medicare_part_d
);

-- Monthly distribution of expiring drugs
SELECT 
  YEAR(patent_expire_date) AS expire_year,
  MONTH(patent_expire_date) AS expire_month,
  COUNT(*) AS num_expirations
FROM patent_product_cleaned
WHERE patent_expire_date IS NOT NULL
GROUP BY expire_year, expire_month
ORDER BY expire_year, expire_month;

