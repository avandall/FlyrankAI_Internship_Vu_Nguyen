from urllib.parse import urljoin
from bs4 import BeautifulSoup
from datetime import datetime, timezone

def extract_catalogue_links(html: str, current_page_url: str) -> tuple[list[str], str | None]:
    soup = BeautifulSoup(html, "html.parser")

    # Lấy danh sách link sách
    book_links = []
    articles = soup.select("article.product_pod h3 a")
    for a in articles:
        href = a.get("href")
        if href:
            absolute_url = urljoin(current_page_url, href)
            book_links.append(absolute_url)

    # Tìm link Next page
    next_btn = soup.select_one("li.next a")
    next_url = urljoin(current_page_url, next_btn.get("href")) if next_btn else None

    return book_links, next_url



def extract_book_details(html: str, product_url: str, source_page: str) -> dict:
    soup = BeautifulSoup(html, "html.parser")
    product_main = soup.select_one("div.product_main")
    if not product_main:
        raise ValueError(f"Not a valid product detail page: {product_url}")

    # Title
    title_elem = product_main.select_one("h1")
    title = title_elem.text.strip() if title_elem else ""

    # Price Text
    price_elem = product_main.select_one("p.price_color")
    price_text = price_elem.text.strip() if price_elem else ""

    # Availability Text
    avail_elem = product_main.select_one("p.instock.availability")
    availability_text = " ".join(avail_elem.text.split()) if avail_elem else ""

    # Rating Text (class: star-rating Three -> 'Three')
    rating_elem = product_main.select_one("p.star-rating")
    rating_text = ""
    if rating_elem:
        classes = rating_elem.get("class", [])
        rating_classes = [c for c in classes if c != "star-rating"]
        rating_text = rating_classes[0] if rating_classes else ""

    # Description (ở thẻ p nằm sau #product_description)
    desc_header = soup.select_one("#product_description")
    description = None
    if desc_header:
        desc_elem = desc_header.find_next_sibling("p")
        if desc_elem and desc_elem.text.strip():
            description = desc_elem.text.strip()

    return {
        "title": title,
        "product_url": product_url,
        "price_text": price_text,
        "availability_text": availability_text,
        "rating_text": rating_text,
        "description": description,
        "source_page": source_page,
        "fetched_at": datetime.now(timezone.utc).isoformat()
    }