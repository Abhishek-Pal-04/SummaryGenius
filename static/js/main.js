// Cache DOM elements
const form = document.getElementById('url-form');
const urlInput = document.getElementById('video-url');
const spinner = document.getElementById('loading-spinner');
const errorMessage = document.getElementById('error-message');
const transcriptContainer = document.getElementById('transcript-container');
const summaryContainer = document.getElementById('summary-container');
const historyContainer = document.getElementById('history-container');

// History management with improved caching
const MAX_HISTORY_ITEMS = 10;
const CACHE_VERSION = '1.0';
const CACHE_KEY = 'videoSummaryHistory';

// Load history with versioning
function loadHistory() {
    const savedData = localStorage.getItem(CACHE_KEY);
    if (savedData) {
        try {
            const data = JSON.parse(savedData);
            if (data.version === CACHE_VERSION) {
                return data.history || [];
            }
        } catch (e) {
            console.error('Failed to parse history:', e);
        }
    }
    return [];
}

let history = loadHistory();

function saveHistory() {
    localStorage.setItem(CACHE_KEY, JSON.stringify({
        version: CACHE_VERSION,
        history: history
    }));
}

function updateHistory(url, summary, transcript, videoInfo) {
    const timestamp = new Date().toISOString();

    history.unshift({
        url,
        title: videoInfo.title,
        thumbnail_url: videoInfo.thumbnail_url,
        summary,
        transcript,
        timestamp
    });

    if (history.length > MAX_HISTORY_ITEMS) {
        history.pop();
    }

    saveHistory();
    renderHistory();
}

function renderHistory() {
    historyContainer.innerHTML = history.map((item, index) => `
        <div class="history-item p-3 border-bottom" data-index="${index}">
            <div class="d-flex align-items-center">
                <div class="thumbnail me-3">
                    <img src="${item.thumbnail_url}" alt="${item.title}" class="img-thumbnail" style="width: 120px;">
                </div>
                <div class="flex-grow-1">
                    <h6 class="mb-1 text-truncate">${item.title}</h6>
                    <small class="text-muted">
                        ${new Date(item.timestamp).toLocaleString()}
                    </small>
                </div>
            </div>
        </div>
    `).join('') || '<p class="text-muted p-3">No history yet...</p>';

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

let currentSummary = '';

function renderSummary(text) {
    if (typeof text === 'string') {
        currentSummary += text;
        // Convert markdown to HTML (basic implementation)
        const html = currentSummary
            .replace(/^# (.*$)/gm, '<h1>$1</h1>')
            .replace(/^## (.*$)/gm, '<h2>$1</h2>')
            .replace(/^### (.*$)/gm, '<h3>$1</h3>')
            .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
            .replace(/\*(.*?)\*/g, '<em>$1</em>')
            .replace(/- (.*$)/gm, '• $1<br>');

        summaryContainer.innerHTML = `<div class="summary-content">${html}</div>`;
    }
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

// Form submission handler with streaming support
form.addEventListener('submit', async (e) => {
    e.preventDefault();
    const url = urlInput.value.trim();

    if (!url) {
        showError('Please enter a YouTube URL');
        return;
    }

    showLoading(true);
    errorMessage.style.display = 'none';
    currentSummary = '';
    summaryContainer.innerHTML = '<div class="summary-content">Generating summary...</div>';

    try {
        const response = await fetch('/api/transcript', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ url })
        });

        if (!response.ok) {
            throw new Error('Failed to fetch transcript');
        }

        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let videoInfo, transcriptData;

        while (true) {
            const { value, done } = await reader.read();
            if (done) break;

            const chunk = decoder.decode(value);
            const lines = chunk.split('\n');

            for (const line of lines) {
                if (line.startsWith('data: ')) {
                    try {
                        const data = JSON.parse(line.slice(6));

                        switch (data.type) {
                            case 'summary':
                                renderSummary(data.content);
                                break;
                            case 'video_info':
                                videoInfo = data.content;
                                break;
                            case 'transcript':
                                transcriptData = data.content;
                                renderTranscript(data.content);
                                break;
                            case 'error':
                                showError(data.content);
                                break;
                            case 'done':
                                if (videoInfo && transcriptData) {
                                    updateHistory(url, currentSummary, transcriptData, videoInfo);
                                }
                                break;
                        }
                    } catch (e) {
                        console.error('Failed to parse SSE data:', e);
                    }
                }
            }
        }

    } catch (error) {
        showError(error.message);
    } finally {
        showLoading(false);
    }
});

// Initialize history on page load
renderHistory();