$(function () {
    $.get('/ssid', function (data) {
        if (data.length === 0) {
            $('.js-before-submit').hide();
            $('.no-networks-message').removeAttr('hidden');
        } else {
            $.each(JSON.parse(data), function (i, val) {
                $(".js-ssid-select").append('<button class="list-group-item list-group-item-action js-select-wifi-network">' + val + '</button>');
            });
        }
    });

    $('.js-connect-form').submit(function (e) {
        e.preventDefault();

        $('.js-submit-button').attr('disabled', 'disabled');

        $.post('/connect', $('.js-connect-form').serialize(), function (data) {
            $('.js-before-submit').hide();
            $('.submit-message').removeAttr('hidden');
        });
    });

    $(document).on('click', '.js-select-wifi-network', function () {
        $('input[name="ssid"]').val($(this).html());
        $('.js-select-wifi-network').removeClass('active');
        $(this).addClass('active');
        return false;
    });
});
