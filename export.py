import requests
import csv
import os
from datetime import datetime

SHOP = "calzaturetafuri.myshopify.com"
TOKEN = os.environ["SHOPIFY_TOKEN"]

def fetch_all_products():
    products = []
    url = f"https://{SHOP}/admin/api/2024-01/products.json?limit=250&status=active"
    while url:
        r = requests.get(url, headers={"X-Shopify-Access-Token": TOKEN})
        r.raise_for_status()
        products.extend(r.json()["products"])
        link = r.headers.get("Link", "")
        url = next((p.split(">")[0].lstrip("<") for p in link.split(",") if 'rel="next"' in p), None)
    return products

def save_csv(products):
    os.makedirs("docs", exist_ok=True)
    with open("docs/products.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["ID", "Titolo", "Marca", "Tipo", "SKU", "Prezzo", "Disponibilita", "Immagine", "URL Prodotto"])
        for p in products:
            for v in p.get("variants", []):
                img = p.get("images", [{}])[0].get("src", "")
                handle = p.get("handle", "")
                w.writerow([
                    p["id"], p["title"], p["vendor"], p["product_type"],
                    v["sku"], v["price"], v["inventory_quantity"],
                    img, f"https://calzaturetafuri.com/products/{handle}"
                ])

products = fetch_all_products()
save_csv(products)
print(f"Aggiornato: {datetime.now()} — {len(products)} prodotti")
