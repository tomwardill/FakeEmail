import email
import base64

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
        email_list = self.storage.get_for_name(self.name)
        decoded_email_list = []
        available_content_types = set()
        if email_list:
            for mail in email_list:
                parts = {}
                msg = email.message_from_string(mail.encode('UTF-8'))
                parts['headers'] = msg.items()
                parts['content_type'] = msg.get_content_type()
                for part in msg.walk():
                    # multipart/* are just containers
                    if part.get_content_maintype() == 'multipart':
                        continue

                    payload = part.get_payload(decode=True)
                    if not isinstance(payload, unicode):
                        payload = unicode(payload, 'utf-8')

                    parts[part.get_content_subtype()] = payload
                    available_content_types.add(part.get_content_subtype())
                decoded_email_list.append(parts)

        data = {'email_list': decoded_email_list,
                'address_name': self.name,
                'content_types': list(available_content_types)}

        env = Environment(loader=PackageLoader('fakeemail', 'templates'))
        template = env.get_template('message_display.html')

        return template.render(data).encode('UTF-8')


class WebMessageRootDisplay(Resource):

    def __init__(self, name, storage):
        Resource.__init__(self)
        self.storage = storage

    def internal_render(self, user_message=None):
        address_list = [[self.storage.get_count(name), name]
                        for name in self.storage.get_all_names()]
        data = {'address_list': address_list, 'user_message': user_message}

        env = Environment(loader=PackageLoader('fakeemail', 'templates'))
        template = env.get_template('home_page.html')

        return template.render(data).encode('utf-8')

    def render_GET(self, request, user_message=None):

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

        data = {'email_list': self.storage.get_for_name(self.name),
                'address_name': self.name, }

        env = Environment(loader=PackageLoader('fakeemail', 'templates'))
        template = env.get_template('data_message_display.html')

        data_dump = {'data': json.dumps(data)}

        return template.render(data_dump).encode('utf-8')


class WebDataRootDisplay(Resource):

    def __init__(self, name, storage):
        Resource.__init__(self)
        self.storage = storage

    def internal_render(self, user_message=''):
        address_list = [[self.storage.get_count(name), name]
                        for name in self.storage.get_all_names()]
        data = {'address_list': address_list, 'user_message': user_message}

        env = Environment(loader=PackageLoader('fakeemail', 'templates'))
        template = env.get_template('data_home_page.html')

        data_dump = {'data': json.dumps(data)}

        return template.render(data_dump).encode('utf-8')

    def render_GET(self, request, user_message=None):

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


def makeWebService(web_interface, web_port, storage):
    root = WebMessageRouter(storage)
    siteFactory = Site(root)
    webService = internet.TCPServer(web_port, siteFactory,
                                    interface=web_interface)
    return webService
