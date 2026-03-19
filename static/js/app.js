
async function ingestRepo() {
    const urlInput = document.getElementById("repoUrl");
    const statusDiv = document.getElementById("repoStatus");
    const ingestBtn = document.getElementById("ingestBtn");
    const btnText = ingestBtn.querySelector(".btn-text");
    const btnLoader = ingestBtn.querySelector(".btn-loader");
    const githubUrl = urlInput.value.trim();

    if (!githubUrl) {
        statusDiv.textContent = "Please enter a GitHub repository URL.";
        statusDiv.style.color = "#fbbf24";
        return;
    }

    ingestBtn.disabled = true;
    btnText.style.display = "none";
    btnLoader.style.display = "inline";
    statusDiv.textContent = "Cloning repository and creating embeddings... This may take 1-3 minutes.";
    statusDiv.style.color = "#94a3b8";

    try {
        const formData = new FormData();
        formData.append("msg", githubUrl);
        const response = await fetch("/chatbot", { method: "POST", body: formData });
        const data = await response.json();
        statusDiv.textContent = data.response;
        statusDiv.style.color = data.response.includes("successfully") ? "#4ade80" : "#f87171";
        if (data.response.includes("successfully")) {
            addMessage("bot", data.response);
        }
    } catch (error) {
        statusDiv.textContent = "Network error. Please check your connection.";
        statusDiv.style.color = "#f87171";
    } finally {
        ingestBtn.disabled = false;
        btnText.style.display = "inline";
        btnLoader.style.display = "none";
    }
}

async function sendQuestion() {
    const questionInput = document.getElementById("userQuestion");
    const sendBtn = document.getElementById("sendBtn");
    const question = questionInput.value.trim();
    if (!question) return;

    addMessage("user", question);
    questionInput.value = "";
    const typingId = showTypingIndicator();
    sendBtn.disabled = true;
    questionInput.disabled = true;

    try {
        const response = await fetch("/get?msg=" + encodeURIComponent(question));
        const data = await response.json();
        removeTypingIndicator(typingId);
        addMessage("bot", data.response);
    } catch (error) {
        removeTypingIndicator(typingId);
        addMessage("bot", "Network error. Please try again.");
    } finally {
        sendBtn.disabled = false;
        questionInput.disabled = false;
        questionInput.focus();
    }
}

function handleKeyPress(event) {
    if (event.key === "Enter") sendQuestion();
}

function addMessage(sender, text) {
    const chatBox = document.getElementById("chatBox");
    const messageDiv = document.createElement("div");
    messageDiv.className = "message " + (sender === "user" ? "user-message" : "bot-message");

    const avatar = document.createElement("div");
    avatar.className = "message-avatar";
    avatar.innerHTML = sender === "user" ? "&#128100;" : "&#129302;";

    const content = document.createElement("div");
    content.className = "message-content";
    content.innerHTML = formatMessage(text);

    messageDiv.appendChild(avatar);
    messageDiv.appendChild(content);
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

function formatMessage(text) {
    let f = text
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;");
    f = f.replace(/\`\`\`([\s\S]*?)\`\`\`/g, "<pre>`$1`</pre>");
    f = f.replace(/\`([^\`]+)\`/g, "<code>`$1`</code>");
    f = f.replace(/\*\*([^*]+)\*\*/g, "<strong>`$1`</strong>");
    f = f.replace(/\n/g, "<br>");
    return "<p>" + f + "</p>";
}

let typingCounter = 0;

function showTypingIndicator() {
    const chatBox = document.getElementById("chatBox");
    const id = "typing-" + (++typingCounter);
    const messageDiv = document.createElement("div");
    messageDiv.className = "message bot-message";
    messageDiv.id = id;
    messageDiv.innerHTML = '<div class="message-avatar">&#129302;</div><div class="message-content"><div class="typing-indicator"><span></span><span></span><span></span></div></div>';
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
    return id;
}

function removeTypingIndicator(id) {
    const el = document.getElementById(id);
    if (el) el.remove();
}
