from flask import current_app
from Server.app import redis
from jsonpickle import decode as json_decode

# all keys agains which node's measurements are stored are prefixed with this key
NODE_PREFIX = "__node__"
# a key to store the nodes which we don't want to show on the dashboard
# the type of value against the key is a set https://redis.io/commands#set
FORGOTTEN_NODES_KEY = '__forgotten_nodes__'


class ComputerMeasurementsRedisAdapter(object):
    """
    Handle communication with redis
    """

    @staticmethod
    def add_measurement(node_identifier, computer_json):
        """
        Add a `shared.hardware_objects_lib.Computer` to the right-hand-side of the double-ended queue of a node on Redis
        The size of the deque is bounded - we discard entries from the left-hand-side to ensure the size of the queue.

        :param node_identifier: what identifies the computer for which we store information
        :param computer_json: shared.hardware_objects_lib.Computer serialized to JSON

        :return: boolean: true if added; false if node is marked as "forgotten"
        """
        if ComputerMeasurementsRedisAdapter.is_node_forgotten(node_identifier):
            return False

        key = make_key(NODE_PREFIX, node_identifier)

        max_entries_per_node = current_app.config['MAX_ENTRIES_PER_NODE']

        # add to the RIGHT of the dequeue
        redis.rpush(key, computer_json)

        # https://redis.io/commands/ltrim
        # keep only the `max_entries_per_node` most recent elements in the dequeue
        redis.ltrim(key, -max_entries_per_node, -1)

        return True

    @staticmethod
    def get_all_for_node(node_identifier, deserialize=True):
        """
        Get a list of all of the measurements available for this node.
        Newest measurement is the LAST element.

        :param node_identifier:
        :param deserialize: if True the entries in the resulting list will be deserialized to a Computer object
                            otherwise a list of json strings will be returned
        :return: list of Computer objects. newest is at the last position.
        """
        key = make_key(NODE_PREFIX, node_identifier)

        list_of_computers_json = redis.lrange(key, 0, redis.llen(key))
        if deserialize:
            return decode_list_of_serialized_computers(list_of_computers_json)
        else:
            return list_of_computers_json

    @staticmethod
    def get_newest_computer_measurement_from_redis(node_identifier, deserialize=True) :
        """
        Returns the most recently added computer measurement for this node
        None if there aren't any measurements for the node
        :param node_identifier:  the identifier which was used when storing Computer objects in the list
        :return: The newest measurement for the node, or None if there aren't any
        """
        try:
            # lrange returns a list which will contain only one element for non-empty response
            return ComputerMeasurementsRedisAdapter.get_all_for_node(node_identifier, deserialize)[-1]
        except Exception as ex:
            print(ex)
            return None

    @staticmethod
    def delete_node(node_identifier):
        """
        Remove the whole dequeue for this node.
        :param node_identifier:
        :return: None
        """
        key = make_key(NODE_PREFIX, node_identifier)

        return redis.delete(key)



    @staticmethod
    def get_all_monitored_hostnames():
        # i.e. non-forgotten nodes
        return [restore_from_key(NODE_PREFIX, key) for key in redis.keys("%s*" % NODE_PREFIX)]

    @staticmethod
    def forget_node(node_identifier):
        ComputerMeasurementsRedisAdapter.delete_node(node_identifier)
        redis.sadd(FORGOTTEN_NODES_KEY, node_identifier)

    @staticmethod
    def unforget_node(node_identifier):
        return redis.srem(FORGOTTEN_NODES_KEY, node_identifier)

    @staticmethod
    def is_node_forgotten(node_identifier):
        all_forgotten_nodes = ComputerMeasurementsRedisAdapter.get_forgotten_hosts()
        return node_identifier in all_forgotten_nodes

    @staticmethod
    def get_forgotten_hosts():
        key = FORGOTTEN_NODES_KEY
        return redis.smembers(key)


def decode_list_of_serialized_computers(list_of_computers_json: [str]):
    return [json_decode(computer_json) for computer_json in list_of_computers_json]


def make_key(prfx, node_name):
    return '%s%s' % (prfx, node_name)


def restore_from_key(prfx, key):
    try:
        return key.split(prfx)[1]
    except:
        raise Exception("unexpected prefix")
