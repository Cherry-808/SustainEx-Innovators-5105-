DELETE FROM users
WHERE index_name LIKE '%reference%'
   OR index_name LIKE '%page_number%';

-- Remove duplicates while keeping only the first occurrence of each combination of index_name, index_value, Company Report Name, and Year
WITH CTE AS (
    SELECT 
        index_name, 
        index_value, 
        `Company Report Name`, 
        Year, 
        ROW_NUMBER() OVER (PARTITION BY index_name, index_value, `Company Report Name`, Year ORDER BY index_name) AS row_num
    FROM users
)
DELETE FROM users
WHERE index_name IN (
    SELECT index_name
    FROM CTE
    WHERE row_num > 1
);

-- Drop NULL values in index_value
SELECT * 
FROM users
WHERE index_value IS NOT NULL;

-- Remove rows where index_value is not numeric
SELECT * 
FROM users
WHERE index_value LIKE '^[0-9]+$';



