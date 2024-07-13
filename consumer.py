from kafka import KafkaConsumer
import json

# Kafka Consumer Configuration
consumer = KafkaConsumer(
    'mytopic',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='my-group',
    value_deserializer=lambda m: m.decode('utf-8')
)

# File to write messages
output_file = 'messages.txt'

# Function to consume messages and write to file
def consume_messages():
    with open(output_file, 'a', buffering=1) as f:  # Line-buffered
        for message in consumer:
            try:
                msg = json.loads(message.value)
                f.write(json.dumps(msg) + '\n')
                f.flush()  # Ensure data is written immediately
            except json.JSONDecodeError as e:
                print(f"Error decoding message: {e} - Message: {message.value}")
            except Exception as e:
                print(f"Unexpected error: {e}")

if __name__ == "__main__":
    consume_messages()
