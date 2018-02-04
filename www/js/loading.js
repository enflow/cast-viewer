var updateProgress = function () {
    var current = getHash().current;
    var total = getHash().total;
    if (total) {
        var bar = document.getElementById('loading-progress');

        bar.value = current;
        bar.max = total;

        bar.style.opacity = 1;

        document.getElementById('title').innerHTML = 'Downloaden...';
    }
};

window.onhashchange = updateProgress;
window.onload = updateProgress;
