from flask import Flask, request, jsonify, send_from_directory
from flask_socketio import SocketIO
from flask_cors import CORS
import time

app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

traffic_stats = {
    'total_packets': 0,
    'suspicious_packets': 0,
    'active_connections': 0,
    'location_counts': {}
}

@app.route("/")
def index():
    return send_from_directory('static', 'index.html')

@app.route('/api/traffic', methods=['GET', 'POST'])
def traffic():
    if request.method == 'POST':
        if not request.is_json:
            return jsonify({'status': 'error',
                            'message': 'Content-Type must be application/json'}), 415

        data = request.get_json()
        print("Received data:", data)

        if not data:
            return jsonify({'status': 'error', 'message': 'No data provided'}), 400

        try:
            traffic_data = {
                'ip_address': str(data['ip_address']),
                'latitude': float(data['latitude']),
                'longitude': float(data['longitude']),
                'timestamp': int(data['timestamp']),
                'suspicious': float(data['suspicious'])
            }

            traffic_stats['total_packets'] += 1
            if traffic_data['suspicious']:
                traffic_stats['suspicious_packets'] += 1

            location_key = f"{traffic_data['latitude']},{traffic_data['longitude']}"
            traffic_stats['location_counts'][location_key] = traffic_stats['location_counts'].get(location_key, 0) + 1

            print("Emitting data:", traffic_data)
            socketio.emit('new_traffic', {'data': traffic_data})

            return jsonify({'status': 'success', 'data': traffic_data})

        except (ValueError, TypeError) as e:
            print(f"Data processing error: {e}")
            return jsonify({'status': 'error', 'message': str(e)}), 400

    elif request.method == 'GET':
        return jsonify({
            'status': 'success',
            'stats': traffic_stats
        })

@socketio.on('connect')
def handle_connect():
    print('Client connected')
    traffic_stats['active_connections'] += 1
    socketio.emit('stats_update', traffic_stats)

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    traffic_stats['active_connections'] -= 1
    socketio.emit('stats_update', traffic_stats)

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=True)
