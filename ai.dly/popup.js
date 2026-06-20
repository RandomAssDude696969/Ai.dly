// === LOADER ===
function showLoader() {
  const loader = document.getElementById("loader-container");
  if (loader) loader.style.display = "flex";
}

function hideLoader() {
  const loader = document.getElementById("loader-container");
  if (loader) loader.style.display = "none";
}

// === MESSAGE HANDLING ===
function appendMessage(role, text) {
  const messagesDiv = document.getElementById("messages");
  const div = document.createElement("div");
  div.className = role;
  div.innerHTML = `<strong>${role === "user" ? "You" : "AI"}</strong>: ${text}`;
  messagesDiv.appendChild(div);
  messagesDiv.scrollTop = messagesDiv.scrollHeight;
}

// === BACKEND COMMUNICATION ===
async function sendMessageToBackend(message) {
  appendMessage("user", message);

  const session_id = localStorage.getItem("session_id") || Date.now().toString();
  localStorage.setItem("session_id", session_id);

  showLoader();

  try {
    const response = await fetch("http://localhost:8080/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ prompt: message, session_id })
    });

    const raw = await response.text();
    console.log("Chat response:", raw);

    const data = JSON.parse(raw);
    if (data.response) {
      appendMessage("ai", data.response);
    } else {
      appendMessage("ai", "Chat failed.");
    }
  } catch (err) {
    console.error("Chat error:", err);
    appendMessage("ai", "Could not connect to chat.");
  } finally {
    hideLoader();
  }
}

// === CHAT FORM HANDLER ===
document.addEventListener("DOMContentLoaded", () => {
  const chatForm = document.getElementById("chat-form");
  const messageInput = document.getElementById("message-input");

  chatForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const msg = messageInput.value.trim();
    if (msg) {
      sendMessageToBackend(msg);
      messageInput.value = "";
    }
  });

  // === ESSAY BUTTON ===
  const essayBtn = document.getElementById("essay");
  if (essayBtn) {
    essayBtn.addEventListener("click", async () => {
      const topic = prompt("What topic should the essay be on?");
      if (!topic) return;

      appendMessage("user", `Write an essay on "${topic}"`);
      console.log("Sending topic to backend:", topic);

      showLoader();
      try {
        const response = await fetch("http://localhost:8080/essay", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ topic })
        });

        const raw = await response.text();
        const data = JSON.parse(raw);

        if (data.essay) {
          appendMessage("ai", `Essay:\n${data.essay}`);
        } else {
          appendMessage("ai", "Essay not generated.");
        }
      } catch (err) {
        console.error("Essay error:", err);
        appendMessage("ai", "Could not generate essay.");
      } finally {
        hideLoader();
      }
    });
  }

  // === YOUTUBE SUMMARY ===
  const ytButton = document.getElementById("youtube_summary");
  if (ytButton) {
    ytButton.addEventListener("click", async () => {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const url = tab.url;

      if (!url.includes("youtube.com")) {
        appendMessage("ai", "Please open a YouTube video.");
        return;
      }

      appendMessage("user", `Summarize this YouTube video: ${url}`);

      showLoader();
      try {
        const response = await fetch("http://localhost:8080/youtube_summary", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url })
        });

        const raw = await response.text();
        const data = JSON.parse(raw);

        if (data.summary) {
          appendMessage("ai", `Summary:\n${data.summary}`);
        } else {
          appendMessage("ai", "No summary found.");
        }
      } catch (err) {
        console.error("YouTube error:", err);
        appendMessage("ai", "Could not summarize video.");
      } finally {
        hideLoader();
      }
    });
  }

  // === PARAPHRASE BUTTON ===
  const paraphraseBtn = document.getElementById("paraphrase");
  if (paraphraseBtn) {
    paraphraseBtn.addEventListener("click", () => {
      const text = prompt("Text to paraphrase?");
      if (text) {
        sendMessageToBackend("Paraphrase this: " + text);
      }
    });
  }

  // === TRANSLATE BUTTON ===
  const translateBtn = document.getElementById("translate");
  if (translateBtn) {
    translateBtn.addEventListener("click", async () => {
      const text = prompt("Enter text to translate:");
      const lang = prompt("Translate to which language? (e.g., en, hi, fr):");

      if (!text || !lang) {
        appendMessage("ai", "Translation cancelled.");
        return;
      }

      appendMessage("user", `Translate to ${lang}: ${text}`);

      showLoader();
      try {
        const response = await fetch("http://localhost:8080/translate", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ text, target_lang: lang })
        });

        const raw = await response.text();
        const data = JSON.parse(raw);

        if (data.translated_text) {
          appendMessage("ai", `Translated to ${lang}:\n${data.translated_text}`);
        } else {
          appendMessage("ai", "No translation received.");
        }
      } catch (err) {
        console.error("Translate error:", err);
        appendMessage("ai", "Could not reach translation server.");
      } finally {
        hideLoader();
      }
    });
  }

  // === PDF UPLOAD ===
  const pdfUpload = document.getElementById("pdfUpload");
  if (pdfUpload) {
    pdfUpload.addEventListener("change", async (event) => {
      const file = event.target.files[0];
      if (!file) return;

      const formData = new FormData();
      formData.append("file", file);

      showLoader();
      try {
        const res = await fetch("http://localhost:8080/read_pdf", {
          method: "POST",
          body: formData
        });

        const data = await res.json();
        appendMessage("ai", "PDF Content:\n" + data.text);
      } catch (err) {
        console.error("PDF error:", err);
        appendMessage("ai", "Could not read PDF.");
      } finally {
        hideLoader();
      }
    });
  }

  // === WEBPAGE READER ===
  const readWebBtn = document.getElementById("readWebpageBtn");
  if (readWebBtn) {
    readWebBtn.addEventListener("click", async () => {
      const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
      const tabUrl = tab.url;

      appendMessage("user", `Read this webpage:\n${tabUrl}`);

      showLoader();
      try {
        const response = await fetch("http://localhost:8080/read_webpage", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: tabUrl })
        });

        const rawText = await response.text();

        if (!response.ok) {
          throw new Error("Server returned error: " + rawText);
        }

        const data = JSON.parse(rawText);
        if (data.text) {
          appendMessage("ai", `Webpage content:\n${data.text}`);
        } else {
          appendMessage("ai", "No content extracted.");
        }
      } catch (err) {
        console.error("Webpage fetch error:", err);
        appendMessage("ai", "Could not fetch webpage.");
      } finally {
        hideLoader();
      }
    });
  }
});
