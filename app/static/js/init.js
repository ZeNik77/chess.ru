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