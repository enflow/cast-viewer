window.onload = function () {
    var ssid = document.getElementById('ssid');
    var ssidValue = getHash().ssid;
    if (ssid && ssidValue) {
        ssid.innerHTML = ssidValue;
    }
};
