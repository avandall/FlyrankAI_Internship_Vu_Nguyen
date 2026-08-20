from urllib.parse import urljoin
from bs4 import BeautifulSoup

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