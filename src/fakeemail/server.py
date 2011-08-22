from zope.interface import implements

from twisted.application import service
from twisted.python import usage

from smtp_server import WebMessageESMTPFactory, makeSMTPService
from web_server import WebMessageRouter, makeWebService

class WebMessageStorage(object):

    messages = {}

    def addMessage(self, to, message):
        if self.messages.has_key(unicode(to.dest)):
            self.messages[unicode(to.dest)].append(message.decode('UTF-8'))
        else:
            self.messages[unicode(to.dest)] = [message.decode('UTF-8')]
            
        print "Message stored for: " + unicode(to.dest)
        
    def get_for_name(self, name):
        if self.messages.has_key(name):
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
        ["web_port", "w", 8000 ,"Web Server Port"],
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

