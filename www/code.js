

function driveIn(tag) {
    sendCommand(tag, 'in');
}

function driveOut(tag) {
    sendCommand(tag, 'out');
}

function driveStop(tag) {
    sendCommand(tag, 'stop');
}
function sendCommand(tag, cmd) {
    console.log(tag)
    const params = { tag : tag, cmd : cmd };
    var http = new XMLHttpRequest();
    var url = "/pbcapi"
    http.open('POST', url, true);
    http.setRequestHeader('Content-Type', 'application/json');
    http.send(JSON.stringify(params))
}