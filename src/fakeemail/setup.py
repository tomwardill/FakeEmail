from setuptools import setup

setup(
    name = 'fakeemail',
    version = '0.1',
    author = 'Tom Wardill',
    author_email = 'tom@howrandom.net',

    zip_safe = True,
    packages = ['fakeemail'],
    install_requires = [
        'Twisted',
    ]

    entry_points = {
        'console_scripts' : [
            'start = server:start'
        ]
    }
)
