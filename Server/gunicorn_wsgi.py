from flask_script import Command, Option

"""
The class defines the wsgi server to be used in production.
This is needed since the default flask dev server is not suitable for production.
"""
class Gunicorn(Command):
    description = 'Runs production server with gunicorn'

    def __init__(self, host='127.0.0.1', port=5000, **options):
        self.port = port
        self.host = host
        self.server_options = options


    def get_options(self):
        options = (
            Option('--gunicorn-host',
                   dest='host',
                   default=self.host),

            Option('--gunicorn-port',
                   dest='port',
                   type=int,
                   default=self.port),

            Option('--gunicorn-config',
                   dest='config',
                   type=str,
                   default='/etc/sysmon-server/Server.ini',
                   required=False))

        return options

    def __call__(self, app, host, port, config, **kwargs):
        from configparser import ConfigParser
        gc = ConfigParser()
        gc.read(config)
        section = 'Gunicorn'

        bind = "%s:%s" % (host, str(port))
        workers = gc.get(section, 'workers')
        pidfile = gc.get(section, 'pidfile')
        loglevel = gc.get(section, 'loglevel')

        # Suppress argparse warnings caused by running gunicorn's argparser
        # "inside" Flask-Script which imports it too...
        import warnings, sys
        warnings.filterwarnings("ignore", "^.*argparse.*$")

        from gunicorn import version_info
        if version_info >= (0, 9, 0):
            from gunicorn.app.base import Application

            class FlaskApplication(Application):
                def init(self, parser, opts, args):
                    return {
                        'bind': bind,
                        'workers': workers,
                        'pidfile': pidfile,
                        'loglevel': loglevel
                    }

                def load(self):
                    return app

            sys.argv = sys.argv[:1]
            print(sys.argv)
            print ("Logging to stderr with loglevel '%s'" % loglevel)
            print ("Starting gunicorn...")
            return FlaskApplication().run()
        else:
            raise RuntimeError("Unsupported gunicorn version! Required > 0.9.0")