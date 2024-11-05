from flask import Flask, request, jsonify
from confluent_kafka import Producer
import json
import time
import asyncio

app = Flask(__name__)

# Kafka configuration
producer_config = {
    'bootstrap.servers': 'localhost:9092',  # Adjust with actual broker address
    'queue.buffering.max.ms': 500           # Set flush interval to 500 ms
}
producer = Producer(producer_config)

async def send_to_kafka(topic, data):
    """Asynchronous function to send data to Kafka."""
    producer.produce(topic, json.dumps(data))
    producer.poll(0)  # Trigger sending any buffered messages
    await asyncio.sleep(0)  # Yield control to event loop

@app.route('/send_emoji', methods=['POST'])
async def handle_emoji():
    """API endpoint to handle emoji POST requests."""
    try:
        # Extracting data from the request
        user_id = request.json.get("user_id")
        emoji_type = request.json.get("emoji_type")
        timestamp = request.json.get("timestamp", int(time.time()))

        # Validate request data
        if not user_id or not emoji_type:
            return jsonify({"error": "Invalid data"}), 400

        # Construct the message to send to Kafka
        data = {
            "user_id": user_id,
            "emoji_type": emoji_type,
            "timestamp": timestamp
        }

        # Send to Kafka asynchronously
        await send_to_kafka("emoji_topic", data)
        return jsonify({"status": "Message queued"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

