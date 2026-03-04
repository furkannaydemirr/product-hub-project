from flask import Flask, jsonify, render_template, request
import psycopg2

app = Flask(__name__)

def get_db_connection():
    try:
        return psycopg2.connect(dbname="postgres", user="postgres", password="sqllearner1", host="localhost", port="5432")
    except Exception as e:
        print(f"BAĞLANTI HATASI: {e}")
        return None

@app.route("/")
def index(): return render_template("app.html")

@app.route("/store/<string:store_name>")
def store_page(store_name): return render_template("store.html", store_name=store_name)

@app.route("/api/products")
def api_products():
    q = request.args.get('q', '')
    sort = request.args.get('sort', 'default')
    min_rating = request.args.get('min_rating', '0')
    max_price = request.args.get('max_price', '')
    category = request.args.get('category', '')
    gender = request.args.get('gender', '')
    country = request.args.get('country', '')

    conn = get_db_connection()
    if not conn: return jsonify({"error": "DB Fail"}), 500
    
    cursor = conn.cursor()
    query = "SELECT m.internal_id, m.api_title, m.api_price, m.api_rating, m.api_image_url, m.api_review_count FROM main_database m WHERE m.api_title ILIKE %s"
    params = [f"%{q}%"]

    # FİLTRELER
    if min_rating and min_rating != '0':
        query += " AND m.api_rating >= %s"
        params.append(float(min_rating))
    if max_price:
        query += " AND m.api_price <= %s"
        params.append(float(max_price))
    if category:
        query += " AND m.api_category = %s"
        params.append(category)
    if gender:
        query += " AND m.api_gender = %s"
        params.append(gender)
    if country:
        query += " AND m.api_country = %s"
        params.append(country)

    # SIRALAMA MANTIĞI
    # Sıralamanın veritabanı sorgusuna yansıdığı yer burasıdır.
    if sort == "lowest_price":
        query += " ORDER BY m.api_price ASC"
    elif sort == "highest_price":
        query += " ORDER BY m.api_price DESC"
    elif sort == "highest_rating":
        query += " ORDER BY m.api_rating DESC"
    elif sort == "highest_reviews":
        query += " ORDER BY m.api_review_count DESC"
    else:
        # Varsayılan sıralama (örneğin ID'ye göre veya rastgele)
        query += " ORDER BY m.internal_id ASC"
    
    cursor.execute(query, params)
    products = cursor.fetchall(); conn.close()
    
    return jsonify([{
        "id": p[0], "title": p[1], "price": float(p[2]) if p[2] else 0.0, 
        "rating": float(p[3]) if p[3] else 0.0, "image": p[4], "reviews": p[5]
    } for p in products])

# DİĞER API ROTALARI (DEĞİŞMEDİ)
@app.route("/api/product/<int:id>/offers")
def get_product_offers(id):
    conn = get_db_connection(); cursor = conn.cursor()
    cursor.execute("SELECT offers_store_name, offer_price, offers_url, offer_store_rating FROM offers_database WHERE product_internal_id = %s", (id,))
    offers = cursor.fetchall(); conn.close()
    return jsonify([{"store": o[0], "price": float(o[1]), "url": o[2], "rating": float(o[3])} for o in offers])

@app.route("/api/store_details/<string:store_name>")
def get_store_details(store_name):
    conn = get_db_connection()
    if not conn: return jsonify({"error": "DB Fail"}), 500
    cursor = conn.cursor()
    cursor.execute("SELECT offers_store_name, AVG(offer_store_rating), COUNT(*) FROM offers_database WHERE offers_store_name = %s GROUP BY offers_store_name", (store_name,))
    d = cursor.fetchone()
    if not d: return jsonify({"error": "Store not found"}), 404
    cursor.execute("SELECT m.api_title, o.offer_price, m.api_image_url, o.offers_url, m.api_rating FROM main_database m JOIN offers_database o ON m.internal_id = o.product_internal_id WHERE o.offers_store_name = %s", (store_name,))
    p_list = cursor.fetchall(); conn.close()
    return jsonify({
        "info": {"name": d[0], "rank": round(float(d[1]), 1) if d[1] else 0, "count": d[2], "image": "https://via.placeholder.com/100", "country": "US"},
        "products": [{"title": p[0], "price": float(p[1]), "image": p[2], "url": p[3], "rating": float(p[4])} for p in p_list]
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)