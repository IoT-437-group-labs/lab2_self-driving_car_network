const net = require('net');

var server_port = 65432;
var server_addr = "192.168.68.110";   // the IP address of your Raspberry PI

document.onkeydown = updateKey;
document.onkeyup = resetKey;

let client;
let invertTurns = false; // Default inversion state
let isTyping = false;    // Flag to indicate if the user is typing

// Establish the TCP connection once and reuse it
function connectToServer() {
    client = net.createConnection({ port: server_port, host: server_addr }, () => {
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
            console.error('Error parsing server response:', e);
            document.getElementById("bluetooth").innerHTML = "Error: " + e.message;
        }
    });

    client.on('end', () => {
        console.log('Disconnected from server');
        document.getElementById("status").textContent = "Disconnected";
        document.getElementById("status").style.color = "red";
    });

    client.on('error', (err) => {
        console.error('Connection error:', err);
        document.getElementById("bluetooth").innerHTML = "Connection error: " + err.message;
        document.getElementById("status").textContent = "Error";
        document.getElementById("status").style.color = "red";
    });
}

// Send commands to the server through the established connection
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
    document.getElementById("direction").textContent = data.direction || "Unknown";
    document.getElementById("speed").textContent = data.speed || "0.0";
    document.getElementById("distance").textContent = data.distance || "0.0";
    document.getElementById("temperature").textContent = data.temperature || "0.0";
    document.getElementById("battery").textContent = data.battery || "N/A"; // New Battery Field
    document.getElementById("bluetooth").innerHTML = JSON.stringify(data, null, 2);
}

function updateKey(e) {
    e = e || window.event;

    // If user is typing, do not send commands
    if (isTyping) return;

    if (e.keyCode == '87') {
        // up (w)
        document.getElementById("upArrow").style.color = "green";
        send_command("w");
    }
    else if (e.keyCode == '83') {
        // down (s)
        document.getElementById("downArrow").style.color = "green";
        send_command("s");
    }
    else if (e.keyCode == '65') {
        // left (a)
        document.getElementById("leftArrow").style.color = "green";
        // Invert left/right based on checkbox state
        if (invertTurns) {
            send_command("d"); // Inverted
        } else {
            send_command("a");
        }
    }
    else if (e.keyCode == '68') {
        // right (d)
        document.getElementById("rightArrow").style.color = "green";
        // Invert left/right based on checkbox state
        if (invertTurns) {
            send_command("a"); // Inverted
        } else {
            send_command("d");
        }
    }
    // if the key is i, then toggle inversion of the directions
    else if (e.keyCode == '73') {
        invertTurns = !invertTurns;
        document.getElementById("invertTurnsCheckbox").checked = invertTurns;
        send_command("i"); // Inform server to toggle inversion
    }
}

function resetKey(e) {
    e = e || window.event;

    document.getElementById("upArrow").style.color = "grey";
    document.getElementById("downArrow").style.color = "grey";
    document.getElementById("leftArrow").style.color = "grey";
    document.getElementById("rightArrow").style.color = "grey";

    send_command("q");  // Send stop command when key is released
}

function update_data() {
    send_command("STATUS");
}

function sendMessage() {
    const message = document.getElementById('message').value;
    send_command(message);
}

// Handle checkbox toggle
document.getElementById("invertTurnsCheckbox").addEventListener('change', function() {
    invertTurns = this.checked;
    send_command("i"); // Inform server to toggle inversion
});

// Handle focus and blur events on the message input
const messageInput = document.getElementById("message");
messageInput.addEventListener('focus', () => {
    isTyping = true;
});

messageInput.addEventListener('blur', () => {
    isTyping = false;
});

// Connect to server once when page loads
connectToServer();

// Update status every 5 seconds
setInterval(update_data, 5000);

// Initial connection attempt
update_data();

// Gracefully close the connection when the window is closed
window.addEventListener('beforeunload', () => {
    if (client && !client.destroyed) {
        client.end();
    }
});
