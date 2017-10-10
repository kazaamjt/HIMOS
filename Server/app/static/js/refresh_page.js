const refresh_app = (function () {
    /**
     * seconds before auto-reloading the page
     * @type {number}
     */
    var refreshPageSeconds = null;

    /**
     * store the result of setInterval(func, seconds), so that we can stop `func` from continueing being executed
     * in the future
     * @type {number}
     */
    var refresherIntervalId = null;

    const init = function () {

        refreshPageSeconds = parseInt($("#auto-refresh-intervals").val());
        var shouldRefreshInitial = SHOULD_REFRESH_PAGE_INITIAL_FLAG;


        if (SHOULD_REFRESH_PAGE_INITIAL_FLAG) {
            enableRefreshing(false, true); //false because it's already in the session
            console.log("auto-reload is Enabled in the session")
        } else {
            console.log("auto-reload is Disabled in the session")
        }
        console.log(`auto-reload interval is configured to ${refreshPageSeconds} seconds`);


    };

    const updateRefreshInterval = function (seconds) {
        // prevent the page to restart during the post request
        disableRefreshing(false);
        refreshPageSeconds = seconds;

        $.post('/update_refresh_interval/' + seconds, function () {
        }).done(function () {
            console.log("Update session's refresh interval");

        }).fail(function () {
            console.error("Failed to update session's refresh interval");
        }).always(function () {
            // programatically refresh the page (handy in case the auto-refresh toggle was off)
            enableRefreshing(true, false);

        });
    };

    /**
     * Schedules `refresh_page` to be executed every `refreshPageSeconds`
     * @param enableInSession: update the server's session, so that the value on the server is
     * maintained between page loads.
     */
    const enableRefreshing = function (enableInSession, pageJustLoaded) {
        enableInSession = typeof enableInSession !== 'undefined' ? enableInSession : true;
        pageJustLoaded = typeof pageJustLoaded !== 'undefined' ? pageJustLoaded : true;

        refresherIntervalId = setInterval(refresh_page, refreshPageSeconds * 1000); // s -> ms
        if (enableInSession) {
            $.post('/refresh_page_toggle/1', function () {
            }).done(function () {
                console.log("Enabling refreshing");
                if (!pageJustLoaded) {

                    refresh_page()
                }
            }).fail(function () {
                console.error("Can't enable refreshing")
            })
        } else {
            if (!pageJustLoaded) {
                refresh_page()
            }
        }
    };

    /**
     *  Stop any planned refreshes of the pages. Also tell that to the server so that it can update its session
     *  so that on next page load, we know that we shouldn't reload.
     * @param disableInSession: update the server's session, so that the value on the server is
     * maintained between page loads.
     */
    const disableRefreshing = function (disableInSession) {
        disableInSession = typeof disableInSession !== 'undefined' ? disableInSession : true;

        // https://www.w3schools.com/jsref/met_win_clearinterval.asp
        clearInterval(refresherIntervalId);

        if (disableInSession) {
            $.post('/refresh_page_toggle/0', function () {
            }).done(function () {
                console.log("Disabled toggling")
            }).fail(function () {
                console.error("Can't disable toggling")
            })
        }
    };

    const refresh_page = function () {
        console.log("about to refresh...");
        setTimeout(function () {
            location.reload()
        }, 100)
    };

    // the public stuff.
    return {
        init: init,
        enableRefrashing: enableRefreshing,
        disableRefreshing: disableRefreshing,
        updateRefreshInterval: updateRefreshInterval,
    }
})();

//entry point
$(document).ready(function () {
    // initialise the dashboard module
    refresh_app.init();
    // assign event listeners
    $("#enable-refreshing-btn").click(function (ev) {
        console.log("boo")
        refresh_app.enableRefrashing(true, false);
    });
    $('#disable-refreshing-btn').click(function (ev) {
        console.log("baa")
        refresh_app.disableRefreshing();
    });
    $("#auto-refresh-intervals").change(function () {
        var newIntervalSeconds = parseInt($("#auto-refresh-intervals").val());
        refresh_app.updateRefreshInterval(newIntervalSeconds);

    });


});