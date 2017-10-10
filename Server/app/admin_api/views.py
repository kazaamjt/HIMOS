from flask import flash

from . import admin_api
from Server.app.measurements_redis_adapter import ComputerMeasurementsRedisAdapter as redis_adapter


@admin_api.route('/delete_host_readings/<hostname>', methods=["DELETE"])
def delete_host_readings(hostname):
    print("Deleting %s's readings" % hostname)
    if redis_adapter.delete_node(hostname):
        flash("All readings for host %s were deleted " % hostname, 'warning')
    else:
        flash("No readings were found for host %s" % hostname, 'danger')
    return ''


@admin_api.route('/forget_host/<hostname>', methods=["DELETE"])
def forget_host(hostname):
    print("Forgetting %s" % hostname)
    redis_adapter.forget_node(hostname)
    flash(
        "Node %s was forgotten. No measurements from this node will be saved and it will be hidden from the dashboard." % hostname,
        'warning')
    return ''


@admin_api.route('/unforget_host/<hostname>', methods=["POST"])
def unforget_host(hostname):
    print("Unforgetting %s" % hostname)
    if redis_adapter.unforget_node(hostname):
        flash("Host %s was unforgotten - new measurements from it will be saved" % hostname, 'success')
    else:
        flash("Host %s was never forgotten" % hostname, 'danger')
    return ''
