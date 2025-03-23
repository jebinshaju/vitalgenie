const backendURL = "http://127.0.0.1:8000";

// ------------------ CHAT FUNCTIONS ------------------
async function sendMessage() {
  const chatInput = document.getElementById("chatInput");
  const message = chatInput.value;
  if (!message) {
    alert("Please enter a message.");
    return;
  }
  addChatBubble("You", message, "chat-user");
  chatInput.value = "";
  try {
    const response = await fetch(`${backendURL}/rag_chat`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ query: message })
    });
    const data = await response.json();
    addChatBubble("VitalGenie", data.response, "chat-ai");
  } catch (error) {
    console.error(error);
    addChatBubble("VitalGenie", "Error: " + error, "chat-ai");
  }
}

function addChatBubble(sender, text, bubbleClass) {
  const chatWindow = document.getElementById("chatWindow");
  const bubble = document.createElement("div");
  bubble.classList.add("chat-bubble", bubbleClass);
  bubble.innerHTML = `<strong>${sender}:</strong> ${text}`;
  chatWindow.appendChild(bubble);
  chatWindow.scrollTop = chatWindow.scrollHeight;
}

// ------------------ IMAGE UPLOAD (for Analysis) ------------------
async function handleImageUpload(file) {
  addChatBubble("You", "Uploaded an image for analysis.", "chat-user");
  const formData = new FormData();
  formData.append("file", file);
  formData.append("prompt", "Describe this medical image.");
  addChatBubble("VitalGenie", `<div class="spinner inline-block"></div> Loading image analysis...`, "chat-ai");
  try {
    const response = await fetch(`${backendURL}/image_analysis`, {
      method: "POST",
      body: formData
    });
    const data = await response.json();
    const analysis = data.analysis.replace(/\n/g, "<br>");
    addChatBubble("VitalGenie", `<strong>Image Analysis:</strong><br>${analysis}`, "chat-ai");
  } catch (error) {
    console.error(error);
    addChatBubble("VitalGenie", "Error during image analysis: " + error, "chat-ai");
  }
}

// ------------------ PRESCRIPTION UPLOAD ------------------
async function handlePrescriptionUpload(file) {
  addChatBubble("You", "Uploaded a prescription image.", "chat-user");
  const formData = new FormData();
  formData.append("file", file);
  addChatBubble("VitalGenie", `<div class="spinner inline-block"></div> Loading prescription extraction...`, "chat-ai");
  try {
    const response = await fetch(`${backendURL}/extract_prescription`, {
      method: "POST",
      body: formData
    });
    const data = await response.json();
    let htmlOutput = `<strong>Extracted Prescription:</strong><br>`;
    if (data.extracted_prescription && data.extracted_prescription.medications.length > 0) {
      data.extracted_prescription.medications.forEach((med, idx) => {
        htmlOutput += `<div class="mt-2 border border-gray-700 p-2 rounded">
          <p><strong>Medication ${idx+1}:</strong></p>
          <p>Name: ${med.name}</p>
          <p>Dosage: ${med.dosage}</p>
          <p>Frequency: ${med.frequency}</p>
          <p>Duration: ${med.duration || "N/A"}</p>
          <p>Notes: ${med.notes || "N/A"}</p>
        </div>`;
      });
    } else {
      htmlOutput += `<p>No prescription details found.</p>`;
    }
    addChatBubble("VitalGenie", htmlOutput, "chat-ai");
  } catch (error) {
    console.error(error);
    addChatBubble("VitalGenie", "Error during prescription extraction: " + error, "chat-ai");
  }
}

// ------------------ RECORDING FUNCTIONS ------------------
// Global variables for recording
let mediaRecorder;
let recordedChunks = [];
let recordedBlob = null; // New: store the recorded blob

const startBtn = document.getElementById("startRec");
const stopBtn = document.getElementById("stopRec");
const recordedAudio = document.getElementById("recordedAudio");
const recordingSpinner = document.getElementById("recordingSpinner");
const recordingOutput = document.getElementById("recordingOutput");

