import requests
import psycopg2 
from datetime import datetime, timedelta
import time

# API Bilgileri

def safe_float(val):
    
    if not val: return 0.0
    try:
       
        val_str = str(val).split('/')[0]
        return float(val_str.replace('$', '').replace(',', '').strip())
    except: return 0.0

def collect_data():
    try:
        conn = psycopg2.connect(dbname="", user="", password="", host="", port="")
        cursor = conn.cursor()

        #  Eski ve bozuk verileri temizle 
        print("Eski veriler temizleniyor...")
        cursor.execute("TRUNCATE main_database CASCADE;")
        conn.commit()

        #  API'den 50 
        print("API'den yeni veriler çekiliyor (Limit: 50)...")
        res = requests.get("https://real-time-product-search.p.rapidapi.com/search-v2", 
                           headers=headers, params={"q": "Nike shoes", "limit": "50"})
        
        if res.status_code != 200:
            print(f"API Hatası: {res.status_code}")
            return

        products = res.json().get('data', {}).get('products', [])
        print(f"Toplam {len(products)} ürün bulundu. İşleniyor...")

        for p in products:
            api_id = p.get("product_id")
            title = p.get("product_title", "No Title")
            
            # Fotoğraf kontrolü
            photos = p.get("product_photos", [])
            img = photos[0] if photos else "https://via.placeholder.com/150"
            
            # Cinsiyet tahmini
            gen = "Kadın" if "Women" in title else "Erkek" if "Men" in title else "Unisex"
            
            # Ürünü veritabanı
            cursor.execute("""
                INSERT INTO main_database (api_id, api_title, api_rating, api_review_count, api_image_url, api_category, api_gender, api_country, api_price)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s) 
                RETURNING internal_id;""", 
                (api_id, title, safe_float(p.get("product_rating")), p.get("product_num_reviews", 0), img, "Ayakkabı", gen, "US", 0.0))
            
            captured_id = cursor.fetchone()[0]
            
            # Mağaza fiyatlarını çek
            time.sleep(0.5) # API limiT
            o_res = requests.get("https://real-time-product-search.p.rapidapi.com/product-offers-v2", 
                                 headers=headers, params={"product_id": api_id})
            
            best_price = 0.0
            
            if o_res.status_code == 200:
                offers = o_res.json().get('data', {}).get('offers', [])
                price_list = []
                
                for o in offers:
                    price = safe_float(o.get("price"))
                    if price > 0: price_list.append(price)
                    
                    #  kaydet
                    cursor.execute("""
                        INSERT INTO offers_database (product_internal_id, offers_url, offer_price, offers_store_name, offer_store_rating)
                        VALUES (%s, %s, %s, %s, %s)""", 
                        (captured_id, o.get("offer_page_url"), price, o.get("store_name"), safe_float(o.get("store_rating"))))
                
                # En düşük fiyat
                if price_list:
                    best_price = min(price_list)

            # 4. ADIM: Ana ürün güncelle
            if best_price > 0:
                cursor.execute("UPDATE main_database SET api_price = %s WHERE internal_id = %s", (best_price, captured_id))
                print(f" Eklendi: {title[:30]}... [Fiyat: ${best_price}]")
            else:
                print(f" Eklendi: {title[:30]}... [Fiyat Bulunamadı, $0 kaldı]")

            conn.commit()

        conn.close()
        print("\n TAMAM")

    except Exception as e: print(f" Hata: {e}")

if __name__ == "__main__": collect_data()