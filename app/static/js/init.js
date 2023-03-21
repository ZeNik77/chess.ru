function sendinfo(url, cFunction, cnt) {
    const xhttp = new XMLHttpRequest();
    xhttp.onload = function () {
        cFunction(this);
    }
    xhttp.open("POST", url);
    xhttp.setRequestHeader("Content-type", "application/json");
    xhttp.send(cnt);
}