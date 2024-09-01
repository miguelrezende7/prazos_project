SELECT 
  city, 
  year, 
  date, 
  count(DISTINCT date) as distinct_dates
  
FROM {{ref('trusted_tj_api_data')}}

GROUP BY
    city,
    year,
    date

HAVING
  distinct_dates > 1
