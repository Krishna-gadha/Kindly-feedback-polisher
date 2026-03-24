chrome.commands.onCommand.addListener((command) => {
    if (command === 'convert-text') {
        chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
            chrome.scripting.executeScript({
                target: { tabId: tabs[0].id },
                function: getSelectedText
            }, (results) => {
                if (results && results[0] && results[0].result) {
                    chrome.storage.local.set({ selectedText: results[0].result }, () => {
                        chrome.action.openPopup();
                    });
                } else {
                    chrome.action.openPopup();
                }
            });
        });
    }
});

function getSelectedText() {
    return window.getSelection().toString().trim();
}