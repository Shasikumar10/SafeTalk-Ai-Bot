let recorder;
let mediaStream;
let isRecording = false;
let greeted = false;
let abortCurrentAction = false;

// Audio analysis for silence detection
let audioContext;
let analyser;
let silenceStart = null;
let recordStartTime = null;

const SILENCE_THRESHOLD = 0.015;
const SILENCE_DURATION = 2500;
const MIN_RECORD_TIME = 2500;

const recordBtn = document.getElementById("recordBtn");
const btnText = document.getElementById("btnText");
const statusText = document.getElementById("status");
const resultCard = document.getElementById("resultCard");
const transcriptText = document.getElementById("transcriptText");
const answerText = document.getElementById("answerText");
const langTag = document.getElementById("langTag");
const orb = document.getElementById("orb");
const waveform = document.getElementById("waveform");
const stopBtn = document.getElementById("stopBtn");

/* ---------- HARD-CODED GREETINGS ---------- */
const GREETING_KEYWORDS = ["hi", "hello", "hey", "good morning", "good evening"];

function detectGreeting(text) {
    if (!text) return false;
    const lowerText = text.toLowerCase();
    return GREETING_KEYWORDS.some(word => lowerText.includes(word));
}

function speakGreeting() {
    const utter = new SpeechSynthesisUtterance("Hello! I am SafeTalk AI. How can I help you today?");
    utter.lang = "en-IN";
    utter.rate = 1;
    utter.pitch = 1;

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utter);
    
    stopBtn.disabled = false;
    utter.onend = () => {
        stopBtn.disabled = true;
    }
}

/* ---------- Speak answer ---------- */
function speak(text, lang) {
    console.log(`Speaking in ${lang}: ${text}`);
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang =
        lang === "te" ? "te-IN" :
        lang === "hi" ? "hi-IN" :
        "en-IN";

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utter);
    
    stopBtn.disabled = false;
    
    utter.onend = () => {
        stopBtn.disabled = true;
    }
}

/* ---------- Monitor silence ---------- */
function monitorSilence() {
    if (!isRecording) return;

    const buffer = new Uint8Array(analyser.fftSize);
    analyser.getByteTimeDomainData(buffer);

    let sum = 0;
    for (let i = 0; i < buffer.length; i++) {
        const v = (buffer[i] - 128) / 128;
        sum += v * v;
    }
    const rms = Math.sqrt(sum / buffer.length);

    if (rms < SILENCE_THRESHOLD) {
        if (!silenceStart) silenceStart = Date.now();

        if (
            Date.now() - silenceStart > SILENCE_DURATION &&
            Date.now() - recordStartTime > MIN_RECORD_TIME
        ) {
            stopRecording();
            return;
        }
    } else {
        silenceStart = null;
    }

    requestAnimationFrame(monitorSilence);
}

/* ---------- Start recording ---------- */
async function startRecording() {
    try {
        isRecording = true;
        greeted = false;
        abortCurrentAction = false;
        silenceStart = null;
        recordStartTime = Date.now();

        // UI Updates
        recordBtn.classList.add("recording");
        orb.classList.add("recording");
        waveform.classList.remove("hidden");
        btnText.innerText = "Stop Recording";
        statusText.innerText = "Listening...";
        resultCard.classList.add("hidden");
        stopBtn.disabled = false;

        mediaStream = await navigator.mediaDevices.getUserMedia({ audio: true });

        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 2048;

        const source = audioContext.createMediaStreamSource(mediaStream);
        source.connect(analyser);

        recorder = new MediaRecorder(mediaStream);
        const chunks = [];

        recorder.ondataavailable = e => chunks.push(e.data);

        recorder.onstop = async () => {
            // UI Updates
            waveform.classList.add("hidden");
            recordBtn.classList.remove("recording");
            orb.classList.remove("recording");
            btnText.innerText = "Start Recording";
            statusText.innerText = "Processing...";

            // Cleanup
            mediaStream.getTracks().forEach(t => t.stop());
            if (audioContext.state !== 'closed') {
                audioContext.close();
            }

            if (chunks.length === 0) {
                statusText.innerText = "No audio recorded.";
                return;
            }

            if (abortCurrentAction) {
                console.log("Action aborted, skipping backend fetch.");
                return;
            }

            const blob = new Blob(chunks, { type: "audio/wav" });
            const formData = new FormData();
            formData.append("file", blob);

            try {
                const res = await fetch("http://127.0.0.1:8000/process-audio", {
                    method: "POST",
                    body: formData
                });

                if (!res.ok) throw new Error("Backend server error");

                const data = await res.json();
                console.log("Backend response:", data);

                // ✅ GREETING DETECTION (Now working thanks to backend fix)
                if (!greeted && detectGreeting(data.text)) {
                    greeted = true;
                    speakGreeting();
                    statusText.innerText = "👋 Greeting detected";
                    return;
                }

                // Show Result
                transcriptText.innerText = data.text || "—";
                answerText.innerText = data.answer || "I'm not sure how to respond to that.";
                langTag.innerText = data.language ? data.language.toUpperCase() : "EN";
                
                resultCard.classList.remove("hidden");
                statusText.innerText = "Ready to listen";

                if (data.answer) {
                    speak(data.answer, data.language);
                } else {
                    stopBtn.disabled = true;
                }

            } catch (err) {
                console.error("Fetch error:", err);
                statusText.innerText = "⚠️ Error connecting to backend";
                stopBtn.disabled = true;
            } finally {
                isRecording = false;
            }
        };

        recorder.start();
        monitorSilence();
    } catch (err) {
        console.error("Critical error:", err);
        statusText.innerText = "⚠️ Microphone access denied";
        isRecording = false;
    }
}

/* ---------- Stop recording ---------- */
function stopRecording() {
    if (!isRecording) return;
    isRecording = false;
    if (recorder && recorder.state !== "inactive") {
        recorder.stop();
    }
}

/* ---------- Button Interaction ---------- */
recordBtn.onclick = () => {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
};

/* ---------- Stop Entire Conversation ---------- */
stopBtn.onclick = () => {
    console.log("Stopping conversation...");
    abortCurrentAction = true;
    
    // 1. Stop recording if in progress
    if (isRecording) {
        stopRecording();
    }
    
    // 2. Cancel Speech Synthesis
    window.speechSynthesis.cancel();
    
    // 3. Reset UI
    stopBtn.disabled = true;
    statusText.innerText = "Stopped.";
    orb.classList.remove("recording");
    waveform.classList.add("hidden");
    btnText.innerText = "Start Recording";
};
