const chatContainer = document.getElementById("chat-container");
const input = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");

function addMessage(text, sender){

    const div = document.createElement("div");

    div.classList.add("message");
    div.classList.add(sender);

    div.innerText = text;

    chatContainer.appendChild(div);

    chatContainer.scrollTop = chatContainer.scrollHeight;
}

async function sendMessage(){

    const message = input.value.trim();

    if(!message) return;

    addMessage(message,"user");

    input.value = "";

    // Temporary response
    setTimeout(()=>{

        addMessage(
            "Backend connection will come in the next step.",
            "bot"
        );

    },500);
}

sendBtn.addEventListener("click",sendMessage);

input.addEventListener("keydown",(e)=>{

    if(e.key==="Enter" && !e.shiftKey){

        e.preventDefault();

        sendMessage();

    }

});