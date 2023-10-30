import sys
import io
import pdfminer
from pdfminer.converter import TextConverter
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
import re
from datetime import datetime
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import googlemaps
import openai
import requests
import usaddress

timestamp = datetime.now().strftime("%y%m%d%H%M%S")

cred = credentials.Certificate(
    'tab-tools-firebase-adminsdk-8ncav-4f5ccee9af.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

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
        extracted_text = data['ParsedResults'][0]['ParsedText']
        print("OCR.Space Extraction done")
        return extracted_text
    else:
        print(f"Failed to extract text using OCR.Space API. Status code: {response.status_code}")
        return None

def gpt_analyze2(extracted_text):
    # Set your API key
    api_key = "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"
    openai.api_key = api_key

    # Define the parameters for your request
    parameters = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.0,
        "messages": [
            # {"role": "system", "content": "You are working in logistics company with rate confirmations"},
            {"role": "user", "content": """
             
            Fetch following data and print in JSON format:
                    1. Extract the load number;
                    2. Extract Broker email address;
                    3. Total "Load Pay" Amount;
                    4. List all "Stops" full address in the order they appear in text;
                    5. Take all addresses from 4th and remove all unnecessary parts, phones and etc;
                    6. List "Date Times" for each Stop from 4th request;
             """},
            {"role": "assistant", "content": extracted_text},
        ],
    }

    # Make a request to ChatGPT
    response = openai.ChatCompletion.create(**parameters)

    # Print the assistant's reply
    print(response['choices'][0]['message']['content'])
    return response

def gpt_analyze(text):
    # Set your API key
    api_key = "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"
    openai.api_key = api_key

    # Define the parameters for your request
    parameters = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.0,
        "messages": [
            # {"role": "system", "content": "You are working in logistics company with rate confirmations"},
            {"role": "user", "content": """
             
            Fetch following data and print in JSON format:
                    1. Extract the load number;
                    2. Extract Broker email address;
                    3. Total "Load Pay" Amount;
                    4. List all "Stops" full address in the order they appear in text;
                    5. List "Date Times" for each Stop from 4th request;
                    6. Take all addresses from 4th and remove all unnecessary parts, phones and etc;
                    7. Take all Date Times from 5th and remove all unnecessary parts, labels and etc;
             """},
            {"role": "assistant", "content": text},
        ],
    }

    # Make a request to ChatGPT
    response = openai.ChatCompletion.create(**parameters)

    # Print the assistant's reply
    print(response['choices'][0]['message']['content'])
    return response

def convert_gpt_response(response):
    # Extract the assistant's reply from the response
    assistant_reply = response['choices'][0]['message']['content']
    return assistant_reply

def extract_info_from_text(text):
    # Define regular expressions for extracting information
    load_number_pattern = r'"Load number":\s*"([^"]*)"'
    broker_email_pattern = r'"Broker email":\s*"([^"]*)"'
    load_pay_pattern = r'"Load Pay Amount":\s*"([^"]*)"'
    
    # Use regular expressions to find date-times and stops
    date_times_pattern = r'\[([^\]]*)\]'  # Matches content within square brackets
    date_times_match = re.findall(date_times_pattern, text)  # Find all matches within square brackets

    # Check if there are at least two matches (for Stops and Date Times)
    if len(date_times_match) >= 2:
        date_times_content = eval("[" + date_times_match[-1] + "]")
        stops_content = eval("[" + date_times_match[-2] + "]")
    else:
        stops_content = []
        date_times_content = []

    # Extract information using regular expressions
    load_number = re.search(load_number_pattern, text).group(1) if re.search(load_number_pattern, text) else None
    broker_email = re.search(broker_email_pattern, text).group(1) if re.search(broker_email_pattern, text) else None
    load_pay = re.search(load_pay_pattern, text).group(1) if re.search(load_pay_pattern, text) else None

    return {
        "Load number": load_number,
        "Broker email": broker_email,
        "Load Pay Amount": load_pay,
        "Stops": stops_content,
        "Date Times": date_times_content
    }

def process_date_times(date_times):
    processed_date_times = []
    for date_time in date_times:
        date_time_parts = date_time.split('-')
        if len(date_time_parts) == 1:
            # Single date-time, add it as is
            processed_date_times.append(date_time)
        else:
            # Date-time range, add only the first date-time
            processed_date_times.append(date_time_parts[0].strip())
    return processed_date_times

