import os
import sys
import io
import pdfminer
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import googlemaps
import requests
import subprocess
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
timestamp = datetime.now().strftime("%y%m%d%H%M%S")

cred = credentials.Certificate('tab-tools-firebase-adminsdk-8ncav-4f5ccee9af.json')
firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://tab-tools-default-rtdb.firebaseio.com/'
    })
db2 = firestore.client()

user_uid = sys.argv[1]
file_name = sys.argv[2]

google_maps_api_key = 'AIzaSyAwKbIHeqAYrgDWY9m7Oa-XNMW1kqqe5To'
gmaps = googlemaps.Client(key=google_maps_api_key)


def extract_text_from_pdf(file_path):
    resource_manager = PDFResourceManager()
    output_stream = io.StringIO()
    laparams = pdfminer.layout.LAParams()
    device = TextConverter(resource_manager, output_stream, laparams=laparams)
    with open(file_path, 'rb') as file:
        interpreter = PDFPageInterpreter(resource_manager, device)
        for page in PDFPage.get_pages(file):
            interpreter.process_page(page)
    text = output_stream.getvalue()
    device.close()
    output_stream.close()
    return text

def count_words(text):
    words = text.split()
    return len(words)

def extract_text_from_ocr(file_path):

    # Replace with your API key
    api_key = "K86347531088957"
    api_url = "https://api.ocr.space/parse/image"
    language = "eng"
    # Define if you want the overlay (bounding box coordinates)
    is_overlay_required = False
    # Define the OCR Engine option
    ocr_engine = 2  # 2 corresponds to OCR Engine2
    # Define the Auto-enlarge content option
    auto_enlarge = True
    # Create a dictionary with the data to be sent in the request
    data = {
        "apikey": api_key,
        "language": language,
        "isOverlayRequired": is_overlay_required,
        "OCREngine": ocr_engine,
        "isTable": True,
        "detectOrientation": "true",  # Detect text orientation automatically
        "scale": auto_enlarge,  # Auto-enlarge content
    }
    files = [("file", (file_path, open(file_path, "rb")))]
    # Send the POST request to the API
    response = requests.post(api_url, files=files, data=data)
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        extracterd_text = data['ParsedResults'][0]['ParsedText']
        print("OCR.Space Extraction done")
        return extracterd_text
    else:
        print(f"Failed to extract text using OCR.Space API. Status code: {response.status_code}")
        return None
# Step 1: Extract text from the PDF
pdf_text = extract_text_from_pdf(file_name)

word_count = count_words(pdf_text)

if word_count > 100:
        print("words < 100")
        ocr_text = extract_text_from_ocr(file_name)
        # Get the base name of the PDF file (without extension)
        base_name = os.path.splitext(os.path.basename(file_name))[0]

        # Call the extract_text_from_ocr function to get OCR text
        ocr_text = extract_text_from_ocr(file_name)

        if ocr_text:
            # Define the path for the PDF file with the same name as the PDF but with ".pdf" extension
            pdf_file_path = f"{base_name}.pdf"

            # Create a PDF document
            doc = SimpleDocTemplate(pdf_file_path, pagesize=letter)
            elements = []

            # Create a style for the PDF content
            styles = getSampleStyleSheet()
            style_normal = styles["Normal"]

            # Add the OCR text to the PDF
            ocr_paragraph = Paragraph(ocr_text, style_normal)
            elements.append(ocr_paragraph)

            # Build the PDF document
            doc.build(elements)

            print(f"OCR text saved to {pdf_file_path}")
        else:
            print("OCR text extraction failed.")
        
        pdf_text = extract_text_from_pdf(pdf_file_path)
        ocr_text = pdf_text
else:
        print("words > 100")

        if len(pdf_text) > 10000:
            print("PDF text exceeds 10,000 characters. Truncating...")
        pdf_text = pdf_text[:10000]
        
        ocr_text = pdf_text

subprocess.call([sys.executable, "unique_rc.py", user_uid, file_name, ocr_text])
