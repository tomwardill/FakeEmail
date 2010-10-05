from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.application import internet, service

from jinja2 import Environment, PackageLoader

try:
    import json
except:
        import simplejson as json

class WebMessageDisplay(Resource):

    def __init__(self, name, storage):
        Resource.__init__(self)
        self.name = name
        self.storage = storage

    def render_GET(self, request):
        
        data = {'email_list' : self.storage.get_for_name(self.name),
                'address_name' : self.name,
                }
        
        env = Environment(loader = PackageLoader('fakeemail', 'templates'))
        template = env.get_template('message_display.html')
        
        return template.render(data).encode('utf-8')
        
class WebMessageRootDisplay(Resource):
    
    def __init__(self, name, storage):
        Resource.__init__(self)
        self.storage = storage
        
    def internal_render(self, user_message = None):
        address_list = [ [self.storage.get_count(name), name] for name in self.storage.get_all_names()]
        data = {'address_list': address_list, 'user_message': user_message}
        
        env = Environment(loader = PackageLoader('fakeemail', 'templates'))
        template = env.get_template('home_page.html')
        
        return template.render(data).encode('utf-8')
        
    def render_GET(self, request, user_message = None):
        
        return self.internal_render()
        
    
    def render_POST(self, request):
        self.storage.clear_all()
        return self.internal_render('Data Cleared')
    
class WebDataMessageDisplay(Resource):

    def __init__(self, name, storage):
        Resource.__init__(self)
        self.name = name
        self.storage = storage

    def render_GET(self, request):
        
        data = {'email_list' : self.storage.get_for_name(self.name),
                'address_name' : self.name,
                }
        
        env = Environment(loader = PackageLoader('fakeemail', 'templates'))
        template = env.get_template('data_message_display.html')
        
        data_dump = {'data': json.dumps(data)}
        
        return template.render(data_dump).encode('utf-8')
    
    
class WebDataRootDisplay(Resource):
    
    def __init__(self, name, storage):
        Resource.__init__(self)
        self.storage = storage
        
    def internal_render(self, user_message = ''):
        address_list = [ [self.storage.get_count(name), name] for name in self.storage.get_all_names()]
        data = {'address_list': address_list, 'user_message': user_message}
        
        env = Environment(loader = PackageLoader('fakeemail', 'templates'))
        template = env.get_template('data_home_page.html')
        
        data_dump = {'data':json.dumps(data)}
        
        return template.render(data_dump).encode('utf-8')
        
    def render_GET(self, request, user_message = None):
        
        return self.internal_render()
    
    def render_POST(self, request):
        self.storage.clear_all()
        return self.internal_render('Data Cleared')
    
    def getChild(self, name, request):
        return WebDataMessageDisplay(name, self.storage)
    
class WebMessageRouter(Resource):

    def __init__(self, storage):
        Resource.__init__(self)
        self.storage = storage

    def getChild(self, name, request):
        if name:
            if name == 'data':
                return WebDataRootDisplay('', self.storage)
            
            return WebMessageDisplay(name, self.storage)
        else:
            return WebMessageRootDisplay(name, self.storage)
        
def makeWebService(web_port, storage):
    root = WebMessageRouter(storage)
    siteFactory = Site(root)
    webService = internet.TCPServer(web_port, siteFactory)
    return webService