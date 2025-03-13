import os
import requests
import time
from bs4 import BeautifulSoup
from tqdm import tqdm

# User-Agent to prevent blocking
HEADERS = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36"}
SESSION = requests.Session()
SESSION.headers.update(HEADERS)

print("Starting script...")

# Detect all available drives
def get_all_drives():
    return [f"{d}:\\" for d in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" if os.path.exists(f"{d}:\\")]

# Check for already downloaded comics in Books and Downloads folders of all drives
def get_downloaded_comics():
    print("Checking for already downloaded comics...")
    downloaded_comics = set()
    for drive in get_all_drives():
        for folder in ["Books", "Downloads"]:
            base_path = os.path.join(drive, folder)
            if os.path.exists(base_path):
                for root, _, files in os.walk(base_path):
                    for file in files:
                        if file.endswith(".cbz") or file.endswith(".cbr"):
                            downloaded_comics.add(file)
    print(f"Total downloaded comics found: {len(downloaded_comics)}")
    return downloaded_comics

# Fetch total pages in a category before scraping
def get_total_pages(base_url):
    print(f"Checking total pages for {base_url}...")
    try:
        response = SESSION.get(base_url, timeout=10)
        print(f"Fetched {base_url}, Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Failed to fetch {base_url}")
            return 1
        
        soup = BeautifulSoup(response.text, 'html.parser')
        pagination = soup.find('a', class_='last')
        if pagination and 'href' in pagination.attrs:
            return int(pagination['href'].split('/page/')[-1].split('/')[0])
        return 1
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {base_url}: {e}")
        return 1

# Get comic links from a single page
def get_comic_links_from_page(url):
    print(f"Scraping page: {url}")
    links = set()
    try:
        response = SESSION.get(url, timeout=10)
        print(f"Fetched {url}, Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Failed to fetch {url} (Status Code: {response.status_code})")
            return []
        
        soup = BeautifulSoup(response.text, 'html.parser')
        for article in soup.find_all('article', class_='post'):
            link = article.find('a', href=True)
            if link and "getcomics.org" in link['href']:
                links.add(link['href'])
        
        print(f"Found {len(links)} comics on {url}")
        time.sleep(1)  # Small delay to prevent rate limiting
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {url}: {e}")
    
    return list(links)

# Get direct download link
def get_direct_download_link(comic_page_url):
    print(f"Checking download link for {comic_page_url}...")
    try:
        response = SESSION.get(comic_page_url, timeout=10)
        print(f"Fetched {comic_page_url}, Status: {response.status_code}")
        if response.status_code != 200:
            print(f"Failed to access {comic_page_url} (Status Code: {response.status_code})")
            return None
        
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            if '/dlds/' in link['href']:
                print(f"Download link found: {link['href']}")
                return link['href']
        
        print(f"No direct download link found for {comic_page_url}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Error fetching {comic_page_url}: {e}")
        return None

# Download comics
def download_comic(comic_page_url, save_path):
    direct_link = get_direct_download_link(comic_page_url)
    if not direct_link:
        print(f"Skipping download: No valid link for {comic_page_url}")
        return
    
    comic_name = comic_page_url.strip('/').split('/')[-1]
    if "#comment" in comic_name:
        print(f"Skipping: {comic_name}")
        return
    
    file_extension = ".cbz" if ".cbz" in direct_link else ".cbr"
    save_file_path = os.path.join(save_path, comic_name + file_extension)
    
    print(f"Downloading {comic_name}...")
    try:
        response = SESSION.get(direct_link, stream=True, timeout=30)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        
        with open(save_file_path, 'wb') as f, tqdm(
            total=total_size, unit='B', unit_scale=True, desc=comic_name
        ) as progress:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                progress.update(len(chunk))
        
        print(f"Downloaded: {save_file_path}")
    except requests.exceptions.RequestException as e:
        print(f"Error downloading {comic_name}: {e}")

if __name__ == "__main__":
    categories = [
        "https://getcomics.org",
        "https://getcomics.org/cat/dc",
        "https://getcomics.org/cat/marvel",
        "https://getcomics.org/cat/other-comics",
    ]
    
    print("Starting download process...")
    save_path = os.path.join(os.path.expanduser("~"), "Desktop", "Downloads")
    os.makedirs(save_path, exist_ok=True)
    
    downloaded_comics = get_downloaded_comics()
    
    print("Scraping main categories and home page...")
    for category in categories:
        total_pages = get_total_pages(category)
        print(f"Total pages found for {category}: {total_pages}")
        for page in range(1, total_pages + 1):
            page_url = f"{category}/page/{page}/" if page > 1 else category
            print(f"Scraping page {page} of {total_pages} from {category}...")
            comic_links = get_comic_links_from_page(page_url)
            
            for comic_link in comic_links:
                print(f"Processing comic: {comic_link}")
                download_comic(comic_link, save_path)
    
    print("All comics processed!")
