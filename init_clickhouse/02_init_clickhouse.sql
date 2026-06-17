CREATE DATABASE IF NOT EXISTS rest_staging_area;
CREATE DATABASE IF NOT EXISTS rest_dim_model;
CREATE DATABASE IF NOT EXISTS rest_data_marts;

CREATE TABLE IF NOT EXISTS rest_staging_area.receipts_bronze (
    receipt_id UUID,
    receipt_time DateTime,
    staff_id Nullable(UUID),
    total_price Nullable(Decimal(10, 2)),
    table_id Nullable(Int32),
    client_id Nullable(UUID),
    discount_amount Nullable(Decimal(10, 2)),
    final_price Nullable(Decimal(10, 2)),
    processed_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY toDate(receipt_time)
ORDER BY (toDate(receipt_time), receipt_id);

CREATE TABLE IF NOT EXISTS rest_staging_area.receipt_items_bronze (
    receipt_id UUID,
    receipt_date Date,
    item_id UUID,                  
    quantity Nullable(Int32),       
    price_per_item Nullable(Decimal(10, 2)),      
    total_price Nullable(Decimal(10, 2)),     
    processed_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY receipt_date
ORDER BY (receipt_id, item_id);

CREATE TABLE IF NOT EXISTS rest_staging_area.menu_bronze (
	item_id UUID,
	category Nullable(String),
	dish_name Nullable(String),
	price Nullable(Decimal(10, 2)),
	popularity_weight Nullable(Int32),
	processed_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
ORDER BY item_id;

CREATE TABLE IF NOT EXISTS rest_staging_area.staff_bronze (
	staff_id UUID,
	staff_name Nullable(String),
	staff_position Nullable(String),
	processed_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
ORDER BY staff_id;

CREATE TABLE IF NOT EXISTS rest_dim_model.receipts_silver (
    receipt_id UUID,
    receipt_time DateTime,
    staff_id UUID,
    total_price Decimal(10, 2) DEFAULT 0.00,
    table_id Int32 DEFAULT -1,
    client_id UUID DEFAULT '00000000-0000-0000-0000-000000000000',
    discount_amount Decimal(10, 2) DEFAULT 0.00,
    final_price Decimal(10, 2) DEFAULT 0.00,
    processed_at DateTime DEFAULT now()
) 
ENGINE = ReplacingMergeTree(processed_at)
PARTITION BY toDate(receipt_time)
ORDER BY (toDate(receipt_time), receipt_id);

CREATE TABLE IF NOT EXISTS rest_dim_model.receipt_items_silver (
    receipt_id UUID,
    receipt_date Date,
    item_id UUID,
    quantity Int32 DEFAULT 1,
    price_per_item Decimal(10, 2),
    total_price Decimal(10, 2),
    processed_at DateTime DEFAULT now()
) 
ENGINE = ReplacingMergeTree(processed_at)
PARTITION BY receipt_date
ORDER BY (receipt_id, item_id);

CREATE TABLE IF NOT EXISTS rest_dim_model.menu_silver (
	item_id UUID,
	category String,
	dish_name String,
	price Decimal(10, 2),
	popularity_weight Int32,
	valid_from Date,
	valid_to Date,
	is_current UInt8,
	processed_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
ORDER BY (item_id, valid_from);

CREATE TABLE IF NOT EXISTS rest_dim_model.staff_silver (
	staff_id UUID,
	staff_name String,
	staff_position String,
	valid_from Date,
	valid_to Date,
	is_current UInt8,
	processed_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
ORDER BY (staff_id, valid_from);

CREATE TABLE IF NOT EXISTS rest_data_marts.daily_revenue  (
	report_date Date,
	total_receipts UInt32,
	total_revenue Decimal(15, 2),
	total_discount Decimal(15, 2),
	avg_receipt_value Decimal(15, 2),
	processed_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY report_date
ORDER BY report_date;

CREATE TABLE IF NOT EXISTS rest_data_marts.daily_staff_kpi (
	report_date Date,
	staff_id UUID,
	staff_name String,
	staff_position String,
	receipts_closed UInt32,
	day_revenue Decimal(15, 2),
	avg_receipt_size Decimal(10, 2),
	daily_rank UInt32,
	processed_at DateTime DEFAULT now()
)
ENGINE = MergeTree()
PARTITION BY report_date
ORDER BY (report_date, staff_position, staff_id);

CREATE TABLE IF NOT EXISTS rest_data_marts.analytics_table (
	report_date Date,
	receipt_id UUID,
	receipt_time DateTime,
	items Array(String),
	total_items_count UInt32,
	final_price Decimal(10, 2),
	staff_id UUID,
	staff_name String,
	processed_at DateTime DEFAULT now()	
)
ENGINE = MergeTree()
PARTITION BY report_date
ORDER BY (report_date, receipt_id);