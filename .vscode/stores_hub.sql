-- Tabloları temizle
DROP TABLE IF EXISTS offers_database;
DROP TABLE IF EXISTS main_database;

-- Ana Ürün Havuzu (Pool)
CREATE TABLE main_database (
    internal_id SERIAL PRIMARY KEY, 
    last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    api_id TEXT NOT NULL UNIQUE, 
    api_title TEXT,
    api_price DECIMAL(10, 2), -- SIRALAMA İÇİN KRİTİK SÜTUN
    api_rating DECIMAL(3, 1),
    api_review_count INTEGER DEFAULT 0,
    api_image_url TEXT,
    api_category TEXT,
    api_gender TEXT,
    api_country TEXT
);

-- Mağaza Teklifleri
CREATE TABLE offers_database (
    offers_internal_id SERIAL PRIMARY KEY,
    product_internal_id INTEGER REFERENCES main_database(internal_id), 
    offers_url TEXT,
    offer_price DECIMAL(10,2),
    offers_store_name TEXT,
    offer_store_rating DECIMAL(3,1)
);