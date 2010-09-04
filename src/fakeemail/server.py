from zope.interface import implements

from twisted.internet import defer, protocol
from twisted.mail import smtp
from twisted.mail.mail import MailService
from twisted.python import usage

class WebMessageDelivery:
    implements(smtp.IMessageDelivery)

    def receivedHeader(self, helo, origin, recipients):
        return "Recieved: MessageDelivery"

    def validateFrom(self, helo, origin):
        # take any from address
        return origin

    def validateTo(self, user):
        # take any to
        return lambda: WebMessage()


class WebMessage:
    implements(smtp.IMessage)

    def __init__(self):
        self.lines = []

    def lineReceived(self, line):
        self.lines.append(line)

    def eomReceived(self):
        print "New message received:"
        print "\n".join(self.lines)
        self.lines = None
        return defer.succeed(None)

    def connectionLost(self):
        # some form of error, throw it all away
        self.lines = None

class WebMessageDeliveryFactory(object):
    implements(smtp.IMessageDeliveryFactory)

    def getMessageDelivery(self):
        return WebMessageDelivery()

class WebMessageESMTPFactory(protocol.ServerFactory):
    protocol = smtp.ESMTP

    def buildProtocol(self, addr):
        p = self.protocol()
        p.deliveryFactory = WebMessageDeliveryFactory()
        p.factory = self
        return p

class Options(usage.Options):
    pass

def makeService(config):
    smtpServerFactory = WebMessageESMTPFactory()

    return internet.TCPserver(2025, smtpServerFactory)

