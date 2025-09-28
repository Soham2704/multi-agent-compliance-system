import fitz  # PyMuPDF
import pytesseract
from PIL import Image
import io
import json
import re
import argparse # New import for command-line arguments

def parse_pdf_with_ocr(input_path, output_path):
    """
    Parses a PDF using OCR, extracts text and point numbers, and saves to JSON.
    """
    print(f"--- Starting OCR parsing for '{input_path}' ---")
    all_pages_data = []
    
    try:
        pdf_document = fitz.open(input_path)
    except Exception as e:
        print(f"!!! ERROR: Could not open or read the PDF file at '{input_path}'. Error: {e}")
        return

    # Set the path to the Tesseract executable
    pytesseract.pytesseract.tesseract_cmd = r'C:\Tesseract-OCR\tesseract.exe' # Or your custom path

    for page_num in range(len(pdf_document)):
        page = pdf_document[page_num]
        
        pix = page.get_pixmap(dpi=300)
        image = Image.open(io.BytesIO(pix.tobytes("png")))
        text = pytesseract.image_to_string(image, lang='eng')
        
        pattern = r'\((\d+|[a-z]+)\)|(section \d+)'
        found_items = re.findall(pattern, text)
        point_numbers = [item[0] or item[1] for item in found_items]
        
        page_data = {
            "page_number": page_num + 1,
            "point_numbers": point_numbers,
            "content": text
        }
        all_pages_data.append(page_data)
        print(f"  Processed page {page_num + 1}/{len(pdf_document)}")

    with open(output_path, "w", encoding='utf-8') as f:
        json.dump(all_pages_data, f, indent=4)
    
    print(f"--- Successfully parsed and saved to '{output_path}' ---")


if __name__ == "__main__":
    # Setup command-line argument parsing
    parser = argparse.ArgumentParser(description="Parse a PDF document using OCR.")
    parser.add_argument("--input", required=True, help="Path to the input PDF file.")
    parser.add_argument("--output", required=True, help="Path to the output JSON file.")
    
    args = parser.parse_args()
    
    parse_pdf_with_ocr(args.input, args.output)


