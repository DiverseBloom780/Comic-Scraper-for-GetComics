import os
import requests
from bs4 import BeautifulSoup

def get_comic_links(base_url, num_pages=1):
    """Scrape comic download links from GetComics.org"""
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

def get_direct_download_link(comic_page_url):
    """Extract the direct GetComics download link from a comic's page"""
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

def download_comic(comic_page_url, save_path):
    """Download the comic file from its direct link with progress tracking"""
    direct_link = get_direct_download_link(comic_page_url)
    if not direct_link:
        return
    
    comic_name = comic_page_url.strip('/').split('/')[-1] + ".cbz"  # Assuming CBZ format
    if "#comment" in comic_name:
        print(f"Skipping: {comic_name}")
        return
    
    save_file_path = os.path.join(save_path, comic_name)
    
    print(f"Downloading {comic_name}...")
    response = requests.get(direct_link, stream=True)
    response.raise_for_status()
    
    total_size = int(response.headers.get('content-length', 0))
    downloaded = 0
    
    with open(save_file_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
            downloaded += len(chunk)
            percent = (downloaded / total_size) * 100 if total_size else 0
            print(f"{comic_name}: {downloaded / (1024 * 1024):.2f}/{total_size / (1024 * 1024):.2f} MB ({percent:.2f}%)", end='\r')
    
    print(f"\nDownloaded: {save_file_path}")

if __name__ == "__main__":
    base_url = "https://getcomics.org"  # Change this if needed
    num_pages = 5  # Adjust as needed
    save_path = os.path.join(os.path.expanduser("~"), "Desktop", "Downloads")  # Downloads on Desktop
    os.makedirs(save_path, exist_ok=True)
    
    print("Scraping GetComics...")
    comic_links = get_comic_links(base_url, num_pages)
    print(f"Found {len(comic_links)} comics.")
    
    for comic_link in comic_links:
        download_comic(comic_link, save_path)
    
    print("All comics downloaded!")
