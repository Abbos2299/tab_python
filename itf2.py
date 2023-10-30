import sys
import io
import pdfminer
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
import re
from datetime import datetime
from dateutil import parser
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import googlemaps
import openai
from pdfminer.high_level import extract_text
import pyap
import requests
from firebase_admin import db
from firebase_admin import credentials, db


cred = credentials.Certificate("/Users/abbos/Developer/tab_python/tab-tools-firebase-adminsdk-8ncav-4f5ccee9af.json")
firebase_admin.initialize_app(cred, {
    'databaseURL': 'https://tab-tools-default-rtdb.firebaseio.com/'
})


timestamp = datetime.now().strftime("%y%m%d%H%M%S")

user_uid = sys.argv[1]
file_name = sys.argv[2]

# Initialize Google Maps client
google_maps_api_key = 'AIzaSyAwKbIHeqAYrgDWY9m7Oa-XNMW1kqqe5To'
gmaps = googlemaps.Client(key=google_maps_api_key)


def extract_text_from_pdf(file_path):

    # Replace with your API key
    api_key = "K86347531088957"
    api_url = "https://api.ocr.space/parse/image"
    language = "eng"
    # Define if you want the overlay (bounding box coordinates)
    is_overlay_required = False
    # Define the OCR Engine option
    ocr_engine = 1  # 1 corresponds to OCR Engine1
    # Define the Auto-enlarge content option
    auto_enlarge = True
    # Create a dictionary with the data to be sent in the request
    data = {
        "apikey": api_key,
        "language": language,
        "isOverlayRequired": is_overlay_required,
        "OCREngine": ocr_engine,
        "detectOrientation": "true",  # Detect text orientation automatically
        "scale": auto_enlarge,  # Auto-enlarge content
    }
    files = [("file", (file_path, open(file_path, "rb")))]
    # Send the POST request to the API
    response = requests.post(api_url, files=files, data=data)
    # Check if the request was successful
    if response.status_code == 200:
        result = response.json()   
        # Create a string to store the extracted text from all pages
        extracted_text = ""   
        # Extract text from all pages and remove line breaks
        for parsed_result in result.get("ParsedResults"):
            parsed_text = parsed_result.get("ParsedText")
            extracted_text += parsed_text
            extracted_text = extracted_text.replace("City, State, Zip", "")
            extracted_text = extracted_text.replace("Zip", "")
        # print(f"Extracted text saved to {extracted_text}")
          # Check if "Terms and Conditions" is in the extracted text
        if "Terms and Conditions" in extracted_text:
            # If found, truncate the text after that point
            extracted_text = extracted_text.split("Terms and Conditions")[0]    
        # print(extracted_text)
        return extracted_text
        
    else:
        print("Error: Unable to process the PDF. Status code:", response.status_code)

    

def gpt_analyze(extracted_text):
    # Set your API key
    api_key = "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"
    openai.api_key = api_key

    # Define the parameters for your request
    parameters = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.0,
        "messages": [
            {"role": "user", "content": """
                    Fetch following data:
                    1. Load number;
                    2. Company email address;
                    3. Last Total Agreed to Charges Amount;
                    4. First Pickup location;
                    5. List all Empty Trailer Pick Ups, Pick Ups and Deliveries locations without indexing;
                    6. List of dates and times for Empty Trailer Pick Up, Pick Up, and Deliveries. Include only one date and time for each event.;
                    7. Rewrite locations from request (5) in pyap format.;
             """},
            {"role": "assistant", "content": extracted_text},
            
        ],
    }

    # Calculate the token count of the entire conversation using the tiktoken library
    response = openai.ChatCompletion.create(**parameters)
    usage = response['usage']
    token_count = usage['total_tokens']

    # Print the assistant's reply
    print(response['choices'][0]['message']['content'])

    # Print the token count used in this request
    print("Token count for this request:", token_count)

    # Reference to the "real_token" node
    ref = db.reference('real_token')

    try:
        # Fetch the "used" value
        used_value = ref.child('used').get()
        if used_value is None:
            used_value = 0  # Initialize to 0 if it doesn't exist

        # Calculate the sum of used_value and token_count
        summed_value = used_value + token_count
        ref.child('used').set(summed_value)
    except Exception as e:
        # Handle the case where the path doesn't exist
        print("Path 'real_token/used' doesn't exist. Creating the path and setting the value.")
        summed_value = token_count
        ref.child('used').set(summed_value)

    # Clean up the Firebase app (only if you're done using it)
    firebase_admin.delete_app(firebase_admin.get_app())

    return response

def extract_addresses_from_response(response):
    # Extract the assistant's reply from the GPT-3 response
    assistant_reply = response['choices'][0]['message']['content']

    # Use pyap to extract addresses from the assistant's reply
    addresses = pyap.parse(assistant_reply, country='US')

    extracted_addresses = []
    for address in addresses:
        # Append the found address parts to the extracted_addresses list
        extracted_addresses.append(address.as_dict())

    return extracted_addresses


# Step 1: Extract text from the PDF
pdf_text = extract_text_from_pdf(file_name)

# Step 2: Call gpt_analyze with the extracted text
analyzed_text = gpt_analyze(pdf_text)

# Step 3:
response_from_gpt = analyzed_text  # Replace with the actual GPT-3 response

extracted_addresses = extract_addresses_from_response(response_from_gpt)

# Print only the 'full_address' values
for address in extracted_addresses:
    print(address['full_address'])




sys.exit()