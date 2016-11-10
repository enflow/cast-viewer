function getParameterByName(name) {
    var match = RegExp('[?&]' + name + '=([^&]*)').exec(window.location.search);
    return match && decodeURIComponent(match[1].replace(/\+/g, ' '));
}

window.onload = function () {
    var playerIdentifier = document.getElementById('player-identifier');
    var playerIdentifierValue = getParameterByName('player_identifier');
    if (playerIdentifier && playerIdentifierValue) {
        playerIdentifier.innerHTML = playerIdentifierValue;
    }
};
