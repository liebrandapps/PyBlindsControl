import exceptions
import logging
import time
from logging.handlers import RotatingFileHandler
from os.path import join, exists
import sys

from myio.liebrand.pbc.PBCWebHandler import PBCWebHandler
from myio.liebrand.pbc.PBCApiHandler import PBCApiHandler
from myio.liebrand.pbc.config import Config
from myio.liebrand.phd.server import Daemon, Server


class Context:

    SECTION = "blinds"
    CONFIG_DIR = "./"
    CONFIG_FILE = "pbc.ini"

    def __init__(self):
        path = join(Context.CONFIG_DIR, Context.CONFIG_FILE)
        self.log = None
        if not (exists(path)):
            self.printLogLine(sys.stderr,
                              "[IPFSSVR] No config file %s found at %s" % (Context.CONFIG_FILE, Context.CONFIG_DIR))
            return
        self.cfg = Config(path, Context.SECTION)
        self.setupLogger(self.cfg)
        #self.readConfig(self.cfg)

    def getTimeStamp(self):
        return time.strftime('%d.%m.%Y %H:%M:%S', time.localtime(time.time()))

    def printLogLine(self, fl, message):
        fl.write('%s %s\n' % (self.getTimeStamp(), message))
        fl.flush()

    def setupLogger(self, cfg):
        try:
            self.log = logging.Logger("SPFS")
            self.loghdl = RotatingFileHandler(cfg.logFileName, 'a', cfg.maxFilesize, 4)
            #self.loghdl = logging.FileHandler(cfg.logFileName)
            self.loghdl.setFormatter(logging.Formatter(cfg.msgFormat))
            self.loghdl.setLevel(cfg.logLevel)
            self.log.addHandler(self.loghdl)
            self.log.disabled = False
            self.initialLogLevel = cfg.logLevel
            self.debugLevel = False
            return True
        except exceptions.Exception, e:
            self.printLogLine(sys.stderr, "[SPFSSVR] Unable to initialize logging. Reason: %s" % e)
            return False

    def getLogger(self):
        return self.log

    def getConfig(self):
        return self.cfg


if __name__ == '__main__':
    if len(sys.argv) > 1:
        todo = sys.argv[1]
        if todo in [ 'start', 'stop', 'restart', 'status' ]:
            pidFile = "/tmp/pbc.pid"
            logFile = "/tmp/pbc.log"
            d = Daemon(pidFile)
            d.startstop(todo, stdout=logFile, stderr=logFile)
    ctx = Context()

    pbcApiHandler = PBCApiHandler(ctx.getConfig(), ctx.getLogger())
    pbcWebHandler = PBCWebHandler(ctx.getConfig(), ctx.getLogger())
    s = Server(8020, [pbcApiHandler, pbcWebHandler, ], ctx.getLogger())
    s.serve()