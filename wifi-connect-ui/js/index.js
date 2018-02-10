$(function () {
    $.get('/ssid', function (data) {
        if (data.length === 0) {
            $('.js-before-submit').hide();
            $('.no-networks-message').removeAttr('hidden');
        } else {
            $(".js-ssid-select").append('<option value="">Maak een keuze</option>');
            $.each(JSON.parse(data), function (i, val) {
                $(".js-ssid-select").append($('<option>').attr('val', val).text(val));
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
});
