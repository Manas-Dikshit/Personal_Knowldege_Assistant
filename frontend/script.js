const chatContainer = document.getElementById("chat-container");
const input = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");

function addMessage(text, sender) {
    const div = document.createElement("div");

    div.classList.add("message");
    div.classList.add(sender);

    div.innerText = text;

    chatContainer.appendChild(div);

    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function sendMessage() {

    const message = input.value.trim();

    if (!message) return;

    // Show user message
    addMessage(message, "user");

    input.value = "";

    // Show thinking message
    addMessage("Thinking...", "bot");

    try {

        const response = await fetch(
            "http://127.0.0.1:8000/chat",
            {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    message: message
                })
            }
        );

        const data = await response.json();

        // Remove "Thinking..."
        chatContainer.lastChild.remove();

        // Show AI response
        addMessage(data.response, "bot");

    }
    catch (error) {

        console.error(error);

        chatContainer.lastChild.remove();

        addMessage(
            "Unable to connect to MRD AI backend.",
            "bot"
        );
    }
}

sendBtn.addEventListener("click", sendMessage);

input.addEventListener("keydown", (e) => {

    if (e.key === "Enter" && !e.shiftKey) {

        e.preventDefault();

        sendMessage();

    }

});