const chatContainer = document.getElementById("chat-container");
const input = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");

const API_URL = "http://127.0.0.1:8000/chat";

let isLoading = false;

function addMessage(text, sender) {

    const div = document.createElement("div");

    div.className = `message ${sender}`;

    div.textContent = text;

    chatContainer.appendChild(div);

    scrollToBottom();

    return div;
}

function addTypingIndicator() {

    const div = document.createElement("div");

    div.className = "message bot typing";

    div.innerHTML = `
        <span></span>
        <span></span>
        <span></span>
    `;

    chatContainer.appendChild(div);

    scrollToBottom();

    return div;
}

function scrollToBottom() {

    chatContainer.scrollTo({
        top: chatContainer.scrollHeight,
        behavior: "smooth"
    });

}

async function sendMessage() {

    const message = input.value.trim();

    if (!message || isLoading) return;

    isLoading = true;

    addMessage(message, "user");

    input.value = "";
    input.style.height = "auto";

    sendBtn.disabled = true;

    const typingBubble = addTypingIndicator();

    try {

        const response = await fetch(
            API_URL,
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

        if (!response.ok) {
            throw new Error(`Server error: ${response.status}`);
        }

        const data = await response.json();

        typingBubble.remove();

        addMessage(data.response, "bot");

    }
    catch (error) {

        typingBubble.remove();

        addMessage(
            "Unable to connect to MRD Assistant.",
            "bot"
        );

        console.error(error);

    }

    isLoading = false;

    sendBtn.disabled = false;

}

document.querySelectorAll(".suggestion-card").forEach((card) => {

    card.addEventListener("click", () => {

        input.value = card.textContent.trim();

        sendMessage();

    });

});

sendBtn.addEventListener("click", sendMessage);

input.addEventListener("keydown", (e) => {

    if (e.key === "Enter" && !e.shiftKey) {

        e.preventDefault();

        sendMessage();

    }

});


input.addEventListener("input", () => {

    input.style.height = "auto";

    input.style.height = input.scrollHeight + "px";

});