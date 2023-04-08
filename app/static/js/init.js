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

function getnewroom(type) {
    const xhttp = new XMLHttpRequest();
    var pack = {type: type}
    xhttp.open('POST', '/newroom', false);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send(JSON.stringify(pack));
    return JSON.parse(xhttp.responseText).id
}
