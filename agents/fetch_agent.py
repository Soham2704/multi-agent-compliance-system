import requests
import os

url = "https://portal.mcgm.gov.in/irj/go/km/docs/documents/MCGM%20Department%20List/Chief%20Engineer%20(Development%20Plan)/Docs/SANCTIONED%20DP2034/DCPR/DCPR%202034.pdf"
save_path = "io/DCPR_2034.pdf"

print(f"Downloading file from {url}...")
response = requests.get(url)

if response.status_code == 200:
    print("Success! The file was downloaded.")
    
    # We open the save_path in 'write-bytes' mode ('wb')
    with open(save_path, "wb") as f:
        # We write the content from the response to our new file
        f.write(response.content)
    
    print(f"File saved successfully to {save_path}")
else:
    print(f"Failed with status code: {response.status_code}")