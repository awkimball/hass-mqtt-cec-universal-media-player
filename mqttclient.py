import paho.mqtt.client as paho

import common

class mqttClient:
    client = {}
    broker = 'localhost'

    def set_connect_callback(self, callback):
        self.client.on_connect = callback

    def set_disconnect_callback(self, callback):
        self.client.on_disconnect = callback

    def set_message_callback(self, callback):
        self.client.on_message = callback

    def __init__(self, config):
        clientname = config['mqtt']['clientname']
        self.broker = config['mqtt']['host']
        self.client = paho.Client(clientname)
        self.client.username_pw_set(config['mqtt']['user'], config['mqtt']['pass'])
        self.client.will_set(common.power_avail_topic, 'offline')
        self.client.reconnect_delay_set(min_delay=2, max_delay=20)

    def start_mqtt(self):
        self.client.connect(self.broker, 1883, 60)
        self.client.loop_start()

if __name__ == '__main__':
    print("this shouldn't be visible")


