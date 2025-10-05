import json
import logging
from kafka import KafkaProducer
from kafka.errors import KafkaError

from app.config import settings

logger = logging.getLogger(__name__)

class KafkaProducerClient:
    def __init__(self):
        self.producer = None
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=settings.kafka_bootstrap_servers.split(','),
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                api_version=(0, 10, 1) # Explicitly set for compatibility
            )
            logger.info("Successfully connected to Kafka brokers.")
        except KafkaError as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            # In a real application, you might want to implement retry logic or a circuit breaker
            self.producer = None

    def send_message(self, topic: str, message: dict):
        if not self.producer:
            logger.error("Kafka producer is not available. Cannot send message.")
            return

        try:
            future = self.producer.send(topic, value=message)
            # Block for 'synchronous' sends for up to 10 seconds
            record_metadata = future.get(timeout=10)
            logger.info(
                f"Message sent to topic '{record_metadata.topic}' "
                f"partition {record_metadata.partition} "
                f"offset {record_metadata.offset}"
            )
        except KafkaError as e:
            logger.error(f"Failed to send message to Kafka topic '{topic}': {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred while sending message to Kafka: {e}")

    def close(self):
        if self.producer:
            self.producer.flush()
            self.producer.close()
            logger.info("Kafka producer connection closed.")

# A single instance to be used across the application.
# The connection is created upon initialization.
kafka_producer_client = KafkaProducerClient()

# To gracefully close the connection, we should call kafka_producer_client.close()
# during the application's shutdown event. This can be handled in FastAPI's lifespan events in main.py.