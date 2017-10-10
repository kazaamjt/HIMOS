#!/usr/bin/env python3
from flask_script import Manager, Server, Shell

from Server.Config import settings
from Server.app import create_app
from Server.gunicorn_wsgi import *

def make_app():
    return create_app(settings.Run_Level)

# we can pass a function returning an app to the Manager, instead of passing him an app straight away
manager = Manager(make_app)

if settings.Run_Level == 'production':
    # running a hardened server (not a weak flask development)
    # http://stackoverflow.com/questions/15693192/heroku-node-js-error-web-process-failed-to-bind-to-port-within-60-seconds-of
    manager.add_command("runserver", Gunicorn(host=settings.Address, port=settings.Port))

else:
    manager.add_command("runserver", Server(host=settings.Address, threaded=True))

@manager.command
def test(folder=""):
    import unittest
    tests_folder = unittest.TestLoader().discover('Server/tests/%s' % folder)
    unittest.TextTestRunner(verbosity=2).run(tests_folder)

if __name__ == '__main__':
    manager.run()
