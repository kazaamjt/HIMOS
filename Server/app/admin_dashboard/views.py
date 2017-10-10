from . import admin
from flask import render_template, flash, current_app
from Server.app.measurements_redis_adapter import ComputerMeasurementsRedisAdapter as redis_adapter


@admin.route("/manage")
def manage():

    all_host_names = redis_adapter.get_all_monitored_hostnames()
    newest_measurement_from = [redis_adapter.get_newest_computer_measurement_from_redis(host).time_now_utc for host in
                                    all_host_names]

    forgotten_hosts = redis_adapter.get_forgotten_hosts()

    server_settings = {
        'NODE_GONE_AFTER' : current_app.config['NODE_GONE_AFTER'],
        "MAX_ENTRIES_PER_NODE": current_app.config['MAX_ENTRIES_PER_NODE'],
        "REDIS_HOST": current_app.config['REDIS_HOST'],
        "REDIS_PORT": current_app.config['REDIS_PORT'],
        "REDIS_DB": current_app.config['REDIS_DB'],
    }

    return render_template('admin/admin_dash.html', all_host_names=all_host_names, forgotten_hosts=forgotten_hosts, server_settings=server_settings,
                           newest_measurement_from=newest_measurement_from)

