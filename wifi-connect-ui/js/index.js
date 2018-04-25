$(function () {
    $.get('/ssid', function (data) {
        if (data.length === 0) {
            $('.js-before-submit').hide();
            $('.no-networks-message').removeAttr('hidden');
        } else {
            $.each(JSON.parse(data), function (i, val) {
                if (val) {
                    $(".js-ssid-select").append('<button class="list-group-item list-group-item-action js-select-wifi-network">' + val + '</button>');
                }
            });
        }
    });

    $('.js-connect-form').submit(function (e) {
        e.preventDefault();

        $('.js-before-submit').hide();
        $('.submit-message').removeAttr('hidden');

        setTimeout(function () {
            $.post('/connect', $('.js-connect-form').serialize(), function (data) {
            });
        }, 1500);

        setTimeout(function () {
            $('.connect-warning').animate({ opacity: 1 });
        }, 3500);
    });

    $(document).on('click', '.js-select-wifi-network', function () {
        $('input[name="ssid"]').val($(this).html());
        $('.js-select-wifi-network').removeClass('active');
        $(this).addClass('active');

        $('html, body').animate({
            scrollTop: $(this).offset().top
        }, 250, function () {
            $(".js-connect-form input[name='passphrase']").focus();
        });

        return false;
    });
});
