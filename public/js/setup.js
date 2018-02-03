window.onload = function () {
    var playerIdentifier = document.getElementById('player-identifier');
    var playerIdentifierValue = getHash().player_identifier;
    if (playerIdentifier && playerIdentifierValue) {
        playerIdentifier.innerHTML = playerIdentifierValue;
    }
};
