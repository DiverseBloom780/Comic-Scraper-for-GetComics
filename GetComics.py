import os
import requests
from bs4 import BeautifulSoup
import threading
from tqdm import tqdm  # Progress bar for downloads

# Function to get the number of pages for a category
def get_total_pages(category_url):
    response = requests.get(category_url)
    if response.status_code != 200:
        print(f"Failed to fetch {category_url}")
        return 1
    
    soup = BeautifulSoup(response.text, 'html.parser')
    pagination = soup.find('div', class_='wp-pagenavi')
    if pagination:
        pages = [int(a.text) for a in pagination.find_all('a') if a.text.isdigit()]
        return max(pages) if pages else 1
    return 1

# Function to scrape all comic links from a category
def get_comic_links(base_url, num_pages):
    links = set()
    for page in range(1, num_pages + 1):
        url = f"{base_url}/page/{page}/" if page > 1 else base_url
        response = requests.get(url)
        if response.status_code != 200:
            print(f"Failed to fetch {url}")
            continue
        soup = BeautifulSoup(response.text, 'html.parser')
        for link in soup.find_all('a', href=True):
            if '/dc/' in link['href'] or '/marvel/' in link['href']:
                links.add(link['href'])
    return list(links)

# Function to get the direct download link
def get_direct_download_link(comic_page_url):
    response = requests.get(comic_page_url)
    if response.status_code != 200:
        print(f"Failed to access {comic_page_url}")
        return None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    for link in soup.find_all('a', href=True):
        if '/dlds/' in link['href']:
            return link['href']
    
    print(f"No direct download link found for {comic_page_url}")
    return None

# Function to download a comic with resuming support
def download_comic(comic_page_url, save_path):
    direct_link = get_direct_download_link(comic_page_url)
    if not direct_link:
        return
    
    comic_name = comic_page_url.strip('/').split('/')[-1] + ".cbz"  # Assuming CBZ format
    if "#comment" in comic_name:
        print(f"Skipping: {comic_name}")
        return
    
    save_file_path = os.path.join(save_path, comic_name)
    
    if os.path.exists(save_file_path):
        print(f"Skipping already downloaded: {comic_name}")
        return
    
    response = requests.get(direct_link, stream=True)
    response.raise_for_status()
    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0
    
    with open(save_file_path, 'wb') as f, tqdm(
        total=total_size, unit='B', unit_scale=True, desc=comic_name) as progress:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            progress.update(len(chunk))
    
    print(f"\nDownloaded: {save_file_path}")

if __name__ == "__main__":
    categories = {
        "DC": "https://getcomics.org/category/dc-comics/",
        "Marvel": "https://getcomics.org/category/marvel-comics/",
        "Indie": "https://getcomics.org/category/indie-week/",
        "Other": "https://getcomics.org/category/other-comics/"
    }
    
    save_path = os.path.join(os.path.expanduser("~"), "Desktop", "Downloads")
    os.makedirs(save_path, exist_ok=True)
    
    all_comic_links = []
    
    # Scrape comics from each category
    for name, url in categories.items():
        total_pages = get_total_pages(url)
        print(f"Scraping {name} ({total_pages} pages)...")
        all_comic_links.extend(get_comic_links(url, total_pages))
    
    print(f"Found {len(all_comic_links)} comics.")
    
    # Use threading to download multiple comics at once
    threads = []
    for comic_link in all_comic_links:
        thread = threading.Thread(target=download_comic, args=(comic_link, save_path))
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    
    print("All comics downloaded!")
