# hass-mqtt-cec-universal-media-player

## Overview

An MQTT based HDMI-CEC appliance for use with Home Assistant.

I run this along with shairport-sync (Airplay server) on a Raspberry Pi 2 Model B connected to a Yamaha RX-V373 over HDMI. This MQTT client connects to my Home Assistant MQTT Broker and exposes the RX-V373 as a controllable device to Home Assistant over my home network as a series of virtual switches.

**TODO** Update desc to universal media player

<!-- Currently represented in Home Assistant as a power switch, and an input source switch. The `Stereo` switch controls power/standby on the RX-V373 and the `Airplay` switch controls the input source and switches between Airplay (HDMI) and TV (Optical S/PDIF) audio into the receiver. -->

A `systemd` service unit file is included for running this python script as a service on `systemd` based systems.

Using `homekit:` and `emulated_hue:` in the Home Assistant `configuration.yaml` allows these virtual switches to be controlled by iOS/macOS devices as well as Amazon echo devices.

## Setup

### Dependencies

Compile and install libcec from source in order to get the python bindings I guess. It should work by just installing `python-libcec` or whatever but I couldn't make it work
