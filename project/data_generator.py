import csv
import json
import time
import requests

def send_package(package):
    url = "http://server:5000/api/traffic"
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, data=json.dumps(package), headers=headers)
        print(f"✅ Sent: {package['ip_address']} → ({package['latitude']}, {package['longitude']}), suspicious: {package['suspicious']}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"❌ Request failed: {e}")
        return False

def process_csv(file_path):
    print(f"📂 Reading {file_path}")
    try:
        with open(file_path, 'r') as file:
            reader = csv.DictReader(file)
            rows = list(reader)
    except Exception as e:
        print(f"❌ Failed to open file: {e}")
        return

    if not rows:
        print("⚠️ File is empty.")
        return

    print(f"🚀 Sending {len(rows)} packages...")

    for i, row in enumerate(rows):
        try:
            package = {
                'ip_address': row['ip address'],
                'latitude': float(row['Latitude']),
                'longitude': float(row['Longitude']),
                'timestamp': int(row['Timestamp']),
                'suspicious': float(row['suspicious'])
            }
        except Exception as e:
            print(f"❌ Row {i} skipped: {e}")
            continue

        sent = send_package(package)
        if not sent:
            print(f"⚠️ Failed to send row {i}")

        time.sleep(0.2)
if __name__ == "__main__":
    try:
        process_csv('ip_addresses.csv')
    except KeyboardInterrupt:
        print("🛑 Interrupted by user")
