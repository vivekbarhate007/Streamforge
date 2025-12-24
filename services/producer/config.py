import os
from dotenv import load_dotenv

load_dotenv()

KAFKA_BROKER = os.getenv("KAFKA_BROKER", "localhost:9092")
KAFKA_TOPIC = os.getenv("KAFKA_TOPIC", "user_events")
EVENTS_PER_SECOND = int(os.getenv("EVENTS_PER_SECOND", "10"))
TOTAL_EVENTS = int(os.getenv("TOTAL_EVENTS", "1000"))

