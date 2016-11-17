$(function () {
    var debugging = window.location.search.indexOf('debug=1') != -1;
    $('body').toggleClass('debugging', debugging);
    var $log = $('.log');

    var log = function (msg) {
        if (!debugging) {
            return;
        }

        $log.append('[' + new Date().toUTCString() + '] ' + msg + '<br>');
        $log.scrollTop($log[0].scrollHeight);
    };

    var getInactiveIframe = function () {
        return $('iframe').not('.active');
    };

    var isInactiveApplicable = function (url) {
        return (getInactiveIframe().attr('src') == url);
    };

    var setInactiveActive = function () {
        var $inactive = getInactiveIframe();
        $('iframe').removeClass('active');
        $inactive.addClass('active');
    };

    var ws = new ReconnectingWebSocket("ws://127.0.0.1:13254/");

    ws.onopen = function (evt) {
        log('Opening connection');
    };

    ws.onmessage = function (evt) {
        var data = JSON.parse(evt.data);

        if (data.action == 'open') {
            log('Opening ' + data.url);

            // Check if we aren't already active
            if (!data.force && $('iframe.active').attr('src') == data.url) {
                return;
            }

            // Check if there is a preload available
            if (isInactiveApplicable(data.url)) {
                setInactiveActive();
                return;
            }

            // Nop, lets just use the first one
            $('iframe').removeClass('active').first().addClass('active').attr('src', data.url);
        }

        if (data.action == 'preload') {
            log('Preloading ' + data.url);

            // No items are active yet, prevent the 'preload' first 'open' after race condition
            // Only really applicable in development
            if ($('iframe.active').length == 0) {
                return;
            }

            setTimeout(function() {
                getInactiveIframe().attr('src', data.url);
            }, 1000);
        }

        if (data.action == 'clear') {
            log('Clearing active');

            $('iframe.active').attr('src', 'about:blank');
        }
    };
    ws.onclose = function (evt) {
        log('Closing connection');
    };
});
