from zope.interface import implementer
from twisted.mail import smtp
from twisted.internet import defer, protocol
from twisted.application import internet


@implementer(smtp.IMessageDelivery)
class WebMessageDelivery:

    def __init__(self, storage):
        self.storage = storage

    def receivedHeader(self, helo, origin, recipients):
        return b"Received: MessageDelivery"

    def validateFrom(self, helo, origin):
        # take any from address
        return origin

    def validateTo(self, user):
        # take any to
        return lambda: WebMessage(self.storage, user)


@implementer(smtp.IMessage)
class WebMessage:

    def __init__(self, storage, user):
        self.lines = []
        self.storage = storage
        self.user = user

    def lineReceived(self, line):
        self.lines.append(line)

    def eomReceived(self):
        message = b"\n".join(self.lines)
        self.storage.addMessage(self.user, message)
        self.lines = None
        return defer.succeed(None)

    def connectionLost(self):
        # some form of error, throw it all away
        self.lines = None


@implementer(smtp.IMessageDeliveryFactory)
class WebMessageDeliveryFactory(object):

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


def makeSMTPService(smtp_port, storage):
    smtpServerFactory = WebMessageESMTPFactory(storage)
    smtpService = internet.TCPServer(smtp_port, smtpServerFactory)

    return smtpService
