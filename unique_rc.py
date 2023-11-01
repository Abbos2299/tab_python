import json
import math
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
from firebase_admin import db 
import subprocess

timestamp = datetime.now().strftime("%y%m%d%H%M%S")

cred = credentials.Certificate('tab-tools-firebase-adminsdk-8ncav-4f5ccee9af.json')
firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://tab-tools-default-rtdb.firebaseio.com/'
    })
db2 = firestore.client()

user_uid = sys.argv[1]
file_name = sys.argv[2]
text = sys.argv[3]

google_maps_api_key = 'AIzaSyAwKbIHeqAYrgDWY9m7Oa-XNMW1kqqe5To'
gmaps = googlemaps.Client(key=google_maps_api_key)

def generate_api_key():

    # Reference to the 'real_token' node in your database
    ref = db.reference('real_token')

    # Retrieve data from the 'real_token' node
    data = ref.get()

    # Iterate through the keys and values
    for key, value in data.items():
        if value < 1200:
            # Use this API key
            openai_api_key = key

            # Increment the value associated with the chosen key by 1
            ref.child(openai_api_key).set(value + 1)

            # Clean up when you're done
            firebase_admin.delete_app(firebase_admin.get_app())
            return openai_api_key

    # If no suitable key is found, return None or handle it as needed
    return None

def gpt_analyze(text):
    # Set your API key
    api_key = api_key_result
    openai.api_key = api_key

    # Define the parameters for your request
    parameters = {
        "model": "gpt-3.5-turbo",
        "temperature": 0.0,
        "messages": [
            # {"role": "system", "content": "You are working in logistics company with rate confirmations"},
            {"role": "user", "content": """
            Fetch following data and print in JSON format:
            json format:
            {
              "load_number": [],
              "broker_email": [],
              "load_pay": [],
              "addresses": [],
              "date_times": [],
              "all_emails": [],
              "all_addresses": []
            }
            1. Extract the load number;
            2. Extract Broker email address;
            3. Total "Load Pay" Amount;
            4. List all "Stops" full addresses in the order they appear in text;
            5. List all date and time information for each "Stops";
            6. Clean up the addresses from 4th (remove unnecessary parts);
            7. Clean up the date and time information from 5th and format as "dd/MM/yyyy HH:mm.".
            8. All Email addresses;
            9  All US addresses;
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

    # Use re.findall to find all matches of the pattern in the text
    data = json.loads(text)

    load_number = data["load_number"][0]
    broker_email = data["broker_email"][0]
    load_pay = data["load_pay"][0]
    if not load_pay.startswith("$"):
        load_pay = "$" + load_pay
    addresses = data["addresses"]
    date_times = data["date_times"]
    all_emails = data["all_emails"]
    all_addresses = data["all_addresses"]
    return {
        "Load number": load_number,
        "Broker email": broker_email,
        "Load Pay Amount": load_pay,
        "Stops": addresses,
        "Date Times": date_times,
        "all_emails": all_emails,
        "all_addresses": all_addresses,
    }

def process_date_times(date_times):
    processed_date_times = []

    for date_time in date_times:
        # Remove everything after a dash ('-')
        cleaned_date_time = re.sub(r'-.*$', '', date_time)
        
        # Remove unwanted symbols using regular expressions
        cleaned_date_time = re.sub(r'[@$]', '', cleaned_date_time)

        # Append the cleaned date_time to the list
        processed_date_times.append(cleaned_date_time)

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

def save_data_to_firestore(user_uid, file_name, LoadNumber, BrokerEmail, Rate, rounded_total_distance_miles, formatted_addresses, processed_date_times, all_emails, all_addresses):
    # Define the Firestore document data
    data = {
        'FileName': file_name,
        'LoadNumber': LoadNumber,
        'Rate': Rate,
        'Driver': user_uid,
        'BrokerEmail': BrokerEmail,
        'Submit BOL': 'no',
        'Broker Update': 'no',
        'Status': 'Active',
        'LoadMiles': rounded_total_distance_miles,
        'Path': timestamp,
        'PickUp': formatted_addresses[0],
        'Deliveries': formatted_addresses[1:],
        'PickUpTime': processed_date_times[0],
        'DeliveryTimes': processed_date_times[1:],
        'all_emails':all_emails,
        'all_addresses':all_addresses
    }

    # Get a reference to the Firestore user document
    user_ref = db2.collection('users').document(user_uid)

    # Create a new document in the "Loads" subcollection with the timestamp as the document name
    load_ref = user_ref.collection('Loads').document(timestamp)

    # Set the data for the document
    load_ref.set(data)



# Step !1: Get Open AI key
api_key_result = generate_api_key()
if api_key_result:
    print(f"Using API Key: {api_key_result}")
else:
    print("No suitable API key found.")


# Step 2: Call gpt_analyze with the extracted text
analyzed_text = gpt_analyze(text)

# Step 3: 
plain_text_response = convert_gpt_response(analyzed_text)

# Step 4: 
info = extract_info_from_text(plain_text_response)
print(info)

processed_date_times = process_date_times(info ["Date Times"])

# Step 5: 
# Call the function to list addresses from stops_content
address_list = list_addresses_from_stops(info["Stops"])
for i, address in enumerate(address_list, start=1):
    print(f"Address {i}: {address}")

# Step 6: 
formatted_addresses = format_addresses_with_google_maps(address_list, google_maps_api_key)
for i, formatted_address in enumerate(formatted_addresses, start=1):
    print(f"Formatted Address {i}: {formatted_address}")

# Step 7: Calculate the total distance between the addresses
total_distance_miles = calculate_total_distance(formatted_addresses, google_maps_api_key)
rounded_total_distance_miles = math.floor(total_distance_miles)
print(f"Total Distance (in miles): {rounded_total_distance_miles}")

# Step 8: 
# Call the function to save data to Firestore with load_number, broker_email, and load_pay values
save_data_to_firestore(user_uid, file_name, info["Load number"], info["Broker email"], info["Load Pay Amount"], rounded_total_distance_miles, formatted_addresses, processed_date_times, info["all_emails"], info["all_addresses"])

sys.exit()


