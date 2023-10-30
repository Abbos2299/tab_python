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

timestamp = datetime.now().strftime("%y%m%d%H%M%S")

# Initialize Firebase credentials
cred = credentials.Certificate(
    'tab-tools-firebase-adminsdk-8ncav-4f5ccee9af.json')
firebase_admin.initialize_app(cred)
db = firestore.client()

user_uid = sys.argv[1]
file_name = sys.argv[2]

# Initialize Google Maps client
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


def apply_regex_rules(text):
    load_number = re.search(r'Carrier Confirmation for Load (.+)', text)
    rate = re.search(r'Total Rate:(.+)', text)
    broker_email = re.search(r'J.B. Hunt Contact\n.+?\n(.+)', text)
    broker_email_address = broker_email.group(1) if broker_email else None
    if broker_email_address:
        email_match = re.search(
            r'Email:\s?([\w\.-]+@[\w\.-]+)', broker_email_address)
        if email_match:
            broker_email_address = email_match.group(1)
        elif re.match(r'^[\w\.-]+@[\w\.-]+$', broker_email_address):
            pass
        else:
            broker_email_address = None
    pick_up_info = re.search(
        r'Shipper\s?:?\s?1\n(.+?)\n(.+?)\n(.+?)\n', text, re.DOTALL)
    pick_up = ' '.join(pick_up_info.groups()) if pick_up_info else None
    pick_up_time = re.search(r'Pickup\n(.+)', text)
    pick_up_t = pick_up_time.group(1) if pick_up_time else None

    consignee_regex = r'Consignee # (\d+)\n(.+?)\n(.+?)\n(.+?)\n'
    consignees = re.findall(consignee_regex, text, re.DOTALL)
    consignee_location = ['\n'.join(consignee[1:]) for consignee in consignees]

    delivery_info = re.findall(r'Delivery\n(.+)', text)
    delivery_times = delivery_info[:-1]  # Exclude the last occurrence

    return (
        load_number.group(1) if load_number else None,
        rate.group(1) if rate else None,
        broker_email_address,
        pick_up,
        pick_up_t,
        consignee_location,
        delivery_times,
    )
def processing_date_times(pick_up_t):
    processed_PU_time = []
    for date_time in pick_up_t:
        date_time_parts = date_time.split('-')
        if len(date_time_parts) == 1:
            # Single date-time, add it as is
            processed_PU_time.append(date_time)
        else:
            # Date-time range, add only the first date-time
            processed_PU_time.append(date_time_parts[0].strip())
    return processed_PU_time

def process_date_times(delivery_times):
    processed_DEL_times = []
    for date_time in delivery_times:
        date_time_parts = date_time.split('-')
        if len(date_time_parts) == 1:
            # Single date-time, add it as is
            processed_DEL_times.append(date_time)
        else:
            # Date-time range, add only the first date-time
            processed_DEL_times.append(date_time_parts[0].strip())
    return processed_DEL_times

def calculate_driving_distance(locations):
    total_distance = 0.0
    for i in range(len(locations) - 1):
        origin = locations[i]
        destination = locations[i + 1]
        directions = gmaps.directions(
            origin, destination, mode="driving", units="imperial")
        if directions:
            # Convert meters to miles
            distance_miles = directions[0]['legs'][0]['distance']['value'] * 0.000621371
            total_distance += distance_miles
    return total_distance


def save_result_to_firebase(load_number, rate, broker_email, pick_up, processed_pick_up_times, consignee_location, processed_delivery_times, full_distance):
    

    loads_ref = db.collection('users').document(user_uid).collection('Loads')

    # Create a new load document
    load_doc_ref = loads_ref.document(timestamp)

    full_distance_int = int(
        full_distance) if full_distance is not None else None

    # Save the extracted information to the load document
    load_doc_ref.set({
        'FileName': file_name,
        'LoadNumber': load_number,
        'Rate': rate,
        'BrokerEmail': broker_email,
        'LoadMiles': full_distance_int,
        'PickUp': processed_pick_up_times,
        'PickUpTime': pick_up_t,
        'Deliveries': consignee_location,
        'DeliveryTimes': processed_delivery_times,
        'Status': 'Active',
        'Path': timestamp,
        'Submit BOL': 'no',
        'Broker Update': 'no',
        'Driver': user_uid,
    })

def add_timestamp_field_to_user_document(user_uid, timestamp):
    user_doc_ref = db.collection('load_group').document(user_uid)

    # Check if the document exists
    user_doc = user_doc_ref.get()

    if user_doc.exists:
        # Update the document with the timestamp field
        user_doc_ref.update({
            timestamp: 'Load'
        })
    else:
        # If the document doesn't exist, create it and set the timestamp field
        user_doc_ref.set({
            timestamp: 'Load'
        })

# Call the function to add the timestamp field
add_timestamp_field_to_user_document(user_uid, timestamp)

# Extract text from the PDF
pdf_text = extract_text_from_pdf(file_name)

# Apply regex rules to extract information
(
    load_number, rate, broker_email, pick_up, pick_up_t, consignee_location, delivery_times
) = apply_regex_rules(pdf_text)

# Process pick-up times
processed_pick_up_times = processing_date_times(pick_up_t)

# Process delivery times
processed_delivery_times = process_date_times(delivery_times)

# Calculate the driving distance between locations
if pick_up and consignee_location:
    all_locations = [pick_up] + consignee_location
    full_distance = calculate_driving_distance(all_locations)
else:
    full_distance = None
    print('error')


# Save the result to Firebase
# Save the result to Firebase
save_result_to_firebase(
    load_number, rate, broker_email, pick_up, processed_pick_up_times, consignee_location, processed_delivery_times, full_distance
)


sys.exit()