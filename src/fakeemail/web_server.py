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

            email_list = self.storage.get_for_name(self.name)
            email_list = zip(range(len(email_list)), email_list)
            
            html_string = "<html><body>"
            
            # add quick nav bar
            html_string += "<div>"
            for num, email in email_list:
                html_string += "<a href='#%s'>%s</a>" % (str(num), str(num))
            html_string += "</div>"
            
            html_string += "<ul>"
            for num, email in email_list:
                html_string += "<a name='%s'><li><pre>%s</pre></a></li>" % (num, email, )
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