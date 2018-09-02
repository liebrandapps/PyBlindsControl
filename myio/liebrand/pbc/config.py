from ConfigParser import RawConfigParser


class Config:

    BLINDS = 0
    BLINDX = 1
    WEB = 2
    SECTIONS = ["blinds", "blind_%d", "webServer"]

    STRING_KEYS =["msgFormat", "logFileName", "endPoint", "webRoot", "default", "name", "tag", "address", "cmdDriveIn",
                  "cmdDriveOut", "cmdStop", "headline"]
    INT_KEYS =["maxFilesize", "logLevel", "count"]
    BOOLEAN_KEYS =["enableLogging"]

    DEFAULTS ={"enableLogging" :"yes",
                "logFileName": "/tmp/pbc.log",
                "maxFilesize": 1000000,
                "msgFormat": "%(asctime)s, %(levelname)s, %(module)s {%(process)d}, %(lineno)d, %(message)s",
                "logLevel": 10
                }

    def __init__(self, cfgFile, section):
        self.section = section
        self.cfg = RawConfigParser(Config.DEFAULTS)
        _ = self.cfg.read(cfgFile)

    def hasKey(self, dct, key):
        k = key.upper()
        for d in dct:
            if d.upper() == k:
                return d
        return None

    def hasSection(self, section):
        return self.cfg.has_section(section)

    def hasOption(self, option):
        return self.cfg.has_option(self.section, option)

    def __getattr__(self, name):
        key = self.hasKey(Config.STRING_KEYS, name)
        if not key is None:
            return self.cfg.get(self.section, key)
        key = self.hasKey(Config.INT_KEYS, name)
        if not key is None:
            return self.cfg.getint(self.section, key)
        key = self.hasKey(Config.BOOLEAN_KEYS, name)
        if not key is None:
            return self.cfg.getboolean(self.section, key)
        return None

    def setSection(self, newSection):
        tmp = self.section
        self.section = newSection
        return tmp

    def readValue(self, key):
        return self.cfg.get(self.section, key)