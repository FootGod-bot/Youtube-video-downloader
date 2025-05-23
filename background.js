chrome.contextMenus.create({
  id: "sendYouTubeURL",
  title: "Send to yt-dlp",
  contexts: ["page"],
  documentUrlPatterns: [
    "*://www.youtube.com/watch*",
    "*://www.youtube.com/shorts*"
  ]
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
  if (info.menuItemId === "sendYouTubeURL") {
    chrome.scripting.executeScript({
      target: { tabId: tab.id },
      func: () => window.location.href
    }, (results) => {
      if (chrome.runtime.lastError) {
        console.error("Script injection error:", chrome.runtime.lastError.message);
        alert("Could not get URL. Check permissions.");
        return;
      }
      const url = results[0].result;
      fetch("http://127.0.0.1:5000/save", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url })
      })
      .then(response => {
        if (!response.ok) {
          throw new Error("Server responded with status: " + response.status);
        }
        console.log("URL sent successfully:", url);
      })
      .catch(error => {
        console.error("Failed to send URL:", error);
        alert("Error sending URL: " + error.message);
      });
    });
  }
});
