-- PostgreSQL schema converted from MySQL
-- Database: catalytics
-- Conversion notes:
-- - AUTO_INCREMENT -> SERIAL
-- - varchar(255) -> VARCHAR(255) 
-- - decimal(x,y) -> NUMERIC(x,y)
-- - float -> REAL
-- - datetime -> TIMESTAMP
-- - date -> DATE
-- - int -> INTEGER
-- - Removed MySQL-specific engine and charset specifications
-- - Converted unique key constraints to PostgreSQL format

--
-- Table structure for table liquidity
--

DROP TABLE IF EXISTS liquidity CASCADE;
CREATE TABLE liquidity (
    record_date DATE,
    account_type VARCHAR(255),
    close_today_bal VARCHAR(255),
    open_today_bal VARCHAR(255),
    open_month_bal VARCHAR(255),
    open_fiscal_year_bal VARCHAR(255),
    table_nbr VARCHAR(255),
    table_nm VARCHAR(255),
    sub_table_name VARCHAR(255),
    src_line_nbr INTEGER,
    record_fiscal_year INTEGER,
    record_fiscal_quarter INTEGER,
    record_calendar_year INTEGER,
    record_calendar_quarter INTEGER,
    record_calendar_month INTEGER,
    record_calendar_day INTEGER,
    record_index VARCHAR(255)
);

--
-- Table structure for table lst
--

DROP TABLE IF EXISTS lst CASCADE;
CREATE TABLE lst (
    id SERIAL PRIMARY KEY,
    address VARCHAR(255),
    name VARCHAR(255),
    symbol VARCHAR(255),
    logoURI VARCHAR(255),
    coingeckoId VARCHAR(255)
);

--
-- Table structure for table lst2
--

DROP TABLE IF EXISTS lst2 CASCADE;
CREATE TABLE lst2 (
    id SERIAL PRIMARY KEY,
    asset_name VARCHAR(255),
    price NUMERIC(15,8),
    timestamp VARCHAR(255)
);

--
-- Table structure for table lst3
--

DROP TABLE IF EXISTS lst3 CASCADE;
CREATE TABLE lst3 (
    id SERIAL PRIMARY KEY,
    asset_name VARCHAR(255),
    price NUMERIC(15,8),
    daily_volume NUMERIC(20,8),
    timestamp VARCHAR(255)
);

--
-- Table structure for table lst4
--

DROP TABLE IF EXISTS lst4 CASCADE;
CREATE TABLE lst4 (
    id SERIAL PRIMARY KEY,
    address VARCHAR(255),
    name VARCHAR(255) UNIQUE,
    symbol VARCHAR(255) UNIQUE,
    logoURI VARCHAR(255),
    coingeckoId VARCHAR(255)
);

--
-- Table structure for table price_data
--

DROP TABLE IF EXISTS price_data CASCADE;
CREATE TABLE price_data (
    date DATE PRIMARY KEY,
    global_liquidity REAL,
    bitcoin_price REAL,
    gold_price REAL
);

--
-- Table structure for table table1
--

DROP TABLE IF EXISTS table1 CASCADE;
CREATE TABLE table1 (
    id SERIAL PRIMARY KEY,
    composite_key VARCHAR(255) UNIQUE NOT NULL,
    coin_name VARCHAR(255) NOT NULL,
    index_name VARCHAR(255) NOT NULL,
    liquidity NUMERIC(38,20),
    market_cap NUMERIC(38,20),
    price NUMERIC(38,20),
    timestamp TIMESTAMP NOT NULL,
    unique_id VARCHAR(255) NOT NULL,
    volume24h NUMERIC(38,20)
);

-- Create indexes for table1
CREATE INDEX idx_table1_index_name ON table1(index_name);
CREATE INDEX idx_table1_timestamp ON table1(timestamp);

--
-- Table structure for table table2
--

DROP TABLE IF EXISTS table2 CASCADE;
CREATE TABLE table2 (
    id VARCHAR(255) PRIMARY KEY,
    image VARCHAR(255) NOT NULL,
    "order" INTEGER NOT NULL
);

--
-- Table structure for table table3
--

DROP TABLE IF EXISTS table3 CASCADE;
CREATE TABLE table3 (
    id VARCHAR(255) PRIMARY KEY,
    image VARCHAR(255) NOT NULL,
    "order" INTEGER NOT NULL
);

--
-- Table structure for table table4
--

DROP TABLE IF EXISTS table4 CASCADE;
CREATE TABLE table4 (
    id VARCHAR(255) PRIMARY KEY,
    image VARCHAR(255) NOT NULL,
    "order" INTEGER NOT NULL
);

--
-- Table structure for table trading_view_experiments
--

DROP TABLE IF EXISTS trading_view_experiments CASCADE;
CREATE TABLE trading_view_experiments (
    id SERIAL PRIMARY KEY,
    indicator VARCHAR(255) NOT NULL,
    experiment VARCHAR(255) NOT NULL,
    dd REAL NOT NULL,
    intra_dd REAL NOT NULL,
    sortino REAL NOT NULL,
    sharpe REAL NOT NULL,
    profit_factor REAL NOT NULL,
    profitable REAL NOT NULL,
    trades REAL NOT NULL,
    omega REAL NOT NULL,
    net_profit REAL NOT NULL,
    net_profit_ratio REAL NOT NULL,
    parameters VARCHAR(255)
);