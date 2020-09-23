import cec
import sys
import logging

class pyCecClient:
    cecconfig = cec.libcec_configuration()
    lib = {}
    # don't enable debug logging by default
    log_level = cec.CEC_LOG_TRAFFIC
    volume = -1
    power_status = -1

    

    def SetConfiguration(self):
        self.cecconfig.strDeviceName = "rpi"
        self.cecconfig.bActivateSource = 0
        self.cecconfig.deviceTypes.Add(cec.CEC_DEVICE_TYPE_PLAYBACK_DEVICE)
        self.cecconfig.clientVersion = cec.LIBCEC_VERSION_CURRENT

    def SetLogCallback(self, callback):
        self.cecconfig.SetLogCallback(callback)

    def DetectAdapter(self):
        retval = None
        adapters = self.lib.DetectAdapters()
        for adapter in adapters:
            retval = adapter.strComName
        return retval

    def request_stereo_power(self):
        cmd = self.lib.CommandFromString('45:8F')
        self.lib.Transmit(cmd)
    
    def request_audio_status(self):
        cmd = self.lib.CommandFromString('45:71')
        self.lib.Transmit(cmd)

    def stereo_power_on(self):
        cmd = self.lib.CommandFromString('45:44:6D')
        self.lib.Transmit(cmd)
        cmd = self.lib.CommandFromString('45:70:00:00')
        self.lib.Transmit(cmd)

    def stereo_power_off(self):
        cmd = self.lib.CommandFromString('45:44:6C')
        self.lib.Transmit(cmd)
    
    def source_airplay(self):
        cmd = self.lib.CommandFromString('4F:82:10:00')
        self.lib.Transmit(cmd)

    def source_tv(self):
        cmd = self.lib.CommandFromString('4F:82:20:00')
        self.lib.Transmit(cmd)

    def stereo_volume_up(self):
        cmd = self.lib.CommandFromString('45:44:41')
        self.lib.Transmit(cmd)
        self.request_audio_status()

    def stereo_volume_down(self):
        cmd = self.lib.CommandFromString('45:44:42')
        self.lib.Transmit(cmd)
        self.request_audio_status()

    def get_stereo_power(self):
        return self.power_status

    def get_volume(self):
        return self.volume

    def __init__(self):
        self.SetConfiguration()
        self.SetLogCallback(self.log_callback)
        self.lib = cec.ICECAdapter.Create(self.cecconfig)
        logging.info('libCEC version ' + self.lib.VersionToString(self.cecconfig.serverVersion) + ' loaded: ' + self.lib.GetLibInfo())
    
    def log_callback(self, level, time, message):
        if level != self.log_level:
            return 0

        if level == cec.CEC_LOG_TRAFFIC:
            # audio status
            if message[6:8] == '7a':
                self.volume = int(message[9:11], base=16)
                logging.debug("Volume status callback: %i" % (self.volume))
            # stereo power
            elif message[6:8] == '90':
                value = int(message[9:11])
                if value == 0:
                    self.power_status = 1
                elif value == 1:
                    self.power_status = 0
                else:
                    self.power_status = -1

    def InitLibCec(self):
        adapter = self.DetectAdapter()
        if adapter == None:
            logging.error('No CEC adapters found')
            sys.exit('No CEC adapters found')
        else:
            if self.lib.Open(adapter):
                logging.info("CEC connection opened")
                return
            else:
                logging.error("failed to open a connection to the CEC adapter")
                sys.exit('Error opening CEC adapter')

