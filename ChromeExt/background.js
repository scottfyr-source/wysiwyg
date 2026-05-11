// The function that will be injected into the page
function triggerScrape(url) {
    const urlInput = document.getElementById('discogsUrlInput');
    const scrapeBtn = document.getElementById('scrapeBtn');

    if (urlInput && scrapeBtn) {
        urlInput.value = url;
        // Dispatch input event to ensure any listeners catch the change
        urlInput.dispatchEvent(new Event('input', { bubbles: true }));
        scrapeBtn.click();
        console.log("WYSIWYG Extension: Scrape triggered for " + url);
    } else {
        console.error("WYSIWYG Extension: Could not find input or button.");
    }
}

chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "sendToWysiwyg",
        title: "Send to WYSIWYG Scraper",
        contexts: ["link"],
        targetUrlPatterns: [
            "*://*.discogs.com/release/*",
            "*://*.discogs.com/sell/item/*",
            "*://*.discogs.com/shop/item/*",
            "*://*.discogs.com/master/*"
        ]
    });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "sendToWysiwyg" && info.linkUrl) {
        const targetUrl = info.linkUrl;

        // Helper to inject the script
        const runScript = (tabId) => {
            chrome.scripting.executeScript({
                target: { tabId: tabId },
                func: triggerScrape,
                args: [targetUrl]
            }).catch(err => console.error("Script injection failed:", err));
        };

        // Find the tab where the WYSIWYG tool is running
        chrome.tabs.query({ url: ["http://127.0.0.1:8008/*", "http://localhost:8008/*"] }, (tabs) => {
            if (tabs.length > 0) {
                const wysiwygTab = tabs[0];
                chrome.tabs.update(wysiwygTab.id, { active: true });
                chrome.windows.update(wysiwygTab.windowId, { focused: true });
                runScript(wysiwygTab.id);
            } else {
                // If the tab isn't open, open it and then send the message
                chrome.tabs.create({ url: "http://127.0.0.1:8008/" }, (newTab) => {
                    // Wait for the tab to finish loading before sending the message
                    chrome.tabs.onUpdated.addListener(function listener(tabId, changeInfo) {
                        if (tabId === newTab.id && changeInfo.status === 'complete') {
                            chrome.tabs.onUpdated.removeListener(listener); // Clean up the listener
                            // Small delay to ensure DOM is ready
                            setTimeout(() => runScript(newTab.id), 500);
                        }
                    });
                });
            }
        });
    }
});