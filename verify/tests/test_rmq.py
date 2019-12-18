import unittest
import uuid
from os import path
from time import sleep
from random import randint

from kombu import Connection, Exchange, Queue

from verify.settings import config


class TestVerifyTask(unittest.TestCase):

    def setUp(self):
        # Open connection to RabbitMQ
        self.conn = Connection(config['broker_url'])
        self.channel = self.conn.channel()

        # Declare Verify queue
        q = config['queues']['verify']
        self.verifyQ = Queue(
            q['name'],
            channel=self.channel,
            exchange=Exchange(q['name']),
            routing_key=q['name'],
            max_priority=q['max_task_priority']
        )
        self.verifyQ.declare()

        # Declare API queue
        q = config['queues']['api']
        self.apiQ = Queue(
            q['name'],
            channel=self.channel,
            exchange=Exchange(q['name']),
            routing_key=q['name'],
            max_priority=q['max_task_priority']
        )
        self.apiQ.declare()

    def tearDown(self):
        # Delete Verify queue
        self.apiQ.delete()
        # Delete API queue
        self.verifyQ.delete()
        # Close connection
        self.conn.close()

    def test_verify(self):

        data = [{
            'filename': '/var/store/15525119098910.pdf',
            'algorithm': 'md5',
            'checksum': 'ec4e3b91d2e03fdb17db55ff46da43b2'
        }, {
            'filename': '/var/store/15525119098910.pdf',
            'algorithm': 'sha512',
            'checksum': 'bc803d8abccf18d89765d6ae9fb7d490ad07f57a48e4987acc1'
                        '73af4e65f143a4d215ffb59e9eebeb03849baab5a6e016e2806'
                        'a2cd0e84b14c778bdb84afbbf4'
        }]

        for i in data:
            self.assertTrue(path.exists(i['filename']))

            # Queues cleanup
            self.verifyQ.purge()
            self.apiQ.purge()

            # Random DFO ID
            dfo_id = randint(1, 2147483647)

            # Send task
            q = config['queues']['verify']
            producer = self.conn.Producer()
            producer.publish(
                routing_key=q['name'],
                body=[[
                    dfo_id,
                    i['filename'],
                    'test',
                    i['algorithm']
                ], {}, {}],
                headers={
                    'task': 'verify_dfo',
                    'id': str(uuid.uuid1())
                }
            )

            # Wait for result message for max 5 seconds
            msg = None
            wait = 0
            while wait <= 5 and msg is None:
                msg = self.apiQ.get(no_ack=False)
                if msg is None:
                    sleep(1)
                    wait += 1

            # Tests
            self.assertFalse(msg is None)
            self.assertTrue(msg.payload[0][0] == dfo_id)
            self.assertTrue(msg.payload[0][1] == i['algorithm'])
            self.assertTrue(msg.payload[0][2] == i['checksum'])
