var server_port = 65432;
var server_addr = "192.168.68.110";   // the IP address of your Raspberry PI

document.onkeydown = updateKey;
document.onkeyup = resetKey;

// for detecting which key is been pressed w,a,s,d
function updateKey(e) {

    e = e || window.event;

    if (e.keyCode == '87') {
        // up (w)
        document.getElementById("upArrow").style.color = "green";
        send_data("87");
    }
    else if (e.keyCode == '83') {
        // down (s)
        document.getElementById("downArrow").style.color = "green";
        send_data("83");
    }
    else if (e.keyCode == '65') {
        // left (a)
        document.getElementById("leftArrow").style.color = "green";
        send_data("65");
    }
    else if (e.keyCode == '68') {
        // right (d)
        document.getElementById("rightArrow").style.color = "green";
        send_data("68");
    }
}

// reset the key to the start state 
function resetKey(e) {

    e = e || window.event;

    document.getElementById("upArrow").style.color = "grey";
    document.getElementById("downArrow").style.color = "grey";
    document.getElementById("leftArrow").style.color = "grey";
    document.getElementById("rightArrow").style.color = "grey";
}

function client(){
    
    const net = require('net');
    var input = document.getElementById("myName").value;

    const client = net.createConnection({ port: server_port, host: server_addr }, () => {
        // 'connect' listener.
        console.log('connected to server!');
        // send the message
        client.write(`${input}\r\n`);
    });
    
    // get the data from the server
    client.on('data', (data) => {
        document.getElementById("greet_from_server").innerHTML = data;
        console.log(data.toString());
        client.end();
        client.destroy();
    });

    client.on('end', () => {
        console.log('disconnected from server');
    });


}

// update data for every 50ms
function update_data(){
    setInterval(function(){
        // get image from python server
        client();
    }, 50);
}

document.getElementById('forwardBtn').addEventListener('click', () => send_data('w'));
document.getElementById('backwardBtn').addEventListener('click', () => send_data('s'));
document.getElementById('leftBtn').addEventListener('click', () => send_data('a'));
document.getElementById('rightBtn').addEventListener('click', () => send_data('d'));
document.getElementById('stopBtn').addEventListener('click', () => send_data('q'));

function send_data(command) {
    const net = require('net');
    const client = net.createConnection({ port: server_port, host: server_addr }, () => {
        console.log('Connected to server!');
        client.write(command);
    });

    client.on('data', (data) => {
        console.log('Received:', data.toString());
        client.end();
    });

    client.on('end', () => {
        console.log('Disconnected from server');
    });
}
