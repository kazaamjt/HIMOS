import unittest
from unittest import TestCase
from flask import current_app
from redis import Redis
from json import dumps, loads
from Server.app.measurements_redis_adapter import ComputerMeasurementsRedisAdapter as redis_adapter, redis as raw_redis

some_node_id = 'my node id'


class TestRedisAdapter(TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_redis_namespace = 9

    def setUp(self):
        # make sure we don't erase redis
        assert raw_redis.client_list()[0]['db'] == str(self.test_redis_namespace)
        if len(raw_redis.keys("*")):
            raw_redis.delete(*raw_redis.keys('*'))

        self.max_entries_per_node = current_app.config['MAX_ENTRIES_PER_NODE']
        assert len(raw_redis.keys('*')) == 0

    def tearDown(self):
        if len(raw_redis.keys("*")):
            raw_redis.delete(*raw_redis.keys('*'))

    def test_smoke_test(self):
        # check if we can connect to redis at all
        self.assertTrue(raw_redis.ping())

    def test_add_measurement_simple(self):
        payload_json = dumps({
            'key1': 'val1'
        })

        redis_adapter.add_measurement(some_node_id, payload_json)
        matching_keys = raw_redis.keys('*%s*' % some_node_id)

        self.assertEqual(len(matching_keys), 1, 'Only one key is expected to be in redis now.')
        matching_key = matching_keys[0]
        self.assertTrue(some_node_id in matching_key, "The name of the host is expected to be in the redis key")

        self.assertEqual(raw_redis.llen(matching_key), 1,
                         "The list against for this node should contain only one element now")

    def test_add_measurement_more_than_limit(self):
        # adding more measurements than the limit will keep only the newest measurements within this limit
        num_entries = self.max_entries_per_node * 2
        for i in range(0, num_entries):
            payload = dumps({'k': str(i)})

            redis_adapter.add_measurement(some_node_id, payload)

        node_key = raw_redis.keys('*%s*' % some_node_id)[0]

        self.assertEqual(raw_redis.llen(node_key), self.max_entries_per_node,
                         "Redis contains more than the allowed limit of measurements")

        oldest = loads(raw_redis.lindex(node_key, 0))
        newest = loads(raw_redis.lindex(node_key, self.max_entries_per_node - 1))

        expected_payload_oldest = str(num_entries - self.max_entries_per_node)
        expected_payload_newest = str(num_entries - 1)

        self.assertEqual(oldest['k'], expected_payload_oldest,
                         "The oldest element in a dequeue should be at index 0")

        self.assertEqual(newest['k'], expected_payload_newest,
                         "The newest element in a dequeue should be at the end of the dequeue")

    def test_add_measurement_dequeue(self):
        # we add at end of the list
        payload_first = dumps({'k1': 'v1'})
        payload_second = dumps({'k2': 'v2'})

        redis_adapter.add_measurement(some_node_id, payload_first)
        redis_adapter.add_measurement(some_node_id, payload_second)

        node_key = raw_redis.keys('*%s*' % some_node_id)[0]

        assert raw_redis.llen(node_key) == 2, 'sanity checking the number of elements'

        second = loads(raw_redis.lindex(node_key, 1))
        self.assertEqual('v2', second['k2'], 'the newest added element to the queue was not at added at the end')

    def test_get_all_for_node(self):
        num_items = 10
        for index in range(0, num_items):
            redis_adapter.add_measurement(some_node_id, dumps({'k': str(index)}))
        node_key = raw_redis.keys('*%s*' % some_node_id)[0]

        all_measurements = redis_adapter.get_all_for_node(some_node_id)
        self.assertEqual(len(all_measurements), num_items)
        
        for index, payload in enumerate(redis_adapter.get_all_for_node(some_node_id)):
            self.assertEqual(payload['k'], str(index))
