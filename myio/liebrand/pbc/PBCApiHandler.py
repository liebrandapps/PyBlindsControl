import json
import time

from config import Config
from myio.liebrand.phd.handler import Handler
import serial

class SunblindWrapper:

    def __init__(self):
        pass

    def send(self, address, cmd):
        port = serial.Serial("/dev/ttyUSB0", baudrate=9600, parity=serial.PARITY_NONE, stopbits=serial.STOPBITS_ONE, bytesize=serial.EIGHTBITS, timeout=3)
        try:
            time.sleep(2);
            while port.inWaiting() > 0:
                port.read(1)
            snd = "TFF" + address + "F0" + cmd + "$"
            port.write(snd)
            rcv = "Sent: " + snd
            time.sleep(.5)
        except ValueError as e:
            print e
            rcv=str(e)
        port.close()
        return [snd, rcv]


class SunBlind:

    def __init__(self, tag, name, address):
        self.tag = tag
        self.address = address
        self.name = name

    def getAddress(self):
        return self.address


class PBCApiHandler(Handler):

    IN = "in"
    OUT = "out"
    STOP = "stop"

    def __init__(self, cfg, log):
        self.cfg = cfg
        self.log = log
        self.blinds = {}
        cfg.setSection(Config.SECTIONS[Config.BLINDS])
        count = cfg.count
        self.cmds = {}
        self.cmds[PBCApiHandler.IN] = cfg.cmdDriveIn
        self.cmds[PBCApiHandler.OUT] = cfg.cmdDriveOut
        self.cmds[PBCApiHandler.STOP] = cfg.cmdStop
        for idx in range(count):
            cfg.setSection(Config.SECTIONS[Config.BLINDX] % (idx+1))
            tag = cfg.tag
            name = cfg.name
            address = cfg.address
            self.blinds[tag] = SunBlind(tag, name, address)
        self.log.info("[PCBAPI] Configured %d blinds" % count)

    def endPoint(self):
        return(["/pbcapi", ])

    def doGET(self, path, headers):
        self.log.debug("opps")
        return [404, {}, ""]

    def doPOST(self, path, headers, body):
        self.log.debug(body)
        fields = json.loads(body)
        dct = {}
        resultHeaders = {}
        if fields.has_key("tag") and fields.has_key("cmd"):
            if self.blinds.has_key(fields["tag"]) and self.cmds.has_key(fields["cmd"]):
                sb = self.blinds[fields["tag"]]
                cmd = self.cmds[fields["cmd"]]
                sbw = SunblindWrapper()
                self.log.debug("Address %s, command %s" % (sb.getAddress(), cmd))
                (snd, rcv) = sbw.send(sb.getAddress(), cmd)
                self.log.debug("Send [%s] -> Received [%s]" % (snd, rcv))
                resultCode = 200
                dct["status"] = "ok"
            else:
                self.log.error("[PCBAPI] Error in config cannot match json: %s" % body )
                resultCode = 500
                dct["status"] = "fail"
                dct["message"] = "server not configure for this type of request"
        else:
            self.log.error("[PCBAPI] Error in json cannot match fields: %s" % body)
            resultCode = 400
            dct["status"] = "fail"
            dct["message"] = "missing required fields"
        body = json.dumps(dct)
        resultHeaders['Content-Type'] = "application/json"
        self.log.debug(body)
        return [resultCode, resultHeaders, body]