def list_addresses_from_stops(stops_content):
    addresses = []
    for stop in stops_content:
        try:
            address, _ = usaddress.tag(stop)
            formatted_address = ' '.join([v for k, v in address.items()])
            addresses.append(formatted_address)
        except usaddress.RepeatedLabelError:
            # Handle repeated labels in the address, if any
            pass
    return addresses

def format_addresses_with_google_maps(address_list, api_key):
    gmaps = googlemaps.Client(key=api_key)
    formatted_addresses = []

    for address in address_list:
        # Geocode the address to get its details
        geocode_result = gmaps.geocode(address)

        if geocode_result:
            # Extract the formatted address from the result
            formatted_address = geocode_result[0]['formatted_address']
            formatted_addresses.append(formatted_address)
        else:
            # If no result is found, add the original address to the list
            formatted_addresses.append(address)

    return formatted_addresses

def calculate_total_distance(addresses, api_key):
    total_distance = 0
    num_addresses = len(addresses)

    if num_addresses < 2:
        return 0  # There's no distance to calculate with less than 2 addresses

    gmaps = googlemaps.Client(key=api_key)

    for i in range(num_addresses - 1):
        origin = addresses[i]
        destination = addresses[i + 1]

        # Make a request to the Google Maps Distance Matrix API
        distance_matrix = gmaps.distance_matrix(origin, destination, units="imperial")  # Specify units as imperial for miles

        # Extract the distance value from the response
        if 'rows' in distance_matrix and len(distance_matrix['rows']) > 0:
            row = distance_matrix['rows'][0]
            if 'elements' in row and len(row['elements']) > 0:
                element = row['elements'][0]
                if 'distance' in element and 'value' in element['distance']:
                    distance_value = element['distance']['value']
                    total_distance += distance_value

    # Convert the total distance from meters to a more appropriate unit (e.g., kilometers)
    total_distance_miles = total_distance / 1609.34

    return total_distance_miles

def save_data_to_firestore(user_uid, file_name, info, rounded_total_distance_miles, formatted_addresses, processed_date_times):
    # Define the Firestore document data
    data = {
        'FileName': file_name,
        'LoadNumber': info["Load number"],
        'Rate': info["Load Pay Amount"],
        'Driver': user_uid,
        'BrokerEmail': info["Broker email"],
        'Submit BOL': 'no',
        'Broker Update': 'no',
        'Status': 'Active',
        'LoadMiles': rounded_total_distance_miles,
        'Path': timestamp,
        'PickUp': formatted_addresses[0],
        'Deliveries': formatted_addresses[1:],
        'PickUpTime': processed_date_times[0],
        'DeliveryTimes': processed_date_times[1:]
    }

    # Get a reference to the Firestore user document
    user_ref = db.collection('users').document(user_uid)

    # Create a new document in the "Loads" subcollection with the timestamp as the document name
    load_ref = user_ref.collection('Loads').document(timestamp)

    # Set the data for the document
    load_ref.set(data)

# Step 1: Extract text from the PDF
pdf_text = extract_text_from_pdf(file_name)

word_count = count_words(pdf_text)

if word_count < 100:
        print("words < 100")
        ocr_text = extract_text_from_ocr(file_name)
        analyzed_text = gpt_analyze2(ocr_text)
else:
        print("words > 100")
        # Step 2: Call gpt_analyze with the extracted text
        analyzed_text = gpt_analyze(pdf_text)

# Step 3: 
plain_text_response = convert_gpt_response(analyzed_text)

# Step 4: 
info = extract_info_from_text(plain_text_response)
print(info)

# Step 5: Process the date_times
processed_date_times = process_date_times(info["Date Times"])
for i, date_time in enumerate(processed_date_times, start=1):
    print(f"Processed Date Time {i}: {date_time}")
   
# Step 6: 
# Call the function to list addresses from stops_content
address_list = list_addresses_from_stops(info["Stops"])
for i, address in enumerate(address_list, start=1):
    print(f"Address {i}: {address}")

# Step 7: 
formatted_addresses = format_addresses_with_google_maps(address_list, google_maps_api_key)
for i, formatted_address in enumerate(formatted_addresses, start=1):
    print(f"Formatted Address {i}: {formatted_address}")

# Step 8: Calculate the total distance between the addresses
total_distance_miles = calculate_total_distance(formatted_addresses, google_maps_api_key)
rounded_total_distance_miles = round(total_distance_miles, 2)
print(f"Total Distance (in miles): {rounded_total_distance_miles}")

# Step 9: 
# Call the function to save data to Firestore
save_data_to_firestore(user_uid, file_name, info, rounded_total_distance_miles, formatted_addresses, processed_date_times)

sys.exit()


