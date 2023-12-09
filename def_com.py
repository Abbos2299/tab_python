import os
import re
import subprocess
import sys
from flask import Flask, request
import firebase_admin
from firebase_admin import credentials
from firebase_admin import storage
from datetime import timedelta
import requests
import time
import urllib.parse
from pdfminer.high_level import extract_text

app = Flask(__name__)
cred = credentials.Certificate(
    'tab-tools-firebase-adminsdk-8ncav-4f5ccee9af.json')
firebase_admin.initialize_app(cred)


@app.route('/launchidentify', methods=['GET'])
def launch_python_file():
    user_uid = request.args.get('uid')

    bucket_name = 'tab-tools.appspot.com'
    bucket = storage.bucket(bucket_name)
    folder_name = user_uid  # Replace with the appropriate user UID

    blobs = bucket.list_blobs(prefix=folder_name)

    time.sleep(1)

    broker_name = None  # Initialize broker_name
    last_added_blob = None

    for blob in blobs:
        if not last_added_blob or blob.updated > last_added_blob.updated:
            last_added_blob = blob

    if last_added_blob:
        file_name = urllib.parse.unquote(last_added_blob.name.split(
            '/')[-1])  # Get the file name from the blob URL
        file_url = last_added_blob.generate_signed_url(
            expiration=timedelta(minutes=15))

        # Download the file from Firebase
        response = requests.get(file_url)
        with open(file_name, 'wb') as f:
            f.write(response.content)


        context_text = extract_text(file_name)
        # print(context_text)

        broker_companies = [
        "AAA Truck Truck Truck",
        ]

        # Initialize a dictionary to count the occurrences of each broker company
        broker_counts = {company: 0 for company in broker_companies}

        # Search for matches with broker companies
        for company in broker_companies:
            matches = re.findall(r'\b' + re.escape(company) +
                         r'\b', context_text, flags=re.IGNORECASE)
            count = len(matches)
            broker_counts[company] = count

        # Find the most used broker company
        most_used_broker = max(broker_counts, key=broker_counts.get)

        if broker_counts[most_used_broker] > 0:
            print(most_used_broker)
          
        else:
            print("RC don't identified")
            subprocess.call([sys.executable, "pre_process.py", user_uid, file_name])

    os.remove(file_name)
    return 'Success'

@app.route('/launchamazonidentify', methods=['GET'])
def launch_amazon_file():
    user_uid = request.args.get('uid')

    bucket_name = 'tab-tools.appspot.com'
    bucket = storage.bucket(bucket_name)
    folder_name = user_uid  # Replace with the appropriate user UID

    blobs = bucket.list_blobs(prefix=folder_name)

    time.sleep(1)

    broker_name = None  # Initialize broker_name
    last_added_blob = None

    for blob in blobs:
        if not last_added_blob or blob.updated > last_added_blob.updated:
            last_added_blob = blob

    if last_added_blob:
        file_name = urllib.parse.unquote(last_added_blob.name.split(
            '/')[-1])  # Get the file name from the blob URL
        file_url = last_added_blob.generate_signed_url(
            expiration=timedelta(minutes=15))

        # Download the file from Firebase
        response = requests.get(file_url)
        with open(file_name, 'wb') as f:
            f.write(response.content)


        context_text = extract_text(file_name)
        # print(context_text)

        broker_companies = [
        "AAA Truck Truck Truck",
        ]

        # Initialize a dictionary to count the occurrences of each broker company
        broker_counts = {company: 0 for company in broker_companies}

        # Search for matches with broker companies
        for company in broker_companies:
            matches = re.findall(r'\b' + re.escape(company) +
                         r'\b', context_text, flags=re.IGNORECASE)
            count = len(matches)
            broker_counts[company] = count

        # Find the most used broker company
        most_used_broker = max(broker_counts, key=broker_counts.get)

        if broker_counts[most_used_broker] > 0:
            print(most_used_broker)
          
        else:
            print("RC don't identified")
            subprocess.call([sys.executable, "pre_process_amazon.py", user_uid, file_name])

    os.remove(file_name)
    return 'Success'

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
