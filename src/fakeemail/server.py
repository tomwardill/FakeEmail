from zope.interface import implements

from twisted.application import internet
from twisted.internet import defer, protocol
from twisted.mail import smtp
from twisted.mail.mail import MailService
from twisted.python import usage

class WebMessageDelivery:
    implements(smtp.IMessageDelivery)

    def __init__(self, parent):
        self.parent = parent

    def receivedHeader(self, helo, origin, recipients):
        return "Recieved: MessageDelivery"

    def validateFrom(self, helo, origin):
        # take any from address
        return origin

    def validateTo(self, user):
        # take any to
        return lambda: WebMessage(self)

    def addMessage(self, message):
        self.parent.addMessage(message)


class WebMessage:
    implements(smtp.IMessage)

    def __init__(self, parent):
        self.lines = []
        self.parent = parent

    def lineReceived(self, line):
        self.lines.append(line)

    def eomReceived(self):
        message = "\n".join(self.lines)
        self.parent.addMessage(message)
        self.lines = None
        return defer.succeed(None)

    def connectionLost(self):
        # some form of error, throw it all away
        self.lines = None

class WebMessageDeliveryFactory(object):
    implements(smtp.IMessageDeliveryFactory)

    def __init__(self, parent):
        self.parent = parent

    def getMessageDelivery(self):
        return WebMessageDelivery(self)

    def addMessage(self, message):
        self.parent.messages.append(message)
        print self.parent.messages

class WebMessageESMTPFactory(protocol.ServerFactory):
    protocol = smtp.ESMTP

    messages = []

    def buildProtocol(self, addr):
        p = self.protocol()
        p.deliveryFactory = WebMessageDeliveryFactory(self)
        p.deliveryFactory.factory = self
        p.factory = self
        return p

class Options(usage.Options):
    pass

def makeService(config):
    smtpServerFactory = WebMessageESMTPFactory()

    return internet.TCPServer(2025, smtpServerFactory)

