# backend/app.py
from flask import Flask, jsonify, request
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import redis
import json
from agents.monitoring_agent import MonitoringAgent
from agents.investigation_agent import InvestigationAgent
from agents.action_agent import ActionAgent
import threading
import os

app = Flask(__name__)
CORS(app)
# Wrap the app with SocketIO
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Redis client
redis_host = os.environ.get('REDIS_HOST', 'localhost')
redis_client = redis.Redis(host=redis_host, port=6379, db=0, decode_responses=True)

# Pass the socketio instance to the agents so they can emit events
monitoring_agent = MonitoringAgent(redis_client, socketio)
investigation_agent = InvestigationAgent(redis_client, socketio)
action_agent = ActionAgent(redis_client, socketio)

# --- Standard REST API Endpoints ---
@app.route('/simulate_attack', methods=['POST'])
def simulate_attack():
    data = request.get_json()
    attack_type = data.get('attack_type')
    if not attack_type:
        return jsonify({'error': 'Attack type not specified'}), 400
    monitoring_agent.simulate_traffic(attack_type)
    return jsonify({'message': f'Simulating {attack_type} attack.'})

# --- WebSocket Event Handlers ---
@socketio.on('connect')
def handle_connect():
    """Sends initial data to a newly connected client."""
    print('Client connected')
    # Fetch historical data to populate the new client's UI
    feed = redis_client.lrange('live_feed_log', 0, -1)
    logs = redis_client.lrange('action_log_history', 0, -1)
    latest = redis_client.get('latest_log')
    
    initial_data = {
        'live_feed': feed,
        'action_log': [json.loads(log) for log in logs],
        'latest_status': json.loads(latest) if latest else None
    }
    emit('initial_data', initial_data)

def run_agents():
    """Runs all agent listeners in separate threads."""
    print("Starting agent threads...")
    threading.Thread(target=investigation_agent.run, daemon=True).start()
    threading.Thread(target=action_agent.run, daemon=True).start()

# Clear previous logs and start the agent threads when the application starts.
# This block will be executed by Gunicorn when it loads the app.
redis_client.delete('latest_log', 'action_log_history', 'live_feed_log')
run_agents()

# Note: The `if __name__ == '__main__':` block and `socketio.run()` are removed.
# Gunicorn will be used to run the app via the Dockerfile's CMD instruction.