/* MRD Assistant — premium frontend logic */

const API_BASE = "http://127.0.0.1:8000";

const chatContainer = document.getElementById("chat-container");
const hero = document.getElementById("hero");
const input = document.getElementById("message-input");
const sendBtn = document.getElementById("send-btn");
const composer = document.getElementById("composer");
const statusPill = document.getElementById("status-pill");
const statusDot = document.getElementById("status-dot");
const statusText = document.getElementById("status-text");

let isLoading = false;

/* ---------------- Markdown-lite renderer ---------------- */

function escapeHtml(text) {
    return text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
}

function renderMarkdown(raw) {
    const escaped = escapeHtml(raw);

    // Fenced code blocks first.
    const blocks = [];
    let html = escaped.replace(
        /```(\w*)\n?([\s\S]*?)```/g,
        (m, lang, code) => {
            blocks.push(code.replace(/\n$/, ""));
            return `\u0000BLOCK${blocks.length - 1}\u0000`;
        }
    );

    // Inline code, bold, italics.
    html = html.replace(/`([^`\n]+)`/g, "<code>$1</code>");
    html = html.replace(/\*\*([^*\n]+)\*\*/g, "<strong>$1</strong>");
    html = html.replace(/(^|\s)\*([^*\n]+)\*(?=[\s.,!?)]|$)/g, "$1<em>$2</em>");

    // Bullet lists and paragraphs, line by line.
    const lines = html.split("\n");
    let out = "";
    let inList = false;

    for (const line of lines) {
        const bullet = line.match(/^\s*[-*•]\s+(.*)$/);

        if (bullet) {
            if (!inList) {
                out += "<ul>";
                inList = true;
            }
            out += `<li>${bullet[1]}</li>`;
            continue;
        }

        if (inList) {
            out += "</ul>";
            inList = false;
        }

        if (line.trim() === "") continue;

        if (line.startsWith("\u0000BLOCK")) {
            out += line;
            continue;
        }

        out += `<p>${line}</p>`;
    }

    if (inList) out += "</ul>";

    // Restore code blocks.
    html = out.replace(
        /\u0000BLOCK(\d+)\u0000/g,
        (m, i) => `<pre><code>${blocks[Number(i)]}</code></pre>`
    );

    return html;
}

/* ---------------- Chat UI ---------------- */

function timestamp() {
    return new Date().toLocaleTimeString([], {
        hour: "2-digit",
        minute: "2-digit"
    });
}

function scrollToBottom() {
    chatContainer.scrollTo({
        top: chatContainer.scrollHeight,
        behavior: "smooth"
    });
}

function addMessage(text, sender, sources) {
    const el = document.createElement("div");
    el.className = `message ${sender}`;

    if (sender === "user") {
        el.textContent = text;
    } else {
        el.innerHTML = renderMarkdown(text);
    }

    const time = document.createElement("span");
    time.className = "time";
    time.textContent = timestamp();
    el.appendChild(time);

    if (sender === "bot" && text && !el.classList.contains("error")) {
        const actions = document.createElement("div");
        actions.className = "msg-actions";

        const copyBtn = document.createElement("button");
        copyBtn.type = "button";
        copyBtn.className = "copy-btn";
        copyBtn.textContent = "Copy";
        copyBtn.dataset.raw = text;
        actions.appendChild(copyBtn);
        el.appendChild(actions);
    }

    const sourceMeta = addSourceBadges(el, sources);
    if (sourceMeta) el.appendChild(sourceMeta);

    chatContainer.appendChild(el);
    scrollToBottom();
    return el;
}

const SOURCE_ICONS = {
    github: "📦",
    resume: "📄",
    linkedin: "💼",
    contributions: "🌿",
};

function addSourceBadges(messageEl, sources) {
    if (!Array.isArray(sources) || sources.length === 0) return null;

    const wrap = document.createElement("div");
    wrap.className = "sources";

    for (const s of sources.slice(0, 4)) {
        const badge = document.createElement("span");
        badge.className = "source-badge";
        const icon = SOURCE_ICONS[s.source] || "🔗";
        const label = s.label ? escapeHtml(s.label) : s.source;
        const score =
            typeof s.score === "number" && s.score > 0
                ? ` <span class="score">${s.score.toFixed(2)}</span>`
                : "";
        badge.innerHTML = `${icon} ${label}${score}`;
        wrap.appendChild(badge);
    }

    return wrap;
}

function addTypingIndicator() {
    const el = document.createElement("div");
    el.className = "message bot typing";
    el.innerHTML = "<span></span><span></span><span></span>";
    chatContainer.appendChild(el);
    scrollToBottom();
    return el;
}

async function sendMessage() {

    const message = input.value.trim();

    if (!message || isLoading) return;

    isLoading = true;
    hero.classList.add("hidden");

    addMessage(message, "user");

    input.value = "";
    autoResize();
    updateSendState();

    const typingBubble = addTypingIndicator();

    try {

        const response = await fetch(`${API_BASE}/chat`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message })
        });

        typingBubble.remove();

        if (!response.ok) {
            throw new Error(`Server error ${response.status}`);
        }

        const data = await response.json();

        addMessage(
            data.response || "No response generated.",
            "bot",
            data.sources
        );

    } catch (error) {

        typingBubble.remove();

        addMessage(
            "I can't reach the server right now. Make sure the backend is running:\n`uvicorn backend.app:app --port 8000`",
            "bot"
        );

        setStatus(false);
        console.error(error);
    }

    isLoading = false;
    updateSendState();
    input.focus();
}

/* ---------------- Composer ---------------- */

function autoResize() {
    input.style.height = "auto";
    input.style.height = Math.min(input.scrollHeight, 150) + "px";
}

function updateSendState() {
    sendBtn.disabled = isLoading || input.value.trim().length === 0;
}

composer.addEventListener("submit", (e) => {
    e.preventDefault();
    sendMessage();
});

input.addEventListener("input", () => {
    autoResize();
    updateSendState();
});

// "/" focuses the composer from anywhere.
document.addEventListener("keydown", (e) => {
    if (e.key === "/" && document.activeElement !== input) {
        e.preventDefault();
        input.focus();
    }
});

/* Suggestion chips */
document.querySelectorAll(".chip").forEach((chip) => {
    chip.addEventListener("click", () => {
        input.value = chip.textContent.replace(/^[^\w]+\s*/, "").trim();
        updateSendState();
        sendMessage();
    });
});

/* Copy buttons (event delegation) */
chatContainer.addEventListener("click", async (e) => {
    const btn = e.target.closest(".copy-btn");
    if (!btn) return;

    try {
        await navigator.clipboard.writeText(btn.dataset.raw || "");
        btn.textContent = "Copied!";
        btn.classList.add("copied");
        setTimeout(() => {
            btn.textContent = "Copy";
            btn.classList.remove("copied");
        }, 1600);
    } catch {
        btn.textContent = "Failed";
        setTimeout(() => (btn.textContent = "Copy"), 1600);
    }
});

/* ---------------- Health check ---------------- */

function setStatus(online) {
    statusPill.classList.toggle("online", online);
    statusPill.classList.toggle("offline", !online);
    statusText.textContent = online ? "Online" : "Offline";
}

async function healthCheck() {
    try {
        const res = await fetch(`${API_BASE}/`, { signal: AbortSignal.timeout(4000) });
        setStatus(res.ok);
    } catch {
        setStatus(false);
    }
}

healthCheck();
setInterval(healthCheck, 20000);

/* ---------------- Greeting ---------------- */

addMessage(
    "Hi! I'm MRD Assistant — ask me anything about Manas' projects, experience, skills or open-source work.",
    "bot"
);

autoResize();
updateSendState();
