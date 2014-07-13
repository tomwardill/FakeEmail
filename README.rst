=========
FakeEmail
=========

FakeEmail is an email server, for use in a development environment where routing email is either undesirable, or impossible to manage.

The aim of the system is to open a port, accept SMTP connections and to display a list of the emails that it has received. 
At no point will the emails route further on, so there is no requirement for the addresses to be valid, or to wait around waiting for the email to arrive in your inbox.

Installation
------------

Via pip
~~~~~~~

FakeEmail is installable via pip:

  pip install fakeemail


From Source
~~~~~~~~~~~

FakeEmail is installed using the buildout system and depends on Twisted for it's server capabilites. Installation is as straight forward as possible::

  git clone git://github.com/tomwardill/FakeEmail.git
  cd FakeEmail
  python bootstrap.py
  bin/buildout
  
  
Usage
-----

From pip install
~~~~~~~~~~~~~~~~

If you installed fakeemail via pip, then running is simple:

  fakeemail 2025 8080 0.0.0.0


This will run on SMTP port `2025`, the web interface on `8080` and listen on all network interfaces. Running on port 25 is possible, but you will need to start with root privileges.

Installed from source
~~~~~~~~~~~~~~~~~~~~~

FakeEmail installs itself as a plugin into the local buildout twisted environment. This makes execution reasonably simple::

  bin/twistd -n fakeemail
  
There are two options for the system:

 * -s or --smtp_port : Which port to run the SMTP listener on (defaults to 2025)
 * -w or --web_port : Which port to run the Web Server on (defaults to 8000)
 
Use these options as shown below::

  bin/twistd -n fakeemail -s 1025 -w 8001
  
Note that to run the SMTP listener on port 25 (the standard SMTP port), you may need to start the daemon with root privileges.

Once the server is running, direct any email at the port that you specified, and then load up http://<servername>:webport (http://localhost:8000 for example)

Run the server in the background and output to a log file::

  bin/twistd -l foo.log fakeemail

Dependencies
------------

The dependencies will be installed through the egg/buildout, but if you require them to be system installed, they are listed below:

 * twisted
 * jinja2
 * python (2.4+)