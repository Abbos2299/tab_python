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
        "AFC Brokerage",
        "AFC Logistics",
        "AIT Truckload",
        "AIT Worldwide",
        "Allen Lund",
        "Alliance Highway",
        "ALLY LOGISTICS",
        "AM Transport",
        "American Group",
        "American Sugar",
        "American Transport Group",
        "Amsino",
        "Amstan Logistics",
        "ArcBest Corp",
        "Achest",
        "Archerhub",
        "Sunset Transportation",
        "Armstrong Transport",
        "Arrive Logistics",
        "ASCEND",
        "Ascent Global",
        "Ashley Distribution",
        "ATS Logistics",
        "axlelogistics",
        "B. R. Williams",
        "BAT Logistics",
        "Bay & Bay",
        "Becker Logistics",
        "Beemac Logistics",
        "Best Logistics",
        "BFT Trucking",
        "Blue Marlin Logistics",
        "BlueGrace Logistics",
        "BM2 Freight",
        "BMM Logistics",
        "BNSF Logistics",
        "Buchanan Logistics",
        "BZS TRANSPORT",
        "C.H. Robinson",
        "C.L. Services",
        "C&L",
        "Capable Transport",
        "CAPITAL LOGISTICS",
        "Capstone Logistics",
        "Cardinal Logistics",
        "CarrierHawk",
        "Centerstone",
        "Chariot Logistics",
        "Circle Logistics",
        "Commodity Transportation",
        "Concept International",
        "Confiance LLC",
        "Convoy",
        "Cornerstone Systems",
        "Corporate Traffic",
        "Covenant Transport",
        "Cowan Logistics",
        "COYOTE",
        "Creech Brokerage",
        "CRST The Transportation",
        "Custom Pro",
        "CW Carriers",
        "Czechmate",
        "D2 FREIGHT",
        "Day & Ross",
        "DestiNATION Transport",
        "DIAMOND LOGISTICS",
        "Direct Connect Logistix",
        "Direct Connect Transport",
        "DSV A/S",
        "Dupre Logistics",
        "DYNAMIC LOGISTIX",
        "Dynamo Freight",
        "Ease Logistics",
        "EASE Logistics Services",
        "Echo Global",
        "Edge Logistics",
        "ELISqutions",
        "ELITE TRANSITSOLU",
        "emergemarket",
        "englandlogistics",
        "eShipping",
        "Evans Delivery",
        "EVE INTERNATIONAL",
        "everest",
        "EXPRESS LOGISTICS",
        "Fastmore",
        "FEDEX CUSTOM CRITICAL",
        "Fifth Wheel Freight",
        "FitzMark",
        "FLS Transportation",
        "freedomtransusa",
        "Freezpak Logistics",
        "FreightEx Logistics",
        "Frontier Logistics",
        "Genpro Inc.",
        "GIX Logistics",
        "GlobalTranz",
        "G02 EXPRESS",
        "GulfRelay",
        "Haines City Truck",
        "Hazen Transfer",
        "High Tide Logistics",
        "HTS Logistics",
        "Hub Group",
        "InstiCo",
        "Integrity Express",
        "ITF LOGISTICS GROUP",
        "ITS Logistics",
        "J.B. Hunt",
        "JEAR Logistics",
        "jerue Companies",
        "Johanson Transportation",
        "John J. Jerue Truck",
        "K & L FREIGHT",
        "KAG Logistics",
        "Keller Freight Solutions",
        "Kenco Transportation",
        "Kirsch Transportation",
        "Kiss Logistics",
        "KLG Logistics Services",
        "Knight-Swift Transportation",
        "Koch Logistics",
        "Kodiak Transportation",
        "Koola Logistics",
        "Landmark Logistics",
        "LandStar Global",
        "LANDSTAR INWAY",
        "Landstar",
        "Landstar Ranger",
        "LIBERTY",
        "LinQ Transport",
        "Loadsmart",
        "Logistic Dynamics",
        "Logistics One Brokerage",
        "Logistics Plus",
        "Longship",
        "Magellan Transport",
        "Marathon Transport",
        "Marten Transport",
        "Matson Logistics",
        "Max Trans Logistics",
        "McLeod Logistics",
        "MDB Logistics",
        "Meadow Lark Agency",
        "MegaCorp Logistics",
        "MIDWEST EXPRESS FREIGHT",
        "Mode Global",
        "Moeller Logistics",
        "MoLo Solutions",
        "Motus Freight",
        "Nationwide Logistics",
        "Navajo Expedited",
        "Network Transport",
        "NFI",
        "NTG",
        "NORTH EAST LOGISTICS",
        "ODW Logistics",
        "Old Frontier Family",
        "OpenRoad Transportation",
        "Packer Transponallun",
        "PAM Transport",
        "PATHMARK TRANSPORTATION",
        "Patterson Companies",
        "Paul Logistics",
        "Payne Trucking",
        "PEPSI LOGISTICS",
        "Performance Logistics",
        "Perimeter Logistics",
        "PHOENIX SUPPLY",
        "PINK PANTHERS",
        "PLS",
        "Priority 1",
        "R&R FREIGHT",
        "R2 Logistics",
        "Radiant Logistics",
        "RB Humphreys",
        "Red Classic",
        "Redwood",
        "REED TRANSPORT",
        "RTS",
        "RFX",
        "RJ Logistics",
        "RJ S",
        "RLS Logistics",
        "ROAR LOGISTICS",
        "ROYAL TRANSPORTATION",
        "RPM carrier",
        "RPM Freight Systems",
        "RXO, Inc.",
        "RYAN TRANSPORTATION",
        "Ryder Supply Chain",
        "S & H Transport",
        "S and S Nationwide",
        "SCAN GLOBAL",
        "Schneider",
        "Schneider Shipment",
        "Scotlynn USA Division",
        "Sim Ie Lo istics,LLC",
        "Spartan Logistics",
        "SP1 Logistics",
        "Spirit Logistics",
        "spotinc",
        "ST Freight",
        "Starland Global Logistics",
        "Steam Logistics",
        "Summit E1even",
        "Sunrise Logistics",
        "Surge Transportation",
        "Synchrogistics",
        "TA Services",
        "Tallgrass Freight",
        "TAYLOR LOGISTICS",
        "TERRY ENTERPRISES",
        "The Worthington Company",
        "Thomas E. Keller Trucking",
        "TII Logistics",
        "TORCH LOGISTICS",
        "Torch3pl",
        "Total Quality Logistics",
        "TRAFFIX",
        "Trailer Bridge",
        "TransAm Logistics",
        "Transfix",
        "TRANSLOOP",
        "Transplace",
        "Trident Transport",
        "Trinity Logistics",
        "Triple T Transport",
        "U.S. Xpress",
        "Uber Freight",
        "UNIVERSAL CAPACITY",
        "Universal Logistics",
        "Unlimited Logistics",
        "US Logistics",
        "US1 Network",
        "USAT Logistics",
        "Value Logistics",
        "Venture Connect",
        "VERIHA LOGISTICS",
        "Veritiv Logistics",
        "Watco Logistics",
        "Werner Enterprises",
        "West Motor Freight",
        "NORTHEAST LOGISTICS",
        "XPO Logistics",
        "Yellow Logistics",
        "Zengistics",
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
        
        if most_used_broker == "AFC Brokerage":
            script_name = "1.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "AFC Logistics":
            script_name = "2.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "AIT Truckload":
            script_name = "3.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "AIT Worldwide":
            script_name = "4.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Allen Lund":
            script_name = "5.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Alliance Highway":
            script_name = "6.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "ALLY LOGISTICS":
            script_name = "7.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "AM Transport":
            script_name = "8.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "American Group":
            script_name = "9.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "American Sugar":
            script_name = "10.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "American Transport Group":
            script_name = "11.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Amsino":
            script_name = "12.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Amstan Logistics":
            script_name = "13.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "ArcBest Corp":
            script_name = "14.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Achest":
            script_name = "15.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Archerhub":
            script_name = "16.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])
        
        if most_used_broker == "Sunset Transportation":
            script_name = "17.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Armstrong Transport":
            script_name = "18.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Arrive Logistics":
            script_name = "19.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "ASCEND":
            script_name = "20.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Ascent Global":
            script_name = "21.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Ashley Distribution":
            script_name = "22.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "ATS Logistics":
            script_name = "23.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "axlelogistics":
            script_name = "24.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "B. R. Williams":
            script_name = "25.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "BAT Logistics":
            script_name = "26.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Bay & Bay":
            script_name = "27.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Becker Logistics":
            script_name = "28.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Beemac Logistics":
            script_name = "29.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Best Logistics":
            script_name = "30.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "BFT Trucking":
            script_name = "31.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Blue Marlin Logistics":
            script_name = "32.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "BlueGrace Logistics":
            script_name = "33.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "BM2 Freight":
            script_name = "34.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "BMM Logistics":
            script_name = "35.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "BNSF Logistics":
            script_name = "36.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Buchanan Logistics":
            script_name = "37.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "BZS TRANSPORT":
            script_name = "38.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "C.H. Robinson":
            script_name = "39.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "C.L. Services":
            script_name = "40.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "C&L":
            script_name = "41.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Capable Transport":
            script_name = "42.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "CAPITAL LOGISTICS":
            script_name = "43.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Capstone Logistics":
            script_name = "44.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Cardinal Logistics":
            script_name = "45.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "CarrierHawk":
            script_name = "46.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Centerstone":
            script_name = "47.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Chariot Logistics":
            script_name = "48.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])
        
        if most_used_broker == "Circle Logistics":
            script_name = "49.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Commodity Transportation":
            script_name = "50.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Concept International":
            script_name = "51.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Confiance LLC":
            script_name = "52.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Convoy":
            script_name = "53.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Cornerstone Systems":
            script_name = "54.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Corporate Traffic":
            script_name = "55.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Covenant Transport":
            script_name = "56.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Cowan Logistics":
            script_name = "57.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "COYOTE":
            script_name = "58.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Creech Brokerage":
            script_name = "59.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "CRST The Transportation":
            script_name = "60.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Custom Pro":
            script_name = "61.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "CW Carriers":
            script_name = "62.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Czechmate":
            script_name = "63.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "D2 FREIGHT":
            script_name = "64.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Day & Ross":
            script_name = "65.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "DestiNATION Transport":
            script_name = "66.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "DIAMOND LOGISTICS":
            script_name = "67.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Direct Connect Logistix":
            script_name = "68.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Direct Connect Transport":
            script_name = "69.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "DSV A/S":
            script_name = "70.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Dupre Logistics":
            script_name = "71.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "DYNAMIC LOGISTIX":
            script_name = "72.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Dynamo Freight":
            script_name = "73.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Ease Logistics":
            script_name = "74.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "EASE Logistics Services":
            script_name = "75.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Echo Global":
            script_name = "76.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Edge Logistics":
            script_name = "77.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "ELISqutions":
            script_name = "78.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "ELITE TRANSITSOLU":
            script_name = "79.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "emergemarket":
            script_name = "80.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])
        
        if most_used_broker == "englandlogistics":
            script_name = "81.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "eShipping":
            script_name = "82.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Evans Delivery":
            script_name = "83.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "EVE INTERNATIONAL":
            script_name = "84.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "everest":
            script_name = "85.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "EXPRESS LOGISTICS":
            script_name = "86.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Fastmore":
            script_name = "87.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "FEDEX CUSTOM CRITICAL":
            script_name = "88.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Fifth Wheel Freight":
            script_name = "89.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "FitzMark":
            script_name = "90.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "FLS Transportation":
            script_name = "91.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "freedomtransusa":
            script_name = "92.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Freezpak Logistics":
            script_name = "93.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "FreightEx Logistics":
            script_name = "94.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Frontier Logistics":
            script_name = "95.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Genpro Inc.":
            script_name = "96.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "GIX Logistics":
            script_name = "97.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "GlobalTranz":
            script_name = "98.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "G02 EXPRESS":
            script_name = "99.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "GulfRelay":
            script_name = "100.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Haines City Truck":
            script_name = "101.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Hazen Transfer":
            script_name = "102.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "High Tide Logistics":
            script_name = "103.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "HTS Logistics":
            script_name = "104.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Hub Group":
            script_name = "105.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "InstiCo":
            script_name = "106.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Integrity Express":
            script_name = "107.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "ITS Logistics":
            script_name = "108.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "JEAR Logistics":
            script_name = "109.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "jerue Companies":
            script_name = "110.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Johanson Transportation":
            script_name = "111.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "John J. Jerue Truck":
            script_name = "112.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])
        
        if most_used_broker == "K & L FREIGHT":
            script_name = "113.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "KAG Logistics":
            script_name = "114.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Keller Freight Solutions":
            script_name = "115.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Kenco Transportation":
            script_name = "116.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Kirsch Transportation":
            script_name = "117.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Kiss Logistics":
            script_name = "118.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "KLG Logistics Services":
            script_name = "119.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Knight-Swift Transportation":
            script_name = "120.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Koch Logistics":
            script_name = "121.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Kodiak Transportation":
            script_name = "122.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Koola Logistics":
            script_name = "123.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Landmark Logistics":
            script_name = "124.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "LandStar Global":
            script_name = "125.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "LANDSTAR INWAY":
            script_name = "126.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "LIBERTY":
            script_name = "127.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "LinQ Transport":
            script_name = "128.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Loadsmart":
            script_name = "129.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Logistic Dynamics":
            script_name = "130.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Logistics One Brokerage":
            script_name = "131.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Logistics Plus":
            script_name = "132.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Longship":
            script_name = "133.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Magellan Transport":
            script_name = "134.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Marathon Transport":
            script_name = "135.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Marten Transport":
            script_name = "136.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Matson Logistics":
            script_name = "137.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Max Trans Logistics":
            script_name = "138.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "McLeod Logistics":
            script_name = "139.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "MDB Logistics":
            script_name = "140.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Meadow Lark Agency":
            script_name = "141.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "MegaCorp Logistics":
            script_name = "142.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "MIDWEST EXPRESS FREIGHT":
            script_name = "143.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Mode Global":
            script_name = "144.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])
        
        if most_used_broker == "Moeller Logistics":
            script_name = "145.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "MoLo Solutions":
            script_name = "146.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Motus Freight":
            script_name = "147.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Nationwide Logistics":
            script_name = "148.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Navajo Expedited":
            script_name = "149.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Network Transport":
            script_name = "150.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "NFI":
            script_name = "151.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "NTG":
            script_name = "152.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "NORTHEAST LOGISTICS":
            script_name = "153.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "ODW Logistics":
            script_name = "154.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Old Frontier Family":
            script_name = "155.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "OpenRoad Transportation":
            script_name = "156.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Packer Transponallun":
            script_name = "157.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "PAM Transport":
            script_name = "158.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "PATHMARK TRANSPORTATION":
            script_name = "159.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Patterson Companies":
            script_name = "160.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Paul Logistics":
            script_name = "161.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Payne Trucking":
            script_name = "162.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "PEPSI LOGISTICS":
            script_name = "163.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Performance Logistics":
            script_name = "164.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Perimeter Logistics":
            script_name = "165.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "PHOENIX SUPPLY":
            script_name = "166.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "PINK PANTHERS":
            script_name = "167.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "PLS":
            script_name = "168.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Priority 1":
            script_name = "169.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "R&R FREIGHT":
            script_name = "170.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "R2 Logistics":
            script_name = "171.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Radiant Logistics":
            script_name = "172.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "RB Humphreys":
            script_name = "173.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Red Classic":
            script_name = "174.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Redwood":
            script_name = "175.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "REED TRANSPORT":
            script_name = "176.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])
        
        if most_used_broker == "RTS":
            script_name = "177.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "RFX":
            script_name = "178.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "RJ Logistics":
            script_name = "179.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "RJ S":
            script_name = "180.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "RLS Logistics":
            script_name = "181.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "ROAR LOGISTICS":
            script_name = "182.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "ROYAL TRANSPORTATION":
            script_name = "183.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "RPM carrier":
            script_name = "184.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "RPM Freight Systems":
            script_name = "185.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "RXO, Inc.":
            script_name = "186.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "RYAN TRANSPORTATION":
            script_name = "187.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Ryder Supply Chain":
            script_name = "188.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "S & H Transport":
            script_name = "189.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "S and S Nationwide":
            script_name = "190.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "SCAN GLOBAL":
            script_name = "191.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Schneider":
            script_name = "192.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Schneider Shipment":
            script_name = "193.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Scotlynn USA Division":
            script_name = "194.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Sim Ie Lo istics,LLC":
            script_name = "195.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Spartan Logistics":
            script_name = "196.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "SP1 Logistics":
            script_name = "197.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Spirit Logistics":
            script_name = "198.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "spotinc":
            script_name = "199.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "ST Freight":
            script_name = "200.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Starland Global Logistics":
            script_name = "201.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Steam Logistics":
            script_name = "202.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Summit E1even":
            script_name = "203.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Sunrise Logistics":
            script_name = "204.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Surge Transportation":
            script_name = "205.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Synchrogistics":
            script_name = "206.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "TA Services":
            script_name = "207.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Tallgrass Freight":
            script_name = "208.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])
        
        if most_used_broker == "TAYLOR LOGISTICS":
            script_name = "209.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "TERRY ENTERPRISES":
            script_name = "210.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "The Worthington Company":
            script_name = "211.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Thomas E. Keller Trucking":
            script_name = "212.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "TII Logistics":
            script_name = "213.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "TORCH LOGISTICS":
            script_name = "214.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Torch3pl":
            script_name = "215.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Total Quality Logistics":
            script_name = "216.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "TRAFFIX":
            script_name = "217.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Trailer Bridge":
            script_name = "218.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "TransAm Logistics":
            script_name = "219.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Transfix":
            script_name = "220.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "TRANSLOOP":
            script_name = "221.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Transplace":
            script_name = "222.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Trident Transport":
            script_name = "223.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Trailer Bridge":
            script_name = "224.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Trinity Logistics":
            script_name = "225.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Triple T Transport":
            script_name = "226.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "U.S. Xpress":
            script_name = "227.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Uber Freight":
            script_name = "228.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "UNIVERSAL CAPACITY":
            script_name = "229.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Universal Logistics":
            script_name = "230.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Unlimited Logistics":
            script_name = "231.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "US Logistics":
            script_name = "232.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "US1 Network":
            script_name = "233.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "USAT Logistics":
            script_name = "234.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Value Logistics":
            script_name = "235.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Venture Connect":
            script_name = "236.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "VERIHA LOGISTICS":
            script_name = "237.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Veritiv Logistics":
            script_name = "238.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Johanson Transportation":
            script_name = "239.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Werner Enterprises":
            script_name = "240.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])
        
        if most_used_broker == "West Motor Freight":
            script_name = "241.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Worldwide Express":
            script_name = "242.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "XPO Logistics":
            script_name = "243.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Yellow Logistics":
            script_name = "244.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "Zengistics":
            script_name = "245.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        if most_used_broker == "ITF LOGISTICS GROUP":
            script_name = "itf.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])

        elif most_used_broker == "J.B. Hunt":
            script_name = "j.b.hunt.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])
        
        elif most_used_broker == "Landstar Ranger":
            script_name = "landstar.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])
        
        elif most_used_broker == "Landstar":
            script_name = "landstar.py"
            if script_name not in os.listdir():
                script_name = "unique_rc.py"
            subprocess.call([sys.executable, script_name, user_uid, file_name])
            
        else:
            print("RC don't identified")
            subprocess.call([sys.executable, "unique_rc.py", user_uid, file_name])


    os.remove(file_name)
    return 'Success'


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)