const recordBtn = document.getElementById("recordBtn");
const statusText = document.getElementById("status");
const resultBox = document.getElementById("resultBox");
const answerText = document.getElementById("answerText");
const modeTag = document.getElementById("modeTag");
const confidenceTag = document.getElementById("confidenceTag");
const sourcesList = document.getElementById("sourcesList");
const speakBtn = document.getElementById("speakBtn");

let recognition;
let finalAnswer = "";

if (!("webkitSpeechRecognition" in window)) {
  alert("Speech Recognition not supported. Use Chrome.");
} else {
  recognition = new webkitSpeechRecognition();
  recognition.lang = "en-US";
  recognition.continuous = false;
  recognition.interimResults = false;
}

recordBtn.onclick = () => {
  resultBox.classList.add("hidden");
  statusText.textContent = "🎧 Listening...";
  recordBtn.disabled = true;

  try {
    recognition.start();
  } catch (e) {
    console.error("Recognition start error:", e);
  }
};

// 🔹 RESULT HANDLER
recognition.onresult = async (event) => {
  const transcript = event.results[0][0].transcript.trim();
  console.log("🎤 Transcript:", transcript);

  if (!transcript) {
    statusText.textContent = "❌ No speech detected";
    recordBtn.disabled = false;
    return;
  }

  statusText.textContent = "🧠 Processing...";

  try {
    const res = await fetch("http://127.0.0.1:8000/process-text", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text: transcript })
    });

    const data = await res.json();
    console.log("📦 Backend response:", data);

    finalAnswer =
      data.answer ||
      data.response?.message ||
      "No response";

    answerText.textContent = finalAnswer;
    modeTag.textContent = data.mode ? data.mode.toUpperCase() : "STANDARD";
    confidenceTag.textContent =
      data.confidence ? `Confidence: ${data.confidence}` : "";

    sourcesList.innerHTML = "";
    (data.sources || []).forEach(src => {
      const li = document.createElement("li");
      li.textContent = src.substring(0, 140) + "...";
      sourcesList.appendChild(li);
    });

    resultBox.classList.remove("hidden");
    statusText.textContent = "✅ Done";
  } catch (err) {
    console.error("❌ Fetch error:", err);
    statusText.textContent = "❌ Backend error";
  } finally {
    recordBtn.disabled = false;
  }
};

// 🔹 IMPORTANT: handle end
recognition.onend = () => {
  console.log("🎙️ Recognition ended");
  recordBtn.disabled = false;
};

// 🔹 ERROR HANDLER
recognition.onerror = (event) => {
  console.error("❌ Speech error:", event.error);
  statusText.textContent = `❌ ${event.error}`;
  recordBtn.disabled = false;
};

speakBtn.onclick = () => {
  if (!finalAnswer) return;
  const utterance = new SpeechSynthesisUtterance(finalAnswer);
  speechSynthesis.speak(utterance);
};
