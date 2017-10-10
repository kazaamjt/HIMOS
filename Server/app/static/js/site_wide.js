$(document).ready(function () {

    var redisCheckRateSeconds = 3;
    $('#redis_status_short').parent().attr('title', `Updated every ${redisCheckRateSeconds} seconds`);
    var redisCheck = function () {
        $.get('/api/ping_redis', function () {
        }).success(function () {
            $('#redis_status_short').text('ok');
            $('#redis_status_short').css('color', 'green')
        }).fail(function () {
            console.warn("redis_pong returned 500");
            $('#redis_status_short').text("DOWN");
            $('#redis_status_short').css('color', 'red')
        })
    };
    redisCheck();
    setInterval(redisCheck, redisCheckRateSeconds * 1000)

    $(document).on('click', '.dropdown-menu-click-no-hide', function (e) {
        e.stopPropagation();
    });


    $(".change-theme-btn").click(function(){
        let theme_name = $(this).data('theme');
        $.post('/set_theme', {
            "theme_name": theme_name,
        }).done(function(){
            location.reload()
        })
    })
});
