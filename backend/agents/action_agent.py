# backend/agents/action_agent.py
import json
import time
from datetime import datetime

class ActionAgent:
    def __init__(self, redis_client, socketio):
        self.redis_client = redis_client
        self.socketio = socketio
        self.pubsub = self.redis_client.pubsub()
        self.pubsub.subscribe('action_channel')

    def _publish_to_feed(self, text):
        timestamp = datetime.now().strftime('%H:%M:%S')
        message = f"[{timestamp}] [Action] {text}"
        self.redis_client.lpush('live_feed_log', message)
        self.redis_client.ltrim('live_feed_log', 0, 99)
        self.socketio.emit('new_feed_event', message)

    def run(self):
        print("Action Agent is running and awaiting instructions...")
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                investigation_result = json.loads(message['data'])
                self.take_action(investigation_result)

    def take_action(self, investigation_result):
        threat_type = investigation_result['threat_data']['threat_type']
        self._publish_to_feed(f"Received recommendation for {threat_type}. Taking action...")
        action_taken = "No specific action taken"

        if "block" in investigation_result['recommended_action'].lower():
            source_ip = investigation_result['threat_data']['traffic_data']['source_ip']
            action_taken = f"Blocked IP: {source_ip}"
        elif "terminate" in investigation_result['recommended_action'].lower():
            action_taken = "Terminated suspicious process"
        
        time.sleep(1)
        
        action_log = {
            'threat_type': threat_type,
            'action_taken': action_taken,
            'effectiveness': "High" if "No specific action" not in action_taken else "N/A",
            'timestamp': time.time(),
            'full_report': investigation_result
        }
        
        # Persist logs to Redis
        self.redis_client.set('latest_log', json.dumps(action_log))
        self.redis_client.lpush('action_log_history', json.dumps(action_log))
        
        # Emit the new log to all connected clients
        self.socketio.emit('new_action_log', action_log)
        
        self._publish_to_feed(f"Action Complete: {action_taken}.")
