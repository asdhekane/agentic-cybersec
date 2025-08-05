import json
import time
from transformers import pipeline
from datetime import datetime

class InvestigationAgent:
    def __init__(self, redis_client, socketio):
        self.redis_client = redis_client
        self.socketio = socketio
        self.pubsub = self.redis_client.pubsub()
        self.pubsub.subscribe('threat_channel')
        self.threat_intel_model = pipeline('text-generation', model='distilgpt2')

    def _publish_to_feed(self, text):
        timestamp = datetime.now().strftime('%H:%M:%S')
        message = f"[{timestamp}] [Investigator] {text}"
        self.redis_client.lpush('live_feed_log', message)
        self.redis_client.ltrim('live_feed_log', 0, 99)
        self.socketio.emit('new_feed_event', message)

    def run(self):
        print("Investigation Agent is running and listening for threats...")
        for message in self.pubsub.listen():
            if message['type'] == 'message':
                threat_data = json.loads(message['data'])
                self.investigate(threat_data)

    def investigate(self, threat_data):
        threat_type = threat_data.get('threat_type')
        self._publish_to_feed(f"Received threat. Starting investigation for {threat_type}...")
        time.sleep(2)
        
        prompt = f"A {threat_type} attack was detected. The recommended countermeasure is to block the source IP address."
        response = self.threat_intel_model(prompt, max_length=50, num_return_sequences=1)
        countermeasure = response[0]['generated_text']
        
        investigation_result = {
            'threat_data': threat_data,
            'investigation_summary': f"Investigated {threat_type}",
            'recommended_action': countermeasure,
            'timestamp': time.time()
        }
        
        self._publish_to_feed(f"Investigation complete. Recommending action: '{countermeasure[:40]}...'.")
        self.redis_client.publish('action_channel', json.dumps(investigation_result))
