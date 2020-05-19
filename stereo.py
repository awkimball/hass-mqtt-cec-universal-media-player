from time import sleep
import random
import cec
from threading import Thread
import paho.mqtt.client as mqtt
# change to your Home Assistant hostname or static IP
broker = 'homeassistant'
# MQTT broker user credentials
username = 'system'
clientname = 'stereoclient'
# appropriate MQTT topics
power_state_topic = 'home/stereo/power/state'
power_command_topic = 'home/stereo/power/cmd'
airplay_state_topic = 'home/stereo/airplay/state'
airplay_command_topic = 'home/stereo/airplay/cmd'
availability_topic = 'home/stereo/availability'
# Number of minutes between checking power state of audio reciever via CEC
check_status_interval_minutes = 1
# define CEC device handles 
stereo = cec.CECDEVICE_AUDIOSYSTEM
broadcast = cec.CECDEVICE_BROADCAST
stereo_device = cec.Device(stereo)
# Initialize CEC adapter
cec.init()
# Read in MQTT Broker user password from file
file = open('pass', 'r')
password = file.read().rstrip()
file.close()
# TODO Setup proper logging, currently being handled by Systemd service 
#file = open('./mqtt-cec.log')
# Method for checking power status of HDMI audio Receiver
def check_power_status():
    sleep(60*check_status_interval_minutes)
    if stereo_device.is_on():
        client.publish(power_state_topic, payload='ON')
    elif (not stereo_device.is_on()):
        client.publish(power_state_topic, payload='OFF')
# Method to send "On" command to stereo, as well as request "System Audio Mode" which is necessary for enabling audio output on my Yamaha Receiver
def stereo_on():
    cec.transmit(stereo, 0x44, b'\x6D')
    cec.transmit(stereo, 0x70, b'\x00\x00')
# Method to send "Off" or 'Standby" command to audio receiver
def stereo_off():
    cec.transmit(stereo, 0x44, b'\x6C')
# Method to change active source to address 1.0.0.0 on the audio receiver - in my case this is HDMI1 which is how this RPi is connected
def airplay_on():
    cec.transmit(broadcast, 0x82, b'\x10\x00')
# Method to change active source to address 2.0.0.0 on the audio receiver - in my case this is Optical S/PDIF which is connected to a TV
def airplay_off():
    cec.transmit(broadcast, 0x82, b'\x20\x00')
# Callback handler method called when a disconnect from the MQTT broker occurs. Mostly for logging purposes to see if frequent disconnects are happening
def on_disconnect(client, userdata, rc):
    print("Disconnected from host. Status: "+str(rc))
# Callback handler for successful connection to the MQTT Broker. Prints status, publishes valid availability of the virtual switches, and subscribes to the command topics of each switch.
def on_connect(client, userdata, flags, rc):
    print("Connected to host "+broker+":1883"+"  status: "+str(rc))
    # Subscribing in on_connect() means that if we lose the connection and
    # reconnect then subscriptions will be renewed.
    client.publish(availability_topic, payload='online')
    client.subscribe(power_command_topic)
    client.subscribe(airplay_command_topic)
# Callback handler for processing any messages received on subscribed-to topics
def on_message(client, userdata, msg):
    if msg.topic == power_command_topic:
        if msg.payload.decode() == 'ON':
            stereo_on()
            client.publish(power_state_topic, payload='ON')
            #print("Stereo on")
        elif msg.payload.decode() == 'OFF':
            stereo_off()
            client.publish(power_state_topic, payload='OFF')
            #print("Stereo off")
    elif msg.topic == airplay_command_topic:
        if msg.payload.decode() == 'ON':
            airplay_on()
            client.publish(airplay_state_topic, payload='ON')
            #print("Turning airplay on")
        elif msg.payload.decode() == 'OFF':
            airplay_off()
            client.publish(airplay_state_topic, payload='OFF')
            #print("Turning airplay off")
    else:
        print("bad command")
# Setup MQTT client params and attempt to connect to the broker. 
client = mqtt.Client(clientname)
client.on_connect = on_connect
client.on_message = on_message
client.username_pw_set(username, password)
# Set last will and testament for this client. If the client loses connection to the broker, this message will immediately be sent, changing the switches to unavailable in Home Assistant
client.will_set(availability_topic, 'offline')
client.connect(broker, 1883)
# Loop indefinitely in a thread, processing received and sent MQTT messages.
client.loop_start()
# Loop to check and update power status of the audio receiver. Runs on the interval defined in check_status_interval_minutes
while True:
    check_power_status()
