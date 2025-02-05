// Cache DOM elements
const form = document.getElementById('url-form');
const urlInput = document.getElementById('video-url');
const spinner = document.getElementById('loading-spinner');
const errorMessage = document.getElementById('error-message');
const transcriptContainer = document.getElementById('transcript-container');
const summaryContainer = document.getElementById('summary-container');
const historyContainer = document.getElementById('history-container');

// History management
const MAX_HISTORY_ITEMS = 10;
let history = JSON.parse(localStorage.getItem('videoHistory') || '[]');

function updateHistory(url, summary, transcript) {
    const title = url; // In a real app, we might want to fetch the video title
    const timestamp = new Date().toISOString();
    
    history.unshift({ url, title, summary, transcript, timestamp });
    if (history.length > MAX_HISTORY_ITEMS) {
        history.pop();
    }
    
    localStorage.setItem('videoHistory', JSON.stringify(history));
    renderHistory();
}

function renderHistory() {
    historyContainer.innerHTML = history.map((item, index) => `
        <div class="history-item p-2 border-bottom" data-index="${index}">
            <div class="d-flex justify-content-between align-items-center">
                <div class="text-truncate">${item.title}</div>
                <small class="text-muted">${new Date(item.timestamp).toLocaleDateString()}</small>
            </div>
        </div>
    `).join('');
    
    // Add click handlers
    document.querySelectorAll('.history-item').forEach(item => {
        item.addEventListener('click', () => {
            const index = parseInt(item.dataset.index);
            const historyItem = history[index];
            renderTranscript(historyItem.transcript);
            renderSummary(historyItem.summary);
        });
    });
}

function renderTranscript(transcript) {
    transcriptContainer.innerHTML = transcript.map(entry => `
        <div class="mb-2">
            <span class="timestamp">${entry.timestamp}</span>
            <span class="text">${entry.text}</span>
        </div>
    `).join('');
}

function renderSummary(summary) {
    // Convert markdown to HTML (basic implementation)
    const html = summary
        .replace(/^# (.*$)/gm, '<h1>$1</h1>')
        .replace(/^## (.*$)/gm, '<h2>$1</h2>')
        .replace(/^### (.*$)/gm, '<h3>$1</h3>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/- (.*$)/gm, '• $1<br>');
    
    summaryContainer.innerHTML = `<div class="summary-content">${html}</div>`;
}

function showError(message) {
    errorMessage.textContent = message;
    errorMessage.style.display = 'block';
    setTimeout(() => {
        errorMessage.style.display = 'none';
    }, 5000);
}

function showLoading(show) {
    spinner.style.display = show ? 'block' : 'none';
    form.querySelector('button').disabled = show;
}

// Form submission handler
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const url = urlInput.value.trim();
    
    if (!url) {
        showError('Please enter a YouTube URL');
        return;
    }
    
    showLoading(true);
    errorMessage.style.display = 'none';
    
    try {
        const response = await fetch('/api/transcript', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url })
        });
        
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Failed to fetch transcript');
        }
        
        renderTranscript(data.transcript);
        renderSummary(data.summary);
        updateHistory(url, data.summary, data.transcript);
        
    } catch (error) {
        showError(error.message);
    } finally {
        showLoading(false);
    }
});

// Initialize history on page load
renderHistory();
