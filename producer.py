# producer.py
from kafka import KafkaProducer
import json
import time
import random

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

while True:
    data = {
        'timestamp': time.time(),
        'value': random.randint(0, 100)
    }
    producer.send('mytopic', data)
    print(f'Sent: {data}')
    time.sleep(1)
