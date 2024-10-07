const net = require('net');

const TCP_PORT = 65432;
const TCP_HOST = "192.168.68.110";

document.onkeydown = updateKey;
document.onkeyup = resetKey;

let client;
let isTyping = false;
let invertTurns = false;

function connectToServer() {
    client = net.createConnection({ port: TCP_PORT, host: TCP_HOST }, () => {
        console.log('Connected to server!');
        document.getElementById("status").textContent = "Connected";
        document.getElementById("status").style.color = "green";
    });

    client.on('data', (data) => {
        console.log('Received from server:', data.toString());
        try {
            const response = JSON.parse(data.toString());
            updateUI(response);
        } catch (e) {
            console.error('Error parsing JSON response:', e);
        }
    });

    client.on('end', () => {
        console.log('Disconnected from server');
        document.getElementById("status").textContent = "Disconnected";
        document.getElementById("status").style.color = "red";
    });

    client.on('error', (err) => {
        console.error('Connection error:', err);
        document.getElementById("status").textContent = "Error";
        document.getElementById("status").style.color = "red";
    });
}


function send_command(command) {
    if (isTyping) {
        console.log('Typing in progress. Command not sent:', command);
        return;
    }
    if (client && !client.destroyed) {
        client.write(`${command}\r\n`);
    } else {
        console.error('Client not connected');
        document.getElementById("status").textContent = "Not connected";
        document.getElementById("status").style.color = "orange";
    }
}

function updateUI(data) {
    if (data.cpu_temperature !== undefined) {
        document.getElementById("cpu_temperature").textContent = data.cpu_temperature + "°C";
    }
    if (data.cpu_usage !== undefined) {
        document.getElementById("cpu_usage").textContent = data.cpu_usage + "%";
    }
    if (data.battery !== undefined) {
        const batteryOcc = parseFloat(data.battery);
        const batteryAll = 8.4;
        document.getElementById("battery").textContent = `${batteryOcc}V/${batteryAll}V`;
    } else {
        document.getElementById("battery").textContent = "N/A";
    }
}

function updateKey(e) {
    e = e || window.event;

    if (isTyping) return;

    if (e.keyCode == '87') {
        document.getElementById("upArrow").style.color = "green";
        send_command("w");
    }
    else if (e.keyCode == '83') {
        document.getElementById("downArrow").style.color = "green";
        send_command("s");
    }
    else if (e.keyCode == '65') {
        document.getElementById("leftArrow").style.color = "green";
        send_command("a");
    }
    else if (e.keyCode == '68') {
        document.getElementById("rightArrow").style.color = "green";
        send_command("d");
    }
    else if (e.keyCode == '73') {
        toggleInvertTurns();
    }
}

function resetKey(e) {
    e = e || window.event;

    document.getElementById("upArrow").style.color = "grey";
    document.getElementById("downArrow").style.color = "grey";
    document.getElementById("leftArrow").style.color = "grey";
    document.getElementById("rightArrow").style.color = "grey";

    send_command("q");
}

function update_data() {
    send_command("STATUS");
}

function sendMessage() {
    const message = document.getElementById('message').value;
    send_command(message);
}


document.getElementById("invertTurnsCheckbox").addEventListener('change', function () {
    invertTurns = this.checked;
    send_command("i");
});


function toggleInvertTurns() {
    const checkbox = document.getElementById("invertTurnsCheckbox");
    checkbox.checked = !checkbox.checked;
    invertTurns = checkbox.checked;
    send_command("i");
}


const messageInput = document.getElementById("message");
messageInput.addEventListener('focus', () => {
    isTyping = true;
});

messageInput.addEventListener('blur', () => {
    isTyping = false;
});


connectToServer();


setInterval(update_data, 5000);


update_data();


window.addEventListener('beforeunload', () => {
    if (client && !client.destroyed) {
        client.end();
    }
});


document.getElementById("invertTurnsCheckbox").checked = invertTurns;
