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
            rows = sorted(list(reader), key=lambda x: float(x['Timestamp']))

        if not rows:
            print("⚠️ File is empty.")
            return

        print(f"🚀 Sending {len(rows)} packages...")
        start_time = time.time()
        base_timestamp = float(rows[0]['Timestamp'])

        for i, row in enumerate(rows):
            current_timestamp = float(row['Timestamp'])
            delay = current_timestamp - base_timestamp
            time.sleep(delay)

            package = {
                'ip_address': row['ip address'],
                'latitude': float(row['Latitude']),
                'longitude': float(row['Longitude']),
                'timestamp': int(current_timestamp),
                'suspicious': int(float(row['suspicious']))
            }

            send_package(package)
            base_timestamp = current_timestamp

    except Exception as e:
        print(f"❌ Error: {e}")
if __name__ == "__main__":
    try:
        process_csv('ip_addresses.csv')
    except KeyboardInterrupt:
        print("🛑 Interrupted by user")