startBtn.addEventListener("click", async () => {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    alert("Audio recording is not supported in your browser.");
    return;
  }
  try {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);
    recordedChunks = [];
    recordedBlob = null; // Reset the blob
    mediaRecorder.start();
    
    mediaRecorder.ondataavailable = (e) => {
      if (e.data.size > 0) {
        recordedChunks.push(e.data);
      }
    };

    mediaRecorder.onstop = () => {
      // Create a blob from the recorded chunks
      recordedBlob = new Blob(recordedChunks, { type: "audio/webm" });
      // Update the audio element to allow playback
      recordedAudio.src = URL.createObjectURL(recordedBlob);
      recordedAudio.style.display = "block";
    };

    startBtn.disabled = true;
    stopBtn.disabled = false;
  } catch (err) {
    alert("Error accessing microphone: " + err);
  }
});

stopBtn.addEventListener("click", () => {
  if (mediaRecorder && mediaRecorder.state !== "inactive") {
    mediaRecorder.stop();
    startBtn.disabled = false;
    stopBtn.disabled = true;
  }
});

async function uploadRecording() {
  const fileInput = document.getElementById("recordUpload");
  recordingSpinner.style.display = "flex";
  recordingOutput.innerHTML = "";
  let formData = new FormData();

  // Prefer file upload if provided; otherwise use the recorded blob
  if (fileInput.files.length > 0) {
    formData.append("file", fileInput.files[0]);
  } else if (recordedBlob) {
    // Create a File object from the recorded blob
    const file = new File([recordedBlob], "recording.webm", { type: "audio/webm" });
    formData.append("file", file);
  } else {
    alert("No recording available. Please record or upload an audio file.");
    recordingSpinner.style.display = "none";
    return;
  }

  try {
    const response = await fetch(`${backendURL}/transcribe`, {
      method: "POST",
      body: formData
    });
    const data = await response.json();
    if (data.transcription) {
      const transcription = data.transcription.replace(/\n/g, "<br>");
      let diarizedHTML = "";
      if (data.diarized) {
        diarizedHTML = data.diarized.replace(/\n/g, "<br>");
      }
      let htmlOutput = `
        <h3 class="text-xl font-bold mb-2">Transcription</h3>
        <p class="mb-4">${transcription}</p>
      `;
      if (diarizedHTML) {
        htmlOutput += `
          <h3 class="text-xl font-bold mb-2">Diarized Transcript</h3>
          <p>${diarizedHTML}</p>
        `;
      }
      recordingOutput.innerHTML = htmlOutput;
      addChatBubble("VitalGenie", htmlOutput, "chat-ai");
    } else {
      recordingOutput.textContent = JSON.stringify(data, null, 2);
      addChatBubble("VitalGenie", JSON.stringify(data, null, 2), "chat-ai");
    }
  } catch (error) {
    console.error(error);
    recordingOutput.textContent = "Error: " + error;
    addChatBubble("VitalGenie", "Error: " + error, "chat-ai");
  } finally {
    recordingSpinner.style.display = "none";
  }
}


// ------------------ MONITORING FUNCTIONS ------------------
function updateMonitoringVideo() {
  const videoEl = document.getElementById("monitoringVideo");
  videoEl.src = "http://192.168.4.180/cam-hi.jpg?ts=" + new Date().getTime();
}
setInterval(updateMonitoringVideo, 1000);

async function pollMonitoringStatus() {
  try {
    const response = await fetch(`${backendURL}/monitor_status`);
    const data = await response.json();
    const statusDiv = document.getElementById("monitoringStatus");
    if (data.status && data.status.toUpperCase() === "ALERT") {
      statusDiv.innerHTML = `<span class="text-red-500">DANGER: ${data.message}</span>`;
    } else {
      statusDiv.innerHTML = `<span class="text-green-400">Status: OK</span>`;
    }
  } catch (error) {
    console.error("Error polling monitoring status:", error);
    document.getElementById("monitoringStatus").innerHTML = `<span class="text-yellow-500">Error fetching status.</span>`;
  }
}
setInterval(pollMonitoringStatus, 10000);
pollMonitoringStatus();

async function downloadEHRReport() {
  try {
    const response = await fetch(`${backendURL}/generate_ehr_pdf`);
    if (!response.ok) {
      throw new Error("Network response was not ok.");
    }
    const blob = await response.blob();
    // Create a temporary link element to trigger the download
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "ehr_report.pdf";
    document.body.appendChild(a);
    a.click();
    a.remove();
    window.URL.revokeObjectURL(url);
  } catch (error) {
    console.error("Error downloading EHR report:", error);
    alert("Failed to download EHR report: " + error);
  }
}

