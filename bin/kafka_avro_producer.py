#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    Avro Kafka Producer. (Producer that writes click avro msgs to a local broker as a demo)
    Every time you make a new line it will generate a new click msg and pub to kafka
"""

from datetime import datetime
import os
import random
import sys
import uuid

from confluent_kafka import avro
from confluent_kafka.avro import AvroProducer


if __name__ == '__main__':
    # Producer configuration
    # See https://github.com/edenhill/librdkafka/blob/master/CONFIGURATION.md
    conf = {'bootstrap.servers': 'vagrant-ubuntu-trusty-64:9092',
            'acks': 'all',
            'schema.registry.url': 'http://vagrant-ubuntu-trusty-64:8081',
            'compression.codec': 'gzip',
            }

    # Kafka Topic Name
    topic = 'clicks'

    # Only defining a value schema as we don't care about keys right now
    my_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    key_schema = avro.load(os.path.join(my_path, 'conf/schema/avro/clicks_key_v1.avsc'))
    sys.stdout.write('%% Loaded key_schema:\n %s \n' % key_schema)

    value_schema = avro.load(os.path.join(my_path, 'conf/schema/avro/clicks_value_v1.avsc'))
    sys.stdout.write('%% Loaded value_schema:\n %s \n' % value_schema)

    # Create Producer instance
    avro_producer = AvroProducer(conf, default_key_schema=key_schema, default_value_schema=value_schema)

    # Optional per-message delivery callback (triggered by poll() or flush())
    # when a message has been successfully delivered or permanently
    # failed delivery (after retries).
    def delivery_callback(err, msg):
        if err:
            sys.stderr.write('%% Message failed delivery: %s\n' % err)
        else:
            sys.stderr.write('%% Message delivered to %s [%d] @ %o\n' %
                             (msg.topic(), msg.partition(), msg.offset()))

    agents = [
        # S8
        'Mozilla/5.0 (Linux; Android 7.0; SM-G892A Build/NRD90M; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/60.0.3112.107 Mobile Safari/537.36',
        # iPhone XR
        'Mozilla/5.0 (iPhone; CPU iPhone OS 12_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/12.0 Mobile/15E148 Safari/604.1',
        # Mac OS-X Using Safari
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9',
        # Roku Ultra
        'Roku4640X/DVP-7.70 (297.70E04154A)',
        # PS4
        'Mozilla/5.0 (PlayStation 4 3.11) AppleWebKit/537.73 (KHTML, like Gecko)'
    ]

    referrers = [
        'google.com',
        'facebook.com',
        'nytimes.com',
        'cnn.com',
        'foxnews.com',
        'espn.com'
    ]

    # Read lines from stdin, produce each line to Kafka
    for i in range(10):
        try:
            click_id = str(uuid.uuid4())

            click_key = {'id': click_id}

            # Produce line (without newline)
            click_value = {
                'id': click_id,
                'impression_id': str(uuid.uuid4()),
                'creative_id': str(uuid.uuid4())[:8],
                'placement_id': str(uuid.uuid4())[:8],
                'timestamp': long(float(datetime.utcnow().strftime('%s.%f')) * 1000),
                'user_agent': str(random.choice(agents)),
                'ip': str('.'.join([str(random.randint(0,255)) for x in range(4)])),
                'referrer': str(random.choice(referrers)),
                'cost': random.uniform(0.05, 1.00)
            }

            avro_producer.produce(topic=topic, key=click_key, value=click_value, callback=delivery_callback)

        except BufferError:
            sys.stderr.write('%% Local producer queue is full (%d messages awaiting delivery): try again\n' %
                             len(avro_producer))

        # Serve delivery callback queue.
        # NOTE: Since produce() is an asynchronous API this poll() call
        #       will most likely not serve the delivery callback for the
        #       last produce()d message.
        avro_producer.poll(0)

    # Wait until all messages have been delivered
    sys.stderr.write('%% Waiting for %d deliveries\n' % len(avro_producer))
    avro_producer.flush()
