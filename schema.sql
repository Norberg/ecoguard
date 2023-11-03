CREATE TABLE IF NOT EXISTS node_data (
    id SERIAL PRIMARY KEY,
    node_id INT,
    node_name VARCHAR(255),
    func VARCHAR(50),
    unit VARCHAR(50),
    utl VARCHAR(50),
    timestamp TIMESTAMP WITHOUT TIME ZONE,
    value FLOAT,
    CONSTRAINT idx_unique_node_data UNIQUE (node_id, node_name, func, unit, utl, timestamp)
);

CREATE TABLE IF NOT EXISTS billing_data (
    id SERIAL PRIMARY KEY,
    billing_name VARCHAR(64) NOT NULL,
    start_date TIMESTAMP NOT NULL,
    end_date TIMESTAMP NOT NULL,
    part_name VARCHAR(64) NOT NULL,
    quantity DECIMAL NOT NULL,
    quantity_unit VARCHAR(10) NOT NULL,
    total_cost_with_vat DECIMAL NOT NULL,
    rate_with_vat DECIMAL NOT NULL,
    CONSTRAINT unique_start_date_part_name UNIQUE (start_date, part_name)
);

CREATE OR REPLACE VIEW node_data_with_cost AS
WITH latest_rate AS (
    SELECT 
        bd.part_name,
        bd.rate_with_vat,
        bd.start_date
    FROM 
        billing_data bd
    WHERE 
        bd.start_date = (SELECT MAX(bd2.start_date) 
                         FROM billing_data bd2 
                         WHERE bd2.part_name = bd.part_name AND bd2.start_date <= CURRENT_DATE)
)
SELECT 
    nd.id,
    nd.func,
    nd.unit,
    nd.utl,
    nd.timestamp,
    nd.value,
    lr.rate_with_vat AS cost_rate,
    nd.value * lr.rate_with_vat AS total_cost
FROM 
    node_data nd
    LEFT JOIN latest_rate lr ON lr.part_name = CASE 
                                                 WHEN nd.utl = 'ELEC' THEN 'Elenergi'
                                                 WHEN nd.utl = 'HW' THEN 'Varmvatten'
                                                 WHEN nd.utl = 'CW' THEN 'Kallvatten'
                                               END;


CREATE OR REPLACE VIEW monthly_aggregated_data AS
SELECT
    DATE_TRUNC('month', ndwc.timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'CET') AS period,
    ndwc.func,
    ndwc.unit,
    ndwc.utl,
    CASE 
        WHEN ndwc.func = 'val' THEN AVG(ndwc.value)
        ELSE SUM(ndwc.value)
    END AS aggregated_value,
    AVG(ndwc.cost_rate) AS avg_cost_rate,
    SUM(ndwc.total_cost) AS total_monthly_cost
FROM 
    node_data_with_cost ndwc
GROUP BY
    period,
    ndwc.func,
    ndwc.unit,
    ndwc.utl
ORDER BY 
    period DESC;


CREATE OR REPLACE VIEW weekly_aggregated_data AS
SELECT
    DATE_TRUNC('week', ndwc.timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'CET') AS period,
    ndwc.func,
    ndwc.unit,
    ndwc.utl,
    CASE 
        WHEN ndwc.func = 'val' THEN AVG(ndwc.value)
        ELSE SUM(ndwc.value)
    END AS aggregated_value,
    AVG(ndwc.cost_rate) AS avg_cost_rate,
    SUM(ndwc.total_cost) AS total_weekly_cost
FROM 
    node_data_with_cost ndwc
GROUP BY
    period,
    ndwc.func,
    ndwc.unit,
    ndwc.utl
ORDER BY 
    period DESC;


CREATE OR REPLACE VIEW daily_aggregated_data AS
SELECT
    DATE_TRUNC('day', ndwc.timestamp AT TIME ZONE 'UTC' AT TIME ZONE 'CET') AS period,
    ndwc.func,
    ndwc.unit,
    ndwc.utl,
    CASE 
        WHEN ndwc.func = 'val' THEN AVG(ndwc.value)
        ELSE SUM(ndwc.value)
    END AS aggregated_value,
    AVG(ndwc.cost_rate) AS avg_cost_rate,
    SUM(ndwc.total_cost) AS total_daily_cost
FROM 
    node_data_with_cost ndwc
GROUP BY
    period,
    ndwc.func,
    ndwc.unit,
    ndwc.utl
ORDER BY 
    period DESC;


