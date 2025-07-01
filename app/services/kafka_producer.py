from aiokafka import AIOKafkaProducer
import json
import os
from dotenv import load_dotenv

load_dotenv()

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "task_topic")

class KafkaProducer:
    def __init__(self):
        self.producer = None

    async def start(self):
        self.producer = AIOKafkaProducer(
            bootstrap_servers=KAFKA_BROKER,
            value_serializer=lambda v: json.dumps(v, default=str).encode('utf-8')
        )
        await self.producer.start()

    async def stop(self):
        await self.producer.stop()

    async def send_task(self, task_id: str):
        await self.producer.send(KAFKA_TOPIC, {"taskId": task_id})

# Instantiate Kafka producer
kafka_producer = KafkaProducer()

async def produce_task(task_id: str):
    await kafka_producer.send_task(task_id)


