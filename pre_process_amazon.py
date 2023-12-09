import subprocess
import sys
from PIL import Image
import googlemaps
import pytesseract
from pdf2image import convert_from_path
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore


cred = credentials.Certificate('tab-tools-firebase-adminsdk-8ncav-4f5ccee9af.json')
firebase_admin.initialize_app(cred, {
        'databaseURL': 'https://tab-tools-default-rtdb.firebaseio.com/'
    })
db2 = firestore.client()
user_uid = sys.argv[1]
file_name = sys.argv[2]
# Path to your scanned PDF file

google_maps_api_key = 'AIzaSyAwKbIHeqAYrgDWY9m7Oa-XNMW1kqqe5To'
gmaps = googlemaps.Client(key=google_maps_api_key)

# Convert PDF pages to images

pages = convert_from_path(file_name, 300)  # 300 is the DPI (adjust if needed)

# Extract text from each page
extracted_text = ''
for page in pages:
    text = pytesseract.image_to_string(page, lang='eng')  # Change 'eng' to the language of your PDF if needed
    extracted_text += text + '\n'

# Output the extracted text
print(extracted_text)


subprocess.call([sys.executable, "unique_rc_amazon.py", user_uid, file_name, extracted_text])
