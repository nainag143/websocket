const socket = new WebSocket('ws://1msg.1point1.in:3003/');

// On connection open
socket.addEventListener('open', function (event) {
    console.log('Connected to WebSocket server');

    // Send INIT message
    const initMessage = {
        type: "init",
        agent_id: "1"
    };
    socket.send(JSON.stringify(initMessage));
    console.log('Sent init message:', initMessage);

    // Send MESSAGE after short delay
    setTimeout(() => {
        const chatMessage = {
            type: "message",
            user_id: "6",
            agent_id: "1",
            message_type: "out",
            message: "Hello there!",
            contact_id: "1",
            attachment: null
        };
        socket.send(JSON.stringify(chatMessage));
        console.log('Sent chat message:', chatMessage);
    }, 1000); // Send after 1 second
});

// On message received
socket.addEventListener('message', function (event) {
    console.log('Received from server:', event.data);
});

// On error
socket.addEventListener('error', function (event) {
    console.error('WebSocket error:', event);
});

// On close
socket.addEventListener('close', function (event) {
    console.log('WebSocket connection closed:', event);
});
