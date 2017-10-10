const admin_app = (function () {

    const init = function () {
    };
    const refresh_page = function () {
        location.reload()
    };
    const forgetHost = function (hostname) {
        var url = '/admin_api/forget_host/' + hostname;
        var msg = "Are you sure you want to forget this host? All its readings will be deleted and measurements from it will be ignored.";
        var http_verb = 'DELETE';

        ask_and_then_send(url, msg, http_verb, () => {
            alert(`${hostname} will be ignored in the future.`)
            refresh_page()
        })
    };
    const unforgetHost = function (hostname) {
        var url = '/admin_api/unforget_host/' + hostname;
        var msg = "Are you sure you want to unforget this host?.";
        var http_verb = 'POST';

        ask_and_then_send(url, msg, http_verb, () => {
            alert(`We will accept measurements from ${hostname} from now on.`)
            refresh_page()
        })
    };
    const deleteMeasurements = function (hostname) {
        var url = '/admin_api/delete_host_readings/' + hostname;
        var msg = "Are you sure you want to delete the measurements for this host? If new measurements arrive they will still be visible on the dashboard.";
        var http_verb = 'DELETE';
        ask_and_then_send(url, msg, http_verb, () => {
            alert(`All measurements for ${hostname} were deleted.`)
            refresh_page()
        })
    };

    const ask_and_then_send = function (url, msg, http_verb, callback_succ) {
        var canProceed = confirm(msg);
        if (canProceed) {
            $.ajax({
                url: url,
                type: http_verb,
                success: callback_succ,
                error: () => {
                    alert(`Couldn't perform ${http_verb} operation on ${url} ` + url)
                }
            })
        }
    };
    // the public stuff.
    return {
        init: init,
        forgetHost: forgetHost,
        deleteMeasurements: deleteMeasurements,
        unforgetHost: unforgetHost,

    }
})();

//entry point
$(document).ready(function () {
    // initialise the dashboard module
    admin_app.init();
    $('.forget-host-btn').click(function (ev) {
        var $el = $(ev.target);
        admin_app.forgetHost($el.attr('data-host'))
    })

    $('.unforget-host-btn').click(function (ev) {
        var $el = $(ev.target);
        admin_app.unforgetHost($el.attr('data-host'))
    })

    $('.delete-host-readings-btn').click(function (ev) {
        var $el = $(ev.target);
        admin_app.deleteMeasurements($el.attr('data-host'))
    })


});