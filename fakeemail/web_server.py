import os

from twisted.web.server import Site
from twisted.web.resource import Resource
from twisted.application import internet
from twisted.web.static import File

from jinja2 import Environment, PackageLoader

try:
    import json
except ImportError:
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
            for msg, attachments in email_list:
                parts = {}
                parts['headers'] = msg.items()
                parts['content_type'] = msg.get_content_type()
                for part in msg.walk():
                    # multipart/* are just containers, and things that
                    # don't start with 'text/' are assumed to be
                    # attachments
                    is_multipart = (part.get_content_maintype() == 'multipart')
                    is_text = part.get_content_type().startswith('text/')
                    if is_multipart or not is_text:
                        continue

                    content_type = part.get_content_type()
                    # Assume that any non-text types are just attachments
                    if content_type.startswith('text/'):
                        payload = part.get_payload(decode=True)
                        if isinstance(payload, bytes):
                            output = payload.decode('utf-8')
                        else:
                            output = payload

                    parts[part.get_content_subtype()] = output
                    available_content_types.add(part.get_content_subtype())

                # Output the names of the attachments.
                for i, attachment_path in enumerate(attachments, start=1):
                    heading = 'attachment {}'.format(i)
                    parts[heading] = os.path.basename(attachment_path)
                    available_content_types.add(heading)

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
        # Don't try to output the attachments over the data api.
        email_and_attachment_list = self.storage.get_for_name(self.name)
        email_list = [str(email) for email, _ in email_and_attachment_list]

        data = {'email_list': email_list,
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
        name = name.decode('UTF-8', errors='replace')
        return WebDataMessageDisplay(name, self.storage)


class WebMessageRouter(Resource):

    def __init__(self, storage, temp_dir):
        Resource.__init__(self)
        self.storage = storage
        self.temp_dir = temp_dir

    def getChild(self, name, request):
        if name:
            name = name.decode('UTF-8', errors='replace')
            if name == 'data':
                return WebDataRootDisplay('', self.storage)
            elif name == 'file':
                return File(self.temp_dir)

            return WebMessageDisplay(name, self.storage)
        else:
            return WebMessageRootDisplay(name, self.storage)


def makeWebService(web_interface, web_port, storage):
    root = WebMessageRouter(storage)
    siteFactory = Site(root)
    webService = internet.TCPServer(web_port, siteFactory,
                                    interface=web_interface)
    return webService
