import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import json
import re

# --- Add this line to tell Python where to find Tesseract ---
pytesseract.pytesseract.tesseract_cmd = r'C:\Users\soham\Downloads\Tesseract-OCR\tesseract.exe'

print("Starting OCR parsing process...")
all_pages_data = []
pdf_document = fitz.open("io/DCPR_2034.pdf")

# Loop through every page in the PDF
for page_num in range(len(pdf_document)):
    page = pdf_document[page_num]
    
    # 1. Use PyMuPDF to convert the page to a high-quality image
    pix = page.get_pixmap(dpi=300)
    image_bytes = pix.tobytes("png")
    image = Image.open(io.BytesIO(image_bytes))
    
    # 2. Use Tesseract to "read" the clean text from the image
    text = pytesseract.image_to_string(image, lang='eng')
    
    # 3. Find all point numbers on the current page using the clean text
    pattern = r'\((\d+|[a-z]+)\)|(section \d+)'
    found_items = re.findall(pattern, text)
    point_numbers = [item[0] or item[1] for item in found_items]
    
    # Store all extracted data in a dictionary
    page_data = {
        "page_number": page_num + 1,
        "point_numbers": point_numbers,
        "content": text
    }
    all_pages_data.append(page_data)
    print(f"Processed page {page_num + 1}/{len(pdf_document)}")

# Save the complete list of clean data to a JSON file
output_path = "rules_kb/parsed_rules.json"
with open(output_path, "w", encoding='utf-8') as f:
    json.dump(all_pages_data, f, indent=4)

print(f"\nSuccessfully parsed {len(all_pages_data)} pages with OCR and saved to {output_path}")