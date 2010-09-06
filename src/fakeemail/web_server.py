from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.application import internet, service

class WebMessageDisplay(Resource):

    def __init__(self, name, storage):
        Resource.__init__(self)
        self.name = name
        self.storage = storage

    def render_GET(self, request):
        if self.storage.get_for_name(self.name):
            html_string = "<html><body><ul>"
            for email in self.storage.get_for_name(self.name):
                html_string += "<li><pre>%s</pre></li>" % (email, )
            html_string += "</ul></body></html>"
            return html_string
        else:
            return "<html><body><pre>No emails recorded</pre></body></html>"
        
class WebMessageRootDisplay(Resource):
    
    def __init__(self, name, storage):
        Resource.__init__(self)
        self.storage = storage
        
    def render_GET(self, request):
        html_string =  "<html><body><ul>"
        for name in self.storage.get_all_names():
            html_string += "<li>(%s) <a href='%s'>%s</a></li>" % ( self.storage.get_count(name), name, name, )
        html_string += "</ul><form action='.' method='POST'><input type='submit' value='Clear All'></form></body></html>"
        return html_string
    
    def render_POST(self, request):
        self.storage.clear_all()
        return "<html><body>Cleared</body></html>"

class WebMessageRouter(Resource):

    def __init__(self, storage):
        Resource.__init__(self)
        self.storage = storage

    def getChild(self, name, request):
        if name:
            return WebMessageDisplay(name, self.storage)
        else:
            return WebMessageRootDisplay(name, self.storage)
        
def makeWebService(web_port, storage):
    root = WebMessageRouter(storage)
    siteFactory = Site(root)
    webService = internet.TCPServer(web_port, siteFactory)
    return webService