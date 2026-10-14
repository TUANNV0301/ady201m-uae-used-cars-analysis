-- Q1: mean listing price and sample size by make (joined dimension)
SELECT m.make_name, COUNT(*) AS listings,
       ROUND(AVG(c.price_aed), 2) AS average_price_aed
FROM car_listing AS c
JOIN make AS m ON m.make_id = c.make_id
GROUP BY m.make_name
HAVING COUNT(*) >= 50
ORDER BY average_price_aed DESC;

-- Q2: distribution by body type
SELECT b.body_type_name, COUNT(*) AS listings,
       ROUND(AVG(c.price_aed), 2) AS average_price_aed
FROM car_listing AS c
JOIN body_type AS b ON b.body_type_id = c.body_type_id
GROUP BY b.body_type_name
ORDER BY listings DESC;

-- Q3: median is computed in Python after grouping; SQL provides ordered price rows.
SELECT e.emirate_name, c.price_aed
FROM car_listing AS c
JOIN emirate AS e ON e.emirate_id = c.emirate_id
ORDER BY e.emirate_name, c.price_aed;

-- Q4: asking prices across year and mileage bands
SELECT year,
       CASE WHEN mileage_km < 50000 THEN '<50k'
            WHEN mileage_km < 100000 THEN '50k-99k'
            WHEN mileage_km < 200000 THEN '100k-199k'
            ELSE '200k+' END AS mileage_band,
       COUNT(*) AS listings,
       ROUND(AVG(price_aed), 2) AS average_price_aed
FROM car_listing
GROUP BY year, mileage_band
HAVING COUNT(*) >= 10
ORDER BY year, mileage_band;
