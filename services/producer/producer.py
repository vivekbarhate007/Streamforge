import json
import time
import random
from datetime import datetime, timedelta
from kafka import KafkaProducer
from kafka.errors import KafkaError
import config

# Product catalog with realistic distribution
PRODUCTS = [
    {"id": "prod_001", "category": "Electronics", "price": 99.99},
    {"id": "prod_002", "category": "Electronics", "price": 249.99},
    {"id": "prod_003", "category": "Clothing", "price": 19.99},
    {"id": "prod_004", "category": "Clothing", "price": 49.99},
    {"id": "prod_005", "category": "Books", "price": 39.99},
    {"id": "prod_006", "category": "Books", "price": 49.99},
    {"id": "prod_007", "category": "Home", "price": 79.99},
    {"id": "prod_008", "category": "Home", "price": 29.99},
    {"id": "prod_009", "category": "Sports", "price": 24.99},
    {"id": "prod_010", "category": "Sports", "price": 89.99},
]

# User IDs
USER_IDS = [f"user_{i:03d}" for i in range(1, 11)]

# Event type distribution (views are most common, purchases are rare)
EVENT_TYPES = {
    "view": 0.60,
    "click": 0.25,
    "add_to_cart": 0.10,
    "purchase": 0.05,
}


def get_random_event_type():
    """Select event type based on weighted distribution"""
    rand = random.random()
    cumulative = 0
    for event_type, probability in EVENT_TYPES.items():
        cumulative += probability
        if rand <= cumulative:
            return event_type
    return "view"


def generate_event():
    """Generate a realistic event"""
    event_type = get_random_event_type()
    product = random.choice(PRODUCTS)
    user_id = random.choice(USER_IDS)
    session_id = f"session_{random.randint(1000, 9999)}"
    
    event = {
        "ts": datetime.utcnow().isoformat() + "Z",
        "user_id": user_id,
        "session_id": session_id,
        "event_type": event_type,
        "product_id": product["id"],
        "metadata": {
            "category": product["category"],
            "user_agent": f"Browser_{random.randint(1, 5)}",
            "page_url": f"/products/{product['id']}",
        }
    }
    
    # Add price and quantity for cart/purchase events
    if event_type in ["add_to_cart", "purchase"]:
        event["price"] = product["price"]
        event["quantity"] = random.randint(1, 3)
    
    return event


def wait_for_kafka(max_retries=30):
    """Wait for Kafka to be available"""
    for i in range(max_retries):
        try:
            producer = KafkaProducer(
                bootstrap_servers=[config.KAFKA_BROKER],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                api_version=(0, 10, 1)
            )
            producer.close()
            print("Kafka is ready!")
            return True
        except Exception as e:
            if i < max_retries - 1:
                print(f"Waiting for Kafka... ({i+1}/{max_retries})")
                time.sleep(2)
            else:
                print(f"Failed to connect to Kafka: {e}")
                return False
    return False


def main():
    """Main producer loop"""
    if not wait_for_kafka():
        return
    
    producer = KafkaProducer(
        bootstrap_servers=[config.KAFKA_BROKER],
        value_serializer=lambda v: json.dumps(v).encode('utf-8'),
        api_version=(0, 10, 1)
    )
    
    print(f"Producing {config.TOTAL_EVENTS} events to {config.KAFKA_TOPIC}...")
    print(f"Rate: {config.EVENTS_PER_SECOND} events/second")
    
    delay = 1.0 / config.EVENTS_PER_SECOND
    sent = 0
    
    try:
        for i in range(config.TOTAL_EVENTS):
            event = generate_event()
            
            future = producer.send(config.KAFKA_TOPIC, event)
            
            # Handle callback for success/failure
            def on_send_success(record_metadata):
                pass
            
            def on_send_error(excp):
                print(f"Error sending event: {excp}")
            
            future.add_callback(on_send_success)
            future.add_errback(on_send_error)
            
            sent += 1
            if sent % 100 == 0:
                print(f"Sent {sent} events...")
            
            time.sleep(delay)
        
        # Wait for all messages to be sent
        producer.flush()
        print(f"\nSuccessfully sent {sent} events!")
        
    except KafkaError as e:
        print(f"Kafka error: {e}")
    except KeyboardInterrupt:
        print("\nStopping producer...")
    finally:
        producer.close()


if __name__ == "__main__":
    main()

