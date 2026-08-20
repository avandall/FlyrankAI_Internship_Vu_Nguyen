import json
import time
from datetime import datetime, timezone
from src.config import BASE_URL, OUTPUT_DIR
from src.fetcher import PoliteFetcher
from src.parser import extract_catalogue_links, extract_book_details
from src.schema import BookRecord, normalize_price

def run_pipeline(inject_broken_url: bool = False):
    start_time = datetime.now(timezone.utc)
    fetcher = PoliteFetcher()

    discovered_books = []  # list of (book_url, source_page)
    current_url = BASE_URL
    catalogue_count = 0
    max_catalogue_pages = 3

    print("=== STEP 1: Discover Catalogue Pages ===")
    while current_url and catalogue_count < max_catalogue_pages:
        catalogue_count += 1
        html, _ = fetcher.fetch(current_url)
        links, next_url = extract_catalogue_links(html, current_url)
        for link in links:
            discovered_books.append((link, current_url))
        current_url = next_url

    # Loại bỏ trùng lặp giữ nguyên thứ tự
    seen_urls = set()
    unique_books = []
    for url, src in discovered_books:
        if url not in seen_urls:
            seen_urls.add(url)
            unique_books.append((url, src))

    if inject_broken_url:
        unique_books.append(("https://books.toscrape.com/catalogue/non-existent-book_999/index.html", BASE_URL))

    print(f"\nDiscovered {len(unique_books)} books across {catalogue_count} catalogue pages.")

    print("\n=== STEP 2: Extract, Normalize & Validate Books ===")
    valid_records: list[dict] = []
    invalid_records: list[dict] = []
    failed_pages: list[dict] = []

    for book_url, source_page in unique_books:
        try:
            book_html, _ = fetcher.fetch(book_url)
            raw_record = extract_book_details(book_html, book_url, source_page)

            # Normalize
            price_gbp = normalize_price(raw_record["price_text"])
            raw_record["price_gbp"] = price_gbp

            # Validate via Pydantic
            validated = BookRecord(**raw_record)
            # Chuyển đổi HttpUrl về string khi lưu JSON
            record_dict = validated.model_dump(mode="json")
            valid_records.append(record_dict)

        except Exception as e:
            # Phân loại lỗi mạng/HTTP vs lỗi validation
            err_str = str(e)
            if "HTTP" in err_str or "Network error" in err_str:
                failed_pages.append({"url": book_url, "error": err_str})
                print(f"[PAGE FAILURE] Skipped: {book_url} -> {err_str}")
            else:
                invalid_records.append({"url": book_url, "error": err_str})
                print(f"[SCHEMA ERROR] Invalid data: {book_url} -> {err_str}")

    # Ghi file kết quả
    books_file = OUTPUT_DIR / "books.json"
    errors_file = OUTPUT_DIR / "errors.json"
    report_file = OUTPUT_DIR / "run-report.json"

    with open(books_file, "w", encoding="utf-8") as f:
        json.dump(valid_records, f, indent=2, ensure_ascii=False)

    with open(errors_file, "w", encoding="utf-8") as f:
        json.dump({"schema_errors": invalid_records, "failed_pages": failed_pages}, f, indent=2)

    end_time = datetime.now(timezone.utc)
    duration = (end_time - start_time).total_seconds()

    report = {
        "start_time": start_time.isoformat(),
        "end_time": end_time.isoformat(),
        "duration_seconds": round(duration, 2),
        "catalogue_pages_visited": catalogue_count,
        "pages_fetched": fetcher.pages_fetched,
        "cache_hits": fetcher.cache_hits,
        "valid_records": len(valid_records),
        "invalid_records": len(invalid_records),
        "failed_pages_count": len(failed_pages)
    }

    with open(report_file, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2)

    print("\n=== RUN REPORT ===")
    print(json.dumps(report, indent=2))

if __name__ == "__main__":
    # Để kiểm tra khả năng sống sót khi gặp lỗi, set inject_broken_url=True
    run_pipeline(inject_broken_url=True)