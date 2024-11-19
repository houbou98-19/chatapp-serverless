async function fetchMessages() {
    try {
        const match = window.location.pathname.match(/\/(Prod|Stage)/);
        const envPath = match ? match[0] : ""; 
        //console.log(envPath);
        const response = await fetch(`${envPath}/messages`);
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }
        
        const messages = await response.json();
        const messageContainer = document.getElementById("messages");
        messageContainer.innerHTML = "";
        
        if (messages.length === 0) {
            messageContainer.textContent = "No messages to display.";
        } else {
            messages.forEach(msg => {
                const msgElement = document.createElement("div");
                msgElement.className = "message";
                msgElement.textContent = `${msg.username}: ${msg.messagecontent}`;
                messageContainer.appendChild(msgElement);
            });
        }
    } catch (error) {
        console.error("Error fetching messages:", error);
        document.getElementById("messages").textContent = "Failed to load messages.";
    }
}

async function postMessage(event) {
    event.preventDefault(); 

    const match = window.location.pathname.match(/\/(Prod|Stage)/);
    const envPath = match ? match[0] : ""; 
    const username = document.getElementById("username").value;
    const messageContent = document.getElementById("message").value;
    document.getElementById("message").value = "";

    await fetch(envPath+"/messages", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, content: messageContent }),
    });

    fetchMessages();
}


document.getElementById('message-form').addEventListener('submit', postMessage);
document.addEventListener("DOMContentLoaded", () => {
    fetchMessages(); // Fetch messages when the page loads
    setInterval(fetchMessages, 5000); // Fetch messages every 5 seconds
});