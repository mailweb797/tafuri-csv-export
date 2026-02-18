import requests
import csv
import os
from datetime import datetime

SHOP = "calzaturetafuri"
CLIENT_ID = os.environ["SHOPIFY_CLIENT_ID"]
CLIENT_SECRET = os.environ["SHOPIFY_CLIENT_SECRET"]

def get_token():
    response = requests.post(
        f"https://{SHOP}.myshopify.com/admin/oauth/access_token",
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        data={
            "grant_type": "client_credentials",
            "client_id": CLIENT_ID,
            "client_secret": CLIENT_SECRET,
        }
    )
    response.raise_for_status()
    return response.json()["access_token"]

def fetch_all_products(token):
    products = []
    url = f"https://{SHOP}.myshopify.com/admin/api/2025-01/products.json?limit=250&status=active"
    while url:
        r = requests.get(url, headers={"X-Shopify-Access-Token": token})
        r.raise_for_status()
        products.extend(r.json()["products"])
        link = r.headers.get("Link", "")
        url = next((p.strip().split(";")[0].strip().strip("<>") for p in link.split(",") if 'rel="next"' in p), None)
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

token = get_token()
products = fetch_all_products(token)
save_csv(products)
print(f"Aggiornato: {datetime.now()} — {len(products)} prodotti")
