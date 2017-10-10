from jinja2 import Markup

"""
https://code.tutsplus.com/tutorials/templating-with-jinja2-in-flask-date-and-time-formatting-with-momentjs--cms-25813
"""


class momentjs(object):
    def __init__(self, timestamp, ts_is_utc=True):
        self.ts_is_utc = ts_is_utc
        self.timestamp = timestamp

    # Wrapper to call moment.js method
    def render(self, fmt):
        if self.ts_is_utc:
            moment_constructor_string = "moment.utc(\"%s\").local()"
        else:
            moment_constructor_string = "moment(\"%s\")"

        moment_constructor_string = moment_constructor_string % self.timestamp.strftime("%Y-%m-%dT%H:%M:%S")

        return Markup("<script>\ndocument.write(%s.%s);\n</script>" % (moment_constructor_string, fmt))

    def calendar(self):
        return self.render("calendar()")

    def fromNow(self):
        return self.render("fromNow()")
