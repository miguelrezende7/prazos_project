
  
    

    create or replace table `prazos-project`.`prazos_trusted`.`tj_api_data_transformed`
      
    
    

    OPTIONS()
    as (
      WITH latest_data AS (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY city, year, date, type ORDER BY timestamp DESC) AS row_num
    FROM `prazos-project`.`prazos_trusted`.`tj_api_data`
)

SELECT *
FROM latest_data
WHERE row_num = 1
    );
  