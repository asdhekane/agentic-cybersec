import json
import time
import random
from datetime import datetime

class MonitoringAgent:
    def __init__(self, redis_client, socketio):
        self.redis_client = redis_client
        self.socketio = socketio

    def _publish_to_feed(self, text):
        timestamp = datetime.now().strftime('%H:%M:%S')
        message = f"[{timestamp}] [Monitor] {text}"
        # Push to Redis for history
        self.redis_client.lpush('live_feed_log', message)
        self.redis_client.ltrim('live_feed_log', 0, 99)
        # Emit to live clients
        self.socketio.emit('new_feed_event', message)

    def simulate_traffic(self, attack_type):
        self._publish_to_feed(f"Simulating traffic for a {attack_type} attack...")
        # ... (rest of the simulation logic is the same)
        if attack_type == 'port_scan':
            traffic = self._generate_port_scan_traffic()
            self._detect_anomaly(traffic, "Port Scan")
        elif attack_type == 'sql_injection':
            traffic = self._generate_sql_injection_traffic()
            self._detect_anomaly(traffic, "SQL Injection")
        elif attack_type == 'ddos':
            traffic = self._generate_ddos_traffic()
            self._detect_anomaly(traffic, "DDoS")

    def _generate_port_scan_traffic(self):
        return {'source_ip': '192.168.1.100', 'destination_port': random.randint(1, 1024), 'packets': 1}

    def _generate_sql_injection_traffic(self):
        return {'source_ip': '10.0.0.5', 'payload': "' OR 1=1 --", 'packets': 1}

    def _generate_ddos_traffic(self):
        return {'source_ip': f'172.16.0.{random.randint(1, 254)}', 'packets': random.randint(1000, 5000)}

    def _detect_anomaly(self, traffic_data, threat_type):
        self._publish_to_feed(f"Anomaly Detected! Threat type: {threat_type}. Forwarding to Investigation Agent.")
        message = {
            'threat_type': threat_type,
            'traffic_data': traffic_data,
            'timestamp': time.time()
        }
        self.redis_client.publish('threat_channel', json.dumps(message))