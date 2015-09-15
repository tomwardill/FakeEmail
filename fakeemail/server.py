from __future__ import print_function

from twisted.application import service
from twisted.python import usage
from zope.interface import implements

from smtp_server import WebMessageESMTPFactory, makeSMTPService
from web_server import WebMessageRouter, Site, makeWebService


class WebMessageStorage(object):

    messages = {}

    def addMessage(self, to, message):
        if unicode(to.dest) in self.messages:
            self.messages[unicode(to.dest)].append(message.decode('UTF-8'))
        else:
            self.messages[unicode(to.dest)] = [message.decode('UTF-8')]

        print("Message stored for: " + unicode(to.dest))

    def get_for_name(self, name):
        if name in self.messages:
            return self.messages[name]
        return None

    def get_all_names(self):
        return self.messages.keys()

    def get_count(self, name):
        return len(self.messages[name])

    def clear_all(self):
        self.messages = {}


class Options(usage.Options):
    optParameters = [
        ["smtp_port", "s", 2025, "SMTP Server Port"],
        ["web_port", "w", 8000, "Web Server Port"],
        ["web_interface", "i", "127.0.0.1", "Web Server Interface"],
    ]


def makeService(config):

    storage = WebMessageStorage()

    s = service.MultiService()

    smtp_port = int(config.get('smtp_port'))
    web_port = int(config.get('web_port'))
    web_interface = config.get('web_interface')

    smtpService = makeSMTPService(smtp_port, storage)
    smtpService.setServiceParent(s)

    webService = makeWebService(web_interface, web_port, storage)
    webService.setServiceParent(s)

    return s


def start(config=None):

    if not config:
        import argparse
        parser = argparse.ArgumentParser()
        parser.add_argument("smtp_port", help="SMTP Port", type=int)
        parser.add_argument("web_port", help="Web Port", type=int)
        parser.add_argument("web_interface",
                            help="Listening interface for web")
        args = parser.parse_args()

        config = {
            'smtp_port': args.smtp_port,
            'web_port': args.web_port,
            'web_interface': args.web_interface
        }

    from twisted.internet import reactor
    storage = WebMessageStorage()
    smtp_factory = WebMessageESMTPFactory(storage)
    root = WebMessageRouter(storage)

    reactor.listenTCP(config['smtp_port'], smtp_factory)
    reactor.listenTCP(config['web_port'], Site(root),
                      interface=config['web_interface'])

    reactor.run()
