from setuptools import setup

setup(
    name = 'fakeemail',
    version = '0.1',
    author = 'Tom Wardill',
    author_email = 'tom@howrandom.net',

    zip_safe = True,
    packages = ['fakeemail', 'twisted.plugins'],
    install_requires = [
        'Twisted',
    ],
    package_data={'twisted': ['plugins/fakeemail.py']},
    entry_points = {
        'console_scripts' : [
            'start = fakeemail.server:start'
        ]
    }
)
