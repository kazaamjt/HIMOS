const collapse_manager = (function () {

    const separator = "____";
    const currentPath = window.location.pathname;
    const prefix = `${currentPath}${separator}`;

    const init = function () {
        let dataFromSession = $("#collapsed-by-default-elements").data('ids');
        console.log(dataFromSession);
        let parsedIds = dataFromSession.map(raw_id => raw_id.replace(prefix, ""));

        // collapse all stuff that has to be collapsed
        for (let id of parsedIds) {
            $(`#${id}`).collapse('hide')
        }
    };
    const handleCollapsedMulti = function (raw_ids) {
        $.ajax({
            type : "POST",
            url : '/collapse_multi',
            data : {
                'ids' : JSON.stringify(raw_ids.map(raw_id => `${prefix}${raw_id}`))
            },
        })
    };
    const handleExtendedMulti = function (raw_ids) {
        $.ajax({
            type : 'DELETE',
            url : '/remove_from_collapsed_multi',
            data : {
                'ids' : JSON.stringify(raw_ids.map(raw_id => `${prefix}${raw_id}`))
            },
        })
    };

    return {
        init : init,
        handleCollapsedMulti : handleCollapsedMulti,
        handleExtendedMulti : handleExtendedMulti,
    }
})();

function addListeners() {
    // individual panel's collapse/expand button handler
    $(".btn-collapse").on('click', function (ev) {
        let panel_id = $(this).data('body-id');

        if ($("#" + panel_id).hasClass('in')) {
            console.log(`${panel_id} handleCollapsed`);
            collapse_manager.handleCollapsedMulti([panel_id]);
        } else {
            console.log(`${panel_id} handleExtended`);
            collapse_manager.handleExtendedMulti([panel_id]);
        }
    });

    // the "collapse all" btn on the top right of pages
    $('.panels-collapse-btn').click(function (ev) {
        let ids = [];
        $('.collapse').each(function () {
            $(this).collapse('hide');
            ids.push($(this).attr('id'));
        });

        collapse_manager.handleCollapsedMulti(ids)
    });

    // the "expand all " btn to uncollapse all panels
    $('.panels-show-btn').click(function (ev) {
        let ids = [];
        $('.collapse').each(function () {
            $(this).collapse('show');
            ids.push($(this).attr('id'));
        });

        collapse_manager.handleExtendedMulti(ids);
    })
}

$(document).ready(function () {
    // collapses what should be collapsed
    collapse_manager.init();
    // listen to new collapse/uncollapse events for both individual panels AND the "expand/shrink all" buttons
    addListeners()
});
