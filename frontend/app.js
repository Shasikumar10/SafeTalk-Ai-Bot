let recorder;
let mediaStream;
let isRecording = false;
let greeted = false;
let abortController = null;
let abortCurrentAction = false;

let audioContext;
let analyser;
let silenceStart = null;
let recordStartTime = null;
let smoothedRms = 0;

const SILENCE_THRESHOLD = 0.05;
const SILENCE_DURATION = 2000;
const INITIAL_WAIT_TIME = 5000;


const recordBtn = document.getElementById("recordBtn");
const btnText = document.getElementById("btnText");
const statusText = document.getElementById("status");
const resultCard = document.getElementById("resultCard");
const transcriptText = document.getElementById("transcriptText");
const answerText = document.getElementById("answerText");
const langTag = document.getElementById("langTag");
const orb = document.getElementById("orb");
const waveform = document.getElementById("waveform");



function speakGreeting() {
    const utter = new SpeechSynthesisUtterance("Hi, how can I help you?");
    utter.lang = "en-IN";
    utter.rate = 1;
    utter.pitch = 1;

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utter);

}

function speak(text, lang) {
    console.log(`Speaking in ${lang}: ${text}`);
    const utter = new SpeechSynthesisUtterance(text);
    utter.lang =
        lang === "te" ? "te-IN" :
            lang === "hi" ? "hi-IN" :
                "en-IN";

    window.speechSynthesis.cancel();
    window.speechSynthesis.speak(utter);

}

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
    smoothedRms = (smoothedRms * 0.8) + (rms * 0.2);

    let maxSilenceAllowed = SILENCE_DURATION;

    if (smoothedRms >= SILENCE_THRESHOLD) {
        if (!window.hasSpoken) window.hasSpoken = true;
        silenceStart = null;
    } else {
        if (!silenceStart) silenceStart = Date.now();
        maxSilenceAllowed = window.hasSpoken ? SILENCE_DURATION : INITIAL_WAIT_TIME;

        if (Date.now() - silenceStart > maxSilenceAllowed) {
            console.log("Silence detected, stopping recording. Final RMS:", smoothedRms.toFixed(4));
            stopRecording();
            return;
        }
    }


    requestAnimationFrame(monitorSilence);
}

async function startRecording() {
    try {
        isRecording = true;
        greeted = false;
        abortCurrentAction = false;
        abortController = new AbortController();
        silenceStart = null;
        recordStartTime = Date.now();
        smoothedRms = 0;
        window.hasSpoken = false;

        recordBtn.classList.add("recording");
        orb.classList.add("recording");
        waveform.classList.remove("hidden");
        btnText.innerText = "Stop Recording";
        statusText.innerText = "Listening...";
        resultCard.classList.add("hidden");

        speakGreeting();

        mediaStream = await navigator.mediaDevices.getUserMedia({
            audio: {
                channelCount: 1,
                sampleRate: 16000,
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true
            }
        });

        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        analyser = audioContext.createAnalyser();
        analyser.fftSize = 2048;

        const source = audioContext.createMediaStreamSource(mediaStream);
        source.connect(analyser);

        recorder = new MediaRecorder(mediaStream, {
            audioBitsPerSecond: 128000
        });
        const chunks = [];

        recorder.ondataavailable = e => chunks.push(e.data);

        recorder.onstop = async () => {
            waveform.classList.add("hidden");
            recordBtn.classList.remove("recording");
            orb.classList.remove("recording");
            btnText.innerText = "Start Recording";
            statusText.innerText = "Processing...";

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
                // Updated to Hugging Face Backend
                const res = await fetch("https://shasikumar10-safe-talk-ai.hf.space/process-audio", {
                    method: "POST",
                    body: formData,
                    signal: abortController.signal
                });

                if (!res.ok) throw new Error("Backend server error");
                if (abortCurrentAction) return;

                const data = await res.json();
                if (abortCurrentAction) return;
                console.log("Backend response:", data);



                transcriptText.innerText = data.text || "—";
                answerText.innerText = data.answer || "I'm not sure how to respond to that.";

                if (data.mode && data.mode.includes("greeting")) {
                    langTag.innerText = "⚡ FAST GREETING";
                    langTag.style.backgroundColor = "#10b981";
                } else {
                    langTag.innerText = data.language ? data.language.toUpperCase() : "EN";
                    langTag.style.backgroundColor = "var(--primary-blue)";
                }

                resultCard.classList.remove("hidden");
                statusText.innerText = "Ready to listen";

                if (data.answer) {
                    speak(data.answer, data.language);
                }

            } catch (err) {
                console.error("Fetch error:", err);
                statusText.innerText = "⚠️ Error connecting to backend";
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

function stopRecording() {
    if (!isRecording) return;
    isRecording = false;
    if (recorder && recorder.state !== "inactive") {
        recorder.stop();
    }
}

recordBtn.onclick = () => {
    if (isRecording) {
        stopRecording();
    } else {
        startRecording();
    }
};


