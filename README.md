📌 Instructions to Use GetComics Scraper on Your PC
1️⃣ Install Dependencies
First, make sure you have Python installed. Then, install the required libraries by running:

sh
pip install requests beautifulsoup4 tqdm

2️⃣ Download the Script
Clone your GitHub repository or download GetComics.py into a folder on your PC.

3️⃣ Run the Script
Navigate to the folder where GetComics.py is located and run:

sh
python GetComics.py

4️⃣ What This Script Does:
Scans all drives for previously downloaded comics.
Scrapes all pages from GetComics.org, ensuring no comics are missed.
Automatically skips already downloaded comics.
Looks for MegaDrive, WeTransfer, Mirror, and Main Server links if no direct download is found.
📂 Download Path
By default, comics are saved in:

sh
F:\Books

If you need to change this, edit the save_path variable inside GetComics.py.

