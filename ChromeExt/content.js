chrome.runtime.onMessage.addListener((request, sender, sendResponse) => {
    if (request.action === "scrapeLink") {
        const urlInput = document.getElementById('discogsUrlInput');
        const scrapeBtn = document.getElementById('scrapeBtn');

        if (urlInput && scrapeBtn) {
            console.log("WYSIWYG Extension: Received URL:", request.url);
            urlInput.value = request.url;

            // Dispatch an input event to make sure any listeners on the input field are triggered
            urlInput.dispatchEvent(new Event('input', { bubbles: true }));

            // Click the scrape button
            scrapeBtn.click();
            sendResponse({ status: "success" });
        } else {
            console.error("WYSIWYG Extension: Could not find the URL input or scrape button on the page.");
            sendResponse({ status: "error", message: "Elements not found" });
        }
    }
    return true; // Indicates that the response is sent asynchronously
});