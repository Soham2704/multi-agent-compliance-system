import requests
import os

# --- UPGRADE: Now includes Ahmedabad and Nashik ---
DOCUMENTS = {
    "Mumbai": {
        "url": "https://portal.mcgm.gov.in/irj/go/km/docs/documents/MCGM%20Department%20List/Chief%20Engineer%20(Development%20Plan)/Docs/SANCTIONED%20DP2034/DCPR/DCPR%202034.pdf",
        "output_path": "io/DCPR_2034.pdf"
    },
    "Pune": {
        "url": "https://www.pmrda.gov.in/wp-content/uploads/2025/04/Final-PMRDA-DCPR-2018-.pdf",
        "output_path": "io/Pune_DCR.pdf"
    },
    "Ahmedabad": {
        "url": "https://www.auda.org.in/uploads/Assets/rdp/commongdcr08012016052529533.pdf",
        "output_path": "io/Ahmedabad_DCR.pdf"
    },
    "Nashik": {
        "url": "https://nmc.gov.in/assets/admin/upload/download/SDCR_under_section_26.pdf",
        "output_path": "io/Nashik_DCR.pdf"
    }
}

# --- Download Logic (Unchanged) ---
def download_files():
    print("--- Checking and Downloading Source Documents for All Regions ---")
    os.makedirs("io", exist_ok=True)
    
    for city, info in DOCUMENTS.items():
        if os.path.exists(info["output_path"]):
            print(f"'{info['output_path']}' already exists. Skipping download.")
        else:
            print(f"Downloading {city} DCR from {info['url']}...")
            try:
                response = requests.get(info["url"], timeout=60) # Increased timeout for larger files
                response.raise_for_status()
                
                with open(info["output_path"], "wb") as f:
                    f.write(response.content)
                print(f"Successfully saved to '{info['output_path']}'")
            except requests.exceptions.RequestException as e:
                print(f"!!! FAILED to download {city} DCR. Error: {e}")

if __name__ == "__main__":
    download_files()