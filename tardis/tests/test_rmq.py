from time import sleep
from random import randint

from django.conf import settings
from django.test import TransactionTestCase
from kombu import Connection, Exchange, Queue

from tardis.celery import app


class VerifyTaskTestCase(TransactionTestCase):

    def setUp(self):
        # Open connection to RabbitMQ
        self.conn = Connection(settings.BROKER_URL)
        self.channel = self.conn.channel()

        # Connect to API queue
        self.apiQ = Queue(
            settings.API_QUEUE,
            channel=self.channel,
            exchange=Exchange(settings.API_QUEUE),
            routing_key=settings.API_QUEUE,
            queue_arguments={
                'x-max-priority': settings.MAX_TASK_PRIORITY
            }
        )

    def tearDown(self):
        # Close connection
        self.conn.close()

    def testVerify(self):

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
            # Queue cleanup
            self.apiQ.purge()

            # Random DFO ID
            dfo_id = randint(1, 2147483647)

            # Send task
            app.send_task(
                'mytardis.verify_dfo',
                args=[
                    dfo_id,
                    i['filename'],
                    'test',
                    i['algorithm']
                ]
            )

            # Wait for result message for max 5 seconds
            msg = None
            wait = 0
            while wait <= 5 and msg is None:
                msg = self.apiQ.get()
                if msg is None:
                    sleep(1)
                    wait += 1

            # Tests
            self.assertFalse(msg is None)
            self.assertTrue(msg.payload[0][0] == dfo_id)
            self.assertTrue(msg.payload[0][1] == i['algorithm'])
            self.assertTrue(msg.payload[0][2] == i['checksum'])
