from zope.interface import implements

from twisted.application import internet, service
from twisted.internet import defer, protocol
from twisted.mail import smtp
from twisted.python import usage

from twisted.web.server import Site
from twisted.web.resource import Resource

class WebMessageStorage(object):

    messages = {}

    def addMessage(self, to, message):
        if self.messages.has_key('to'):
            self.messages[to.dest].append(message)
        else:
            self.messages[to.dest] = [message]

class WebMessageDelivery:
    implements(smtp.IMessageDelivery)

    def __init__(self, storage):
        self.storage = storage

    def receivedHeader(self, helo, origin, recipients):
        return "Recieved: MessageDelivery"

    def validateFrom(self, helo, origin):
        # take any from address
        return origin

    def validateTo(self, user):
        # take any to
        return lambda: WebMessage(self.storage, user)


class WebMessage:
    implements(smtp.IMessage)

    def __init__(self, storage, user):
        self.lines = []
        self.storage = storage
        self.user = user

    def lineReceived(self, line):
        self.lines.append(line)

    def eomReceived(self):
        message = "\n".join(self.lines)
        self.storage.addMessage(self.user, message)
        self.lines = None
        return defer.succeed(None)

    def connectionLost(self):
        # some form of error, throw it all away
        self.lines = None

class WebMessageDeliveryFactory(object):
    implements(smtp.IMessageDeliveryFactory)

    def __init__(self, storage):
        self.storage = storage

    def getMessageDelivery(self):
        return WebMessageDelivery(self.storage)


class WebMessageESMTPFactory(protocol.ServerFactory):
    protocol = smtp.ESMTP

    storage = None

    def __init__(self, storage):
        self.storage = storage

    def buildProtocol(self, addr):
        p = self.protocol()
        p.deliveryFactory = WebMessageDeliveryFactory(self.storage)
        p.factory = self
        return p

class Options(usage.Options):
    pass

class WebMessageDisplay(Resource):

    def __init__(self, name):
        Resource.__init__(self)
        self.name = name

    def render_GET(self, request):
        return "<html><body><pre>%s</pre></body></html>" % (self.name,)

class WebMessageRouter(Resource):
    def getChild(self, name, request):
        return

def makeService(config):

    storage = WebMessageStorage()

    smtpServerFactory = WebMessageESMTPFactory(storage)


    s = service.MultiService()

    smtpService = internet.TCPServer(2025, smtpServerFactory)
    smtpService.setServiceParent(s)

    return s

