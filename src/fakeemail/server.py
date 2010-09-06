from zope.interface import implements

from twisted.application import service
from twisted.python import usage

from smtp_server import WebMessageESMTPFactory, makeSMTPService
from web_server import WebMessageRouter, makeWebService

class WebMessageStorage(object):

    messages = {}

    def addMessage(self, to, message):
        if self.messages.has_key(str(to.dest)):
            self.messages[str(to.dest)].append(message)
        else:
            self.messages[str(to.dest)] = [message]
            
        print self.messages
        
    def get_for_name(self, name):
        if self.messages.has_key(name):
            return self.messages[name]
        return None
    
    def get_all_names(self):
        return self.messages.keys()
    
    def clear_all(self):
        self.messages = {}



class Options(usage.Options):
    optParameters = [
        ["smtp_port", "s", 2025, "SMTP Server Port"],
        ["web_port", "w", 8000 ,"Web Server Port"],
        ]
    

def makeService(config):

    storage = WebMessageStorage()

    s = service.MultiService()

    smtp_port = config.get('smtp_port') if config.get('smtp_port') else 2025
    web_port = config.get('web_port') if config.get('web_port') else 8000
    
    smtpService = makeSMTPService(smtp_port, storage)
    smtpService.setServiceParent(s)

    webService = makeWebService(web_port, storage)
    webService.setServiceParent(s)

    return s

