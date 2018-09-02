from os.path import exists, join
import mimetypes

from myio.liebrand.pbc.config import Config
from myio.liebrand.phd.handler import Handler

class SunBlind:

    TAG_TAG = "##TAG_%d##"
    TAG_NAME = "##NAME_%d##"

    def __init__(self, tag, name, index):
        self.tag = tag
        self.index = index
        self.name = name

    def replaceTags(self, html):
        tagTag = SunBlind.TAG_TAG % self.index
        tagName = SunBlind.TAG_NAME % self.index
        return html.replace(tagTag, self.tag).replace(tagName, self.name)


class PBCWebHandler(Handler):

    def __init__(self, cfg, log):
        self.cfg = cfg
        self.log = log
        cfg.setSection(Config.SECTIONS[Config.BLINDS])
        count = cfg.count
        self.title = cfg.headline
        self.blinds = []
        for idx in range(count):
            cfg.setSection(Config.SECTIONS[Config.BLINDX] % (idx+1))
            tag = cfg.tag
            name = cfg.name
            self.blinds.append(SunBlind(tag, name, idx+1))


    def endPoint(self):
        return(["/pbcweb", "*"])

    def doGET(self, path, headers):
        self.log.debug(path)
        resultHeaders = {}
        resultCode = 404
        body = ""
        self.cfg.setSection(Config.SECTIONS[Config.WEB])
        webRoot = self.cfg.webRoot

        if "/pbcweb" in path:
            path = path.replace("/pbcweb", "")

        if len(path) == 0:
            script = self.cfg.default
        else:
            script = path
        if script.startswith("/"):
            script = script[1:]

        if ".." in script or "%" in script:
            resultCode = 403
        else:
            path = join(webRoot, script)
            if exists(path):
                body = open(path, 'r').read()
                for b in self.blinds:
                    body = b.replaceTags(body)
                body = body.replace("##TITLE##", self.title)
                tmp = mimetypes.guess_type(script)
                if tmp[0] is not None:
                    resultHeaders['Content-Type'] = tmp[0]
                resultCode = 200
            else:
                self.log.error("Could not find www file %s" % (path))
                resultCode = 500

        return [resultCode, resultHeaders, body]

    def doPOST(self, path, headers, body):
        self.log.debug("oops")
        return [404, {}, ""]


