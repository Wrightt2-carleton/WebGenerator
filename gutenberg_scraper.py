import requests
import os
import re
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# Base URL for the Project Gutenberg Mythology Bookshelf
BASE_URL = "https://www.gutenberg.org/ebooks/search/?query=dragon&submit_search=Go%21&start_index=26"

# Headers to mimic a real browser (prevents 403 Forbidden errors)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
}

# Directory to save downloaded books
SAVE_DIR = "gutenberg_books"
os.makedirs(SAVE_DIR, exist_ok=True)  # Ensure directory exists

def get_book_links():
    """Scrape the bookshelf page to get all book links."""
    response = requests.get(BASE_URL, headers=HEADERS)
    
    if response.status_code != 200:
        print("❌ Error: Could not fetch bookshelf page.")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Find all book links
    book_links = [
        urljoin(BASE_URL, a["href"]) for a in soup.select("li.booklink a.link")
        if a["href"].startswith("/ebooks/")
    ]
    
    print(f"🔍 Found {len(book_links)} books.")
    return book_links

def get_text_urls(book_url):
    """Find all possible .txt file URLs for a given book."""
    response = requests.get(book_url, headers=HEADERS)
    
    if response.status_code != 200:
        print(f"❌ Error: Could not access book page {book_url}")
        return []
    
    soup = BeautifulSoup(response.text, "html.parser")
    txt_urls = []

    # 1. Extract direct .txt link from the book's page (if available)
    for a in soup.find_all("a", href=True):
        if "Plain Text UTF-8" in a.text or a["href"].endswith(".txt"):
            txt_urls.append(urljoin(book_url, a["href"]))
    
    # 2. Extract book ID (e.g., "https://www.gutenberg.org/ebooks/55" -> "55")
    match = re.search(r"/ebooks/(\d+)", book_url)
    if match:
        book_id = match.group(1)
        # Correct storage path for most books
        txt_urls.append(f"https://www.gutenberg.org/cache/epub/{book_id}/pg{book_id}.txt")

    return txt_urls

def download_text_file(url):
    """Download the .txt file from the given URL and save it."""
    if not url:
        return
    
    response = requests.get(url, headers=HEADERS, allow_redirects=True)
    
    if response.status_code == 404:
        print(f"❌ Error: File not found at {url} (HTTP 404)")
        return
    elif response.status_code != 200:
        print(f"❌ Error: Could not download {url} (HTTP {response.status_code})")
        return
    
    # Ensure the file is saved as .txt (even if it's mistakenly labeled as UTF-8)
    filename = os.path.join(SAVE_DIR, os.path.basename(url).split(".")[0] + ".txt")

    # Save text content in UTF-8 format
    try:
        with open(filename, "w", encoding="utf-8") as file:
            file.write(response.text)
        print(f"✅ Downloaded: {filename}")
    except Exception as e:
        print(f"❌ Failed to save {filename}: {e}")

if __name__ == "__main__":
    print("🔄 Scraping Project Gutenberg Mythology Bookshelf...")
    book_links = get_book_links()
    
    for book_link in book_links:
        print(f"📖 Processing book: {book_link}")
        text_urls = get_text_urls(book_link)
        
        for text_url in text_urls:
            download_text_file(text_url)

    print("🚀 All available books downloaded!")
