import requests
import os

def download_nyc_311(output_path="data/nyc311_sample.csv", limit=100000):
    print("Downloading NYC 311 data...")
    
    # NYC Open Data API: returns CSV with exactly chosen 100k rows
    url = (
        "https://data.cityofnewyork.us/resource/erm2-nwe9.csv"
        f"?$limit={limit}"
        "&$where=created_date>'2024-01-01'"
        "&$order=created_date DESC"
    )
    
    response = requests.get(url, timeout=60)
    
    if response.status_code == 200:
        # Create data folder if it doesn't exist
        os.makedirs("data", exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(response.text)
        
        print(f"Done. Saved to {output_path}")
    else:
        print(f"Error: {response.status_code}")

if __name__ == "__main__":
    download_nyc_311()