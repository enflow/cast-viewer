var updateProgress = function () {
    var current = getHash().current;
    var total = getHash().total;
    if (total && current > 0) {
        document.getElementById('title').innerHTML = 'Downloaden... '+Math.floor(current / total * 100)+'%';
    }
};

window.onhashchange = updateProgress;
window.onload = updateProgress;
