const match = window.location.pathname.match(/\/(Prod|Stage)/);
const envPath = match ? match[0] : ""; 

async function fetchMessages() {
    try {
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

    const messageContent = document.getElementById("message").value;
    document.getElementById("message").value = "";

    try {
        const response = await fetch(`${envPath}/messages`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json", 
            },
            body: JSON.stringify({ content: messageContent }), 
        });

        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || "Failed to post the message");
        }
    } catch (error) {
        console.error("Error posting message:", error);
        alert("Failed to post the message. Please try again.");
    }
}

async function loginUser(event) {
    event.preventDefault();

    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    const response = await fetch(envPath + "/token", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({ username, password }),
    });

    if (response.ok) {
        //const data = await response.json();
        //localStorage.setItem("token", data.access_token);
        window.location.href = envPath + "/chat";
    } else {
        alert("Invalid username or password");
    }
}

async function logoutUser() {
    const response = await fetch(envPath + "/logout", {
        method: "POST"
    });
    if (response.ok) {
        window.location.href = envPath + "/login";
    } else {
        alert("Failed to log out.. thats crazy....");
    }
}

async function registerUser(event) {
    event.preventDefault();

    const username = document.getElementById("register-username").value;
    const password = document.getElementById("register-password").value;

    const response = await fetch(envPath + "/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/x-www-form-urlencoded",
        },
        body: new URLSearchParams({ username, password }),
    });

    if (response.ok) {
        alert("Registration successful! You can now log in.");
        document.getElementById("register-form").reset(); // Clear form
    } else {
        const error = await response.json();
        alert(`Registration failed: ${error.detail}`);
    }
}



document.addEventListener("DOMContentLoaded", () => {
    const messageForm = document.getElementById("message-form");
    if (messageForm) {
        messageForm.addEventListener("submit", postMessage);
        fetchMessages();
        setInterval(fetchMessages, 5000); // Refetch messages every 5 seconds
    }

    const loginForm = document.getElementById("login-form");
    if (loginForm) {
        loginForm.addEventListener("submit", loginUser);
    }

    const registerForm = document.getElementById("register-form");
    if (registerForm) {
        registerForm.addEventListener("submit", registerUser);
    }

    const logoutButton = document.getElementById("logout-btn");
    if (logoutButton) {
        logoutButton.addEventListener("click", logoutUser);
    }
});
