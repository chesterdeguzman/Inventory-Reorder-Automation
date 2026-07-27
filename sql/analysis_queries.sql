SELECT sku, ROUND(AVG(units_demanded),2) avg_daily_demand, MAX(lead_time_days) lead_time_days, MAX(current_stock) current_stock FROM inventory_history GROUP BY sku ORDER BY avg_daily_demand DESC;
