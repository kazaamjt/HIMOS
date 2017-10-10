from flask import render_template, session, flash, current_app, json, request

from Server.app.api_utils import fail_with
from Server.app.utils import auto_reloadable, refresh_every_seconds_key, refresh_flag_key, add_to_collapsed, \
	get_collapsed, session_prefix_for_collapsed
from . import main
from Server.app.measurements_redis_adapter import ComputerMeasurementsRedisAdapter
from datetime import datetime
from Server.app.utils import from_string_to_datetime


@main.route('/', methods=['GET', 'POST'])
@auto_reloadable
def index(auto_reloading_kwargs={}):
	all_host_names = ComputerMeasurementsRedisAdapter.get_all_monitored_hostnames()
	all_host_names = list(sorted(all_host_names))
	dead_nodes_objects = []
	dead_nodes_names = []
	computers = []
	for index, host_name in enumerate(all_host_names):
		node = ComputerMeasurementsRedisAdapter.get_newest_computer_measurement_from_redis(host_name,
																									 deserialize=True)
		entry = (host_name, node)
		computers.append(entry)
		if is_node_dead(node):
			dead_nodes_objects.append(entry)
			dead_nodes_names.append(host_name)

	return render_template('dashboard.html', host_names=all_host_names, computers=computers,
						   dead_host_objects=dead_nodes_objects,
						   dead_host_names=dead_nodes_names,
						   **auto_reloading_kwargs)


@main.route('/node_info/<node_identifier>')
@auto_reloadable
def node_info(node_identifier, auto_reloading_kwargs={}):
	computer_measurements = ComputerMeasurementsRedisAdapter.get_all_for_node(node_identifier,
																						  deserialize=True)

	newest_computer_measurement = computer_measurements[-1]
	is_dead = is_node_dead(newest_computer_measurement)
	older_computers = list(reversed(computer_measurements[0: -1]))

	return render_template('single_computer.html',
						   computer=newest_computer_measurement,
						   older_computers=older_computers,
						   is_dead=is_dead,
						   **auto_reloading_kwargs)


@main.route('/update_refresh_interval/<int:seconds>', methods=['POST'])
def update_refresh_interval(seconds):
	assert seconds and seconds > 0
	session[refresh_every_seconds_key] = seconds
	return ''


@main.route('/refresh_page_toggle/<int:flag>', methods=['POST'])
def refresh_page_toggle(flag):
	assert flag is 0 or flag is 1
	session[refresh_flag_key] = True if flag is 1 else False
	return ''


######
# Collapsed panels
# if a user of the dashboard collapses a panel, remember which panel was that

@main.route('/collapse_multi', methods=['POST'])
def collapse_multi():
	dom_ids = request.form.get("ids")
	dom_ids = json.loads(dom_ids)
	for id in dom_ids:
		add_to_collapsed(id)

	return 'ok'


@main.route('/get_collapsed')
def _get_collapsed():
	return json.dumps(get_collapsed())


@main.route('/clear_collapsed')
def _clear_all_collapsed():
	to_delete = [key for key in session if key.startswith(session_prefix_for_collapsed)]
	for key in to_delete:
		del session[key]
	return 'ok'


@main.route("/remove_from_collapsed_multi", methods=['DELETE'])
def remove_from_collapsed():
	ids_json = request.form.get('ids')
	for id in json.loads(ids_json):
		if not (session_prefix_for_collapsed + id) in session:
			return fail_with("%s is not in the collapsed session" % id, 418)
		del session[session_prefix_for_collapsed + id]

	return 'cleared'


#### theme
@main.route('/set_theme', methods=['POST'])
def set_theme():
	theme = request.form.get('theme_name')
	session['theme'] = theme
	return ''


#########
def is_node_dead(node):
	"""
	:return: boolean - true if the node hasn't reported for more than NODE_GONE_AFTER seconds
	"""
	now_utc = datetime.utcnow()
	last_measurement_utc = from_string_to_datetime(node.time_now_utc)
	last_update_before_seconds = (now_utc - last_measurement_utc).total_seconds()
	return last_update_before_seconds > current_app.config['NODE_GONE_AFTER']
