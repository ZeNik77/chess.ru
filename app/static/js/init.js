function sendinfo(url, method, cFunction, cnt) {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function () {
        cFunction(this);
    }
    xhttp.open(method, url);
    if (cnt) {
        xhttp.setRequestHeader("Content-type", "application/json");
    }
    xhttp.send(cnt);
}

function getnewroom() {
    const xhttp = new XMLHttpRequest();
    xhttp.open('GET', '/newroom', false);
    xhttp.send();
    return JSON.parse(xhttp.responseText).id
}
