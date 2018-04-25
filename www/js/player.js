$(function() {
    var debugging = window.location.search.indexOf('debug=1') != -1;
    $('body').toggleClass('debugging', debugging);
    var $log = $('.log');

    var log = function(msg) {
        if (!debugging) {
            return;
        }

        $log.append('[' + new Date().toUTCString() + '] ' + msg + '<br>');
        $log.scrollTop($log[0].scrollHeight);
    };

    var getInactiveIframe = function() {
        return $('iframe').not('.active');
    };

    var isInactiveApplicable = function(url) {
        return (getInactiveIframe().attr('src') == url);
    };

    var setSlideVisibleEvent = function($iframe) {
        if ($iframe.attr('src').indexOf('app.beamy.tv') != -1 || $iframe.attr('src').indexOf('beamy.enflow') != -1) {
            var sendSlideVisible = function() {
                $iframe[0].contentWindow.postMessage({
                    'message': 'slide:visible'
                }, "*");
            };

            if (typeof $iframe[0].contentWindow === "undefined") {
                $iframe.on('load', sendSlideVisible);
            } else {
                sendSlideVisible();
            }
        }
    };

    var setInactiveActive = function() {
        var $inactive = getInactiveIframe();
        $('iframe').removeClass('active');
        $inactive.addClass('active');
        setSlideVisibleEvent($inactive);
    };

    var open = function(data) {
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
        setSlideVisibleEvent($('iframe').first());
    };

    var preload = function(data) {
        log('Preloading ' + data.url);

        // No items are active yet, prevent the 'preload' first 'open' after race condition
        // Only really applicable in development
        if ($('iframe.active').length == 0) {
            return;
        }

        setTimeout(function() {
            getInactiveIframe().attr('src', data.url);
        }, 1000);
    };

    var clear = function(data) {
        log('Clearing active');

        $('iframe.active').attr('src', 'about:blank');
    };

    var ws = new ReconnectingWebSocket("ws://127.0.0.1:13254/");

    ws.onopen = function(evt) {
        log('Opening connection');
    };

    ws.onmessage = function(evt) {
        var data = JSON.parse(evt.data);

        if (data.action == 'open') {
            open(data);
        }

        if (data.action == 'preload') {
            preload(data);
        }

        if (data.action == 'clear') {
            clear(data);
        }
    };
    ws.onclose = function(evt) {
        log('Closing connection');
    };

    open({
        url: 'loading.html'
    });

    /*setTimeout(function () {
        preload({'url': 'http://beamy.enflow/api/v1/player/A9F5170/slide/2045464172'});
    }, 1000);

    setTimeout(function () {
        open({'url': 'http://beamy.enflow/api/v1/player/A9F5170/slide/2045464172'});
    }, 4000);*/
});
