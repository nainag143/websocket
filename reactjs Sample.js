const agentId = '123';
const socket = new WebSocket(`ws://${window.location.host}/ws/chat/${agentId}/`);

socket.onmessage = function(e) {
    const data = JSON.parse(e.data);
    console.log("Received:", data);
};

socket.onopen = function() {
    console.log("WebSocket connected");
    // Example sending a message
    socket.send(JSON.stringify({
        user_id: 1,
        contact_id: 5,
        message_type: "out",
        message: "Hello from agent!",
        attachment: null
    }));
};
