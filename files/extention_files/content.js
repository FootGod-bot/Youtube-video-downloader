(function () {
  const buttonText = "Download";
  const gapSize = 10;

  function getCleanUrl() {
    const url = new URL(window.location.href);
    const base = "https://www.youtube.com";
    
    if (url.pathname.startsWith("/watch")) {
      return `${base}/watch?v=${url.searchParams.get("v")}`;
    } else if (url.pathname.startsWith("/shorts")) {
      const id = url.pathname.split("/")[2]; // /shorts/{id}
      return `${base}/shorts?v=${id}`;
    } else if (url.pathname.startsWith("/playlist")) {
      return `${base}/playlist?list=${url.searchParams.get("list")}`;
    }
    return null;
  }

  function addButton() {
    const pathname = window.location.pathname;
    if (!["/watch", "/playlist"].some(p => pathname.startsWith(p)) && !pathname.startsWith("/shorts")) {
      return; // don't show button on other pages
    }

    const micButton = document.querySelector('ytd-microphone-button-renderer, #voice-search-button, [aria-label="Search with your voice"]');
    const createButton = document.querySelector('ytd-create-icon, #create-icon, [aria-label="Create"]');

    if (micButton && createButton && !document.getElementById('send-to-yt-dlp-btn')) {
      const btn = document.createElement("button");
      btn.id = "send-to-yt-dlp-btn";
      btn.className = "yt-spec-button-shape-next yt-spec-button-shape-next--tonal yt-spec-button-shape-next--mono yt-spec-button-shape-next--size-m";
      btn.setAttribute("aria-label", buttonText);
      btn.style.alignSelf = "center";
      btn.style.margin = `0 ${gapSize}px`;
      btn.style.transition = "background 0.2s"; // smooth color change
      btn.innerHTML = `<div class="cbox">${buttonText}</div>`;

      btn.addEventListener("click", () => {
        const cleanUrl = getCleanUrl();
        if (!cleanUrl) return;

        // Visual feedback: flash white like YouTube
        btn.style.background = "#fff";
        btn.style.color = "#000";
        setTimeout(() => {
          btn.style.background = "";
          btn.style.color = "";
        }, 300);

        fetch("http://127.0.0.1:5000/save", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ url: cleanUrl }),
        }).catch(() => {});
      });

      createButton.parentNode.insertBefore(btn, createButton);
    }
  }

  const observer = new MutationObserver(() => addButton());
  observer.observe(document.body, { childList: true, subtree: true });

  addButton();
})();
