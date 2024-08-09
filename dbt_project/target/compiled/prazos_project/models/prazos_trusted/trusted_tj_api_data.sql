

WITH latest_data AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY city, year, date, type ORDER BY timestamp DESC) AS row_num
    FROM `prazos-project`.`prazos_raw`.`tj_api_data`
)

SELECT
    * EXCEPT(row_num)
FROM latest_data
WHERE row_num = 1