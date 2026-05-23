import requests
from urllib.parse import urljoin


# These Shopify stores block common browser User-Agent strings (403).
# Minimal headers keep /search/suggest.json working.
DEFAULT_HEADERS = {
    "Accept": "application/json",
}


def fetch_products(origin: str, query: str, site_label: str, max_items: int = 5):
    """Shopify predictive search JSON — HTML scraping breaks when themes change."""
    results = []
    q = (query or "").strip()
    if not q:
        return results

    base = origin.rstrip("/")
    url = f"{base}/search/suggest.json"
    params = {
        "q": q,
        "resources[type]": "product",
        "resources[limit]": "10",
    }

    try:
        response = requests.get(url, params=params, headers=DEFAULT_HEADERS, timeout=10)
        if response.status_code == 403:
            response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as e:
        print(f"{site_label} Scraper Error:", e)
        return results

    products = (
        data.get("resources", {})
        .get("results", {})
        .get("products", [])
    )

    for product in products[:max_items]:
        title = (product.get("title") or "").strip()
        path = product.get("url") or ""
        if not path and product.get("handle"):
            path = f"/products/{product['handle']}"
        price_raw = product.get("price")
        if not title or not path:
            continue
        try:
            price = int(float(price_raw))
        except (TypeError, ValueError):
            continue

        product_url = urljoin(base + "/", path)
        image_url = product.get("image") or ""
        
        results.append(
            {
                "name": title,
                "price": price,
                "url": product_url,
                "image": image_url,
                "site": site_label,
            }
        )

    return results
