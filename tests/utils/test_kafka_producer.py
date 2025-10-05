import unittest
from unittest.mock import patch, MagicMock

from kafka.errors import KafkaError

# We need to patch the settings before importing the module that uses it
with patch('app.config.settings', MagicMock()) as mock_settings:
    mock_settings.kafka_bootstrap_servers = "mock_server:9092"
    from app.utils.kafka_producer import KafkaProducerClient

class TestKafkaProducerClient(unittest.TestCase):

    @patch('app.utils.kafka_producer.KafkaProducer')
    def test_init_success(self, MockKafkaProducer):
        """Test successful initialization of KafkaProducerClient."""
        mock_producer_instance = MockKafkaProducer.return_value
        client = KafkaProducerClient()

        self.assertIsNotNone(client.producer)
        MockKafkaProducer.assert_called_once_with(
            bootstrap_servers=["mock_server:9092"],
            value_serializer=unittest.mock.ANY,
            api_version=(0, 10, 1)
        )
        client.close() # Clean up

    @patch('app.utils.kafka_producer.KafkaProducer', side_effect=KafkaError("Connection failed"))
    def test_init_failure(self, MockKafkaProducer):
        """Test handling of KafkaError during initialization."""
        with self.assertLogs('app.utils.kafka_producer', level='ERROR') as cm:
            client = KafkaProducerClient()
            self.assertIsNone(client.producer)
            self.assertIn("Failed to initialize Kafka producer: Connection failed", cm.output[0])

    @patch('app.utils.kafka_producer.KafkaProducer')
    def test_send_message_success(self, MockKafkaProducer):
        """Test successful message sending."""
        mock_producer_instance = MockKafkaProducer.return_value
        mock_future = MagicMock()
        mock_record_metadata = MagicMock()
        mock_record_metadata.topic = "test_topic"
        mock_record_metadata.partition = 0
        mock_record_metadata.offset = 1
        mock_future.get.return_value = mock_record_metadata
        mock_producer_instance.send.return_value = mock_future

        client = KafkaProducerClient()
        client.send_message("test_topic", {"key": "value"})

        mock_producer_instance.send.assert_called_once_with("test_topic", value={"key": "value"})
        mock_future.get.assert_called_once_with(timeout=10)
        client.close()

    @patch('app.utils.kafka_producer.KafkaProducer')
    def test_send_message_kafka_error(self, MockKafkaProducer):
        """Test handling of KafkaError during message sending."""
        mock_producer_instance = MockKafkaProducer.return_value
        mock_producer_instance.send.side_effect = KafkaError("Send failed")

        client = KafkaProducerClient()
        with self.assertLogs('app.utils.kafka_producer', level='ERROR') as cm:
            client.send_message("test_topic", {"key": "value"})
            self.assertIn("Failed to send message to Kafka topic 'test_topic': Send failed", cm.output[0])
        client.close()

    @patch('app.utils.kafka_producer.KafkaProducer')
    def test_send_message_no_producer(self, MockKafkaProducer):
        """Test that send_message does nothing if producer is not initialized."""
        # Simulate initialization failure
        MockKafkaProducer.side_effect = KafkaError("Connection failed")

        client = KafkaProducerClient()
        # Suppress the expected init error log for this specific test
        with self.assertLogs('app.utils.kafka_producer', level='ERROR'):
            client.producer = None # Ensure it's None

        with self.assertLogs('app.utils.kafka_producer', level='ERROR') as cm:
            client.send_message("test_topic", {"key": "value"})
            self.assertIn("Kafka producer is not available. Cannot send message.", cm.output[0])

    @patch('app.utils.kafka_producer.KafkaProducer')
    def test_close(self, MockKafkaProducer):
        """Test that the close method calls flush and close on the producer."""
        mock_producer_instance = MockKafkaProducer.return_value

        client = KafkaProducerClient()
        client.close()

        mock_producer_instance.flush.assert_called_once()
        mock_producer_instance.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()