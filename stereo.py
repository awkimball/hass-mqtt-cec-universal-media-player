from time import sleep
import random
import yaml
from threading import Thread
import logging
import threading

import common
import cecclient
import mqttclient

def init(config):
    logging.basicConfig(filename='stereo.log', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    config_file = open('config.yaml', 'r')
    config = yaml.load(config_file, Loader=yaml.FullLoader)
    config_file.close()
    return config

def publish_state():
    mymqttclient.client.publish(common.power_avail_topic, payload='online')
    mycecclient.request_stereo_power()
    mycecclient.request_audio_status()
    sleep(0.5)
    power = mycecclient.get_stereo_power()
    volume = mycecclient.get_volume()
    logging.debug("power status: %s", power)
    logging.debug("volume status: %s", volume)
    if power == 0:
        mymqttclient.client.publish(common.power_state_topic, payload='OFF')
    elif power == 1:
        mymqttclient.client.publish(common.power_state_topic, payload='ON')
    else:
        logging.error("Uh oh, weird state!")
    mymqttclient.client.publish(common.volume_state_topic, payload=str(volume))
    sleep(15)


def stereo_status_worker():
    while True:
         publish_state()

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        logging.info("MQTT connected to host "+mymqttclient.broker+":1883"+" rc: "+str(rc))
        mymqttclient.client.publish(common.power_avail_topic, payload='online')
        mymqttclient.client.subscribe(common.power_command_topic)
        mymqttclient.client.subscribe(common.source_command_topic)
        mymqttclient.client.subscribe(common.volume_command_topic)
        publish_state()
    else:
        logging.error("MQTT failed to connect to host "+mymqttclient.broker+":1883"+" with rc: "+str(rc))

def on_disconnect(client, userdata, rc):
    logging.warning("Power host connection lost with rc: "+str(rc))

def on_message(client, userdata, msg):
    if msg.topic == common.power_command_topic:
        if msg.payload.decode() == 'ON':
            mymqttclient.client.publish(common.power_state_topic, payload='ON')
            mycecclient.stereo_power_on()
        elif msg.payload.decode() == 'OFF':
            mymqttclient.client.publish(common.power_state_topic, payload='OFF')
            mycecclient.stereo_power_off()
    elif msg.topic == common.source_command_topic:
        if msg.payload.decode() == 'Airplay':
            mymqttclient.client.publish(common.source_state_topic, payload='Airplay') 
            mycecclient.source_airplay()
        elif msg.payload.decode() == 'TV':
            mymqttclient.client.publish(common.source_state_topic, payload='TV')
            mycecclient.source_tv()
    elif msg.topic == common.volume_command_topic:
        if msg.payload.decode() == 'ON':
            mymqttclient.client.publish(common.volume_state_topic, payload=(mycecclient.get_volume())+2)
            mycecclient.stereo_volume_up()
        elif msg.payload.decode() == 'OFF':
            mymqttclient.client.publish(common.volume_state_topic, payload=(mycecclient.get_volume())-2)
            mycecclient.stereo_volume_down()  
    else:
        logging.error("bad command")

# main setup
config = None
mycecclient = None
mymqttclient = None

if __name__ == '__main__':
    config = init(config)
    mycecclient = cecclient.pyCecClient()
    mymqttclient = mqttclient.mqttClient(config)
    # setup mycecclient
    mycecclient.InitLibCec()
    # setup mymqttclient
    mymqttclient.set_connect_callback(on_connect)
    mymqttclient.set_disconnect_callback(on_disconnect)
    mymqttclient.set_message_callback(on_message)
    # stereo status monitoring thread setup
    stereoStatusThread = threading.Thread(target=stereo_status_worker)
    # start mqtt client
    mymqttclient.start_mqtt()
    # start stereo status monitoring thread
    sleep(2)
    stereoStatusThread.start()

    while True:
        sleep(0.1)
