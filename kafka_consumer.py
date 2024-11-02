# user_service_auth - user_service_auth/app/kafka/kafka_consumer.py

from aiokafka import AIOKafkaConsumer

async def consume_messages(topic, bootstrap_servers):
    # Create a consumer instance.
    consumer = AIOKafkaConsumer(
        topic,
        bootstrap_servers=bootstrap_servers,
        group_id="user-group",
        auto_offset_reset='earliest'
    )

    # Start the consumer.
    await consumer.start()

    try:
        # Continuously listen for messages.
        async for message in consumer:
            print(f"Consumer Received message: {message.value.decode()} on topic {message.topic}")
            
    finally:
        # Ensure that the consumer is properly closed when done.
        await consumer.stop() 

### ========================= *****  ========================= ###

