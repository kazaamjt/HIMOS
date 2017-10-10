from functools import wraps
from dateutil.parser import parse
from flask import session


def from_string_to_datetime(d_str):
	return parse(d_str)


## utils for pages which can autorefresh

# how often we refresh
refresh_every_seconds_key = 'rfrsh_seconds'
# should we refresh
refresh_flag_key = 'rfrsh_flag'
refresh_interval_opts = [
	(5, '5 seconds'),
	(10, '10 seconds'),
	(60, '1 minute'),
	(600, '10 minutes'),
]


# wraps view functions/
# sets variables which the jinja template will need (and the .js)
# the view funciton should pass the **auto_reloading_kwargs to a jinja template which uses the auto_reload_bar block
def auto_reloadable(func):
	@wraps(func)
	def decorated(*args, **kwargs):
		should_refresh_page_flag = session.get(refresh_flag_key, True)
		refresh_interval_seconds = int(session.get(refresh_every_seconds_key, refresh_interval_opts[0][0]))
		auto_reloading_kwargs = {
			'page_is_autoreloadable': True,
			'should_refresh_page_flag': should_refresh_page_flag,
			'refresh_interval_seconds': refresh_interval_seconds,
			'refresh_interval_options': refresh_interval_opts,
		}
		return func(*args, auto_reloading_kwargs=auto_reloading_kwargs, **kwargs)

	return decorated


### Collapsed items in the frontend
session_prefix_for_collapsed = 'collapsed_by_default_'


def get_collapsed() -> list:
	all_session_keys = [str(key) for key in session]
	return [key.replace(session_prefix_for_collapsed, '') for key in all_session_keys if
			key.startswith(session_prefix_for_collapsed)]


def add_to_collapsed(id: str):
	session[session_prefix_for_collapsed + id] = True
