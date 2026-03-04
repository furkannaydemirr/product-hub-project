async function applyFilters() {
    // Filtre değerlerini çek
    const q = document.getElementById("search-input")?.value || "";
    const sort = document.getElementById("sort-select")?.value || "default";
    const gen = document.getElementById("gender-select")?.value || "";
    const cat = document.getElementById("category-select")?.value || "";
    const country = document.getElementById("country-select")?.value || "";
    const minRating = document.getElementById("min-rating")?.value || "0";
    const maxPrice = document.getElementById("max-price-input")?.value || "";

    const params = new URLSearchParams({ q, sort, gender: gen, category: cat, country, min_rating: minRating, max_price: maxPrice });
    
    try {
        const res = await fetch(`/api/products?${params.toString()}`);
        const products = await res.json();
        const body = document.getElementById("data-body");
        body.innerHTML = ""; 

        products.forEach(p => {
            body.innerHTML += `
                <div class="card" onclick="openModal(${p.id}, '${p.title.replace(/'/g, "\\'")}')" style="background:white; padding:15px; border-radius:10px; text-align:center; cursor:pointer; box-shadow:0 2px 5px rgba(0,0,0,0.1);">
                    <img src="${p.image}" style="width:100%; height:180px; object-fit:cover; border-radius:5px;">
                    <h4 style="font-size:14px; margin:10px 0; height:40px; overflow:hidden;">${p.title}</h4>
                    <p style="color:red; font-weight:bold;">$${p.price}</p>
                    <p style="font-size:12px; color:#f39c12;">⭐ ${p.rating} (${p.reviews} Yorum)</p>
                </div>`;
        });
    } catch (e) { console.error("Hata:", e); }
}

async function openModal(id, title) {
    const res = await fetch(`/api/product/${id}/offers`);
    const offers = await res.json();
    let html = `<h2>${title}</h2><p>Tüm Mağazalar:</p><hr>`;
    offers.forEach(o => {
        html += `
            <div style="display:flex; justify-content:space-between; align-items:center; padding:10px; border-bottom:1px solid #eee;">
                <a href="/store/${encodeURIComponent(o.store)}" style="font-weight:bold; color:blue; text-decoration:none;">🏬 ${o.store}</a>
                <span><strong>$${o.price}</strong></span>
                <a href="${o.url}" target="_blank" style="background:black; color:white; padding:5px 10px; text-decoration:none; border-radius:4px; font-size:12px;">GİT</a>
            </div>`;
    });
    document.getElementById("modal-content").innerHTML = html;
    document.getElementById("modal").style.display = "block";
}

function closeModal() { document.getElementById("modal").style.display = "none"; }
window.onload = applyFilters;