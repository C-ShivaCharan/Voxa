const commandInput = document.getElementById("commandInput");
const responseDiv = document.getElementById("response");
const micBtn = document.getElementById("micBtn");

// ----------------- Send Command -----------------
async function sendCommand(command) {
    if (!command) return;
    try {
        const res = await fetch("/command", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({command})
        });
        const data = await res.json();

        if (data.type === "url" && data.url) {
            responseDiv.innerText = data.message || "Opening website...";
            window.open(data.url, "_blank");
            speakResponse(data.message || "Opening website");
        } else {
            responseDiv.innerText = data.message;
            speakResponse(data.message);
        }
        responseDiv.scrollTop = responseDiv.scrollHeight;
    } catch (err) {
        responseDiv.innerText = "Error processing command.";
        console.error(err);
    }
}

// Enter key support
commandInput.addEventListener("keypress", (e) => {
    if (e.key === "Enter") sendCommand(commandInput.value.trim());
});

// ----------------- Voice Recognition -----------------
let recognition;
if ('webkitSpeechRecognition' in window) {
    recognition = new webkitSpeechRecognition();
    recognition.continuous = false;
    recognition.interimResults = false;
    recognition.lang = 'en-US';

    recognition.onstart = () => {
        micBtn.classList.add("listening");
    };

    recognition.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        commandInput.value = transcript;
        sendCommand(transcript);
    };

    recognition.onerror = () => {
        micBtn.classList.remove("listening");
    };

    recognition.onend = () => {
        micBtn.classList.remove("listening");
    };
} else {
    micBtn.disabled = true;
}

// ----------------- Mic Button -----------------
micBtn.addEventListener("click", () => {
    if (recognition) recognition.start();
});

// ----------------- Speech Synthesis -----------------
function speakResponse(text) {
    if ('speechSynthesis' in window) {
        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = 'en-US';
        utterance.rate = 1;
        utterance.pitch = 1;
        window.speechSynthesis.speak(utterance);
    }
}
