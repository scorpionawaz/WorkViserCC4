from aiokafka import AIOKafkaConsumer
import asyncio
import json
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "task_topic")
KAFKA_GROUP_ID = os.getenv("KAFKA_GROUP_ID", "task_consumer_group")

async def consume():
    consumer = AIOKafkaConsumer(
        KAFKA_TOPIC,
        bootstrap_servers=KAFKA_BROKER,
        group_id=KAFKA_GROUP_ID,
        value_deserializer=lambda v: json.loads(v.decode('utf-8'))
    )
    
    await consumer.start()
    try:
        print("Kafka Consumer Started. Listening for messages...")
        async for msg in consumer:
            task_data = msg.value
            print(f"Received Task ID: {task_data['taskId']}")
            # Process task_id here (e.g., save to DB, trigger a job, etc.)
    finally:
        await consumer.stop()

if __name__ == "__main__":
    asyncio.run(consume())

