document.addEventListener('DOMContentLoaded', () => {
    const startBtn = document.getElementById('startBtn');
    if (!startBtn) return; // Only run on product page
    
    const queryInput = document.getElementById('queryInput');
    const statusContainer = document.getElementById('statusContainer');
    const statusList = document.getElementById('statusList');
    const loader = document.getElementById('loader');
    const reportHeader = document.getElementById('reportHeader');
    const reportContent = document.getElementById('reportContent');
    const downloadPdfBtn = document.getElementById('downloadPdfBtn');
    
    const historyContainer = document.getElementById('historyContainer');
    const historyList = document.getElementById('historyList');

    let currentMarkdown = '';
    let ws = null;

    // Load history on initial load
    fetchHistory();

    startBtn.addEventListener('click', () => {
        const query = queryInput.value.trim();
        if (!query) {
            alert('Please enter a research query.');
            return;
        }

        // Reset UI
        statusContainer.style.display = 'block';
        statusList.innerHTML = '';
        loader.style.display = 'block';
        reportHeader.style.display = 'none';
        reportContent.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">⏳</div>
                <p>Gathering intelligence...</p>
            </div>
        `;
        startBtn.disabled = true;

        // Establish WebSocket connection
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        ws = new WebSocket(`${protocol}//${window.location.host}/ws/research`);

        ws.onopen = () => {
            console.log('WebSocket connection established');
            ws.send(query);
            addStatus('Connection established. Initiating workflow...', false);
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                
                if (data.type === 'status') {
                    addStatus(data.message, false);
                } else if (data.type === 'complete') {
                    loader.style.display = 'none';
                    addStatus('Research complete!', true);
                    
                    // Render markdown
                    currentMarkdown = data.report;
                    // marked.parse is used from marked.js included in head
                    reportContent.innerHTML = marked.parse(currentMarkdown);
                    reportHeader.style.display = 'flex';
                    startBtn.disabled = false;
                    ws.close();
                    
                    // Refresh history list
                    fetchHistory();
                } else if (data.type === 'error') {
                    loader.style.display = 'none';
                    addStatus(`Error: ${data.message}`, false);
                    startBtn.disabled = false;
                    ws.close();
                }
            } catch (e) {
                console.error("Failed to parse websocket message", e);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket Error:', error);
            loader.style.display = 'none';
            addStatus('Connection error occurred.', false);
            startBtn.disabled = false;
        };

        ws.onclose = () => {
            console.log('WebSocket closed');
            startBtn.disabled = false;
        };
    });

    downloadPdfBtn.addEventListener('click', async () => {
        if (!currentMarkdown) return;
        
        downloadPdfBtn.disabled = true;
        downloadPdfBtn.innerHTML = 'Generating...';

        try {
            const response = await fetch('/download-pdf', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ markdown_text: currentMarkdown })
            });

            if (!response.ok) {
                throw new Error('Failed to generate PDF');
            }

            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = 'competitor_report.pdf';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
            document.body.removeChild(a);
        } catch (error) {
            console.error(error);
            alert('An error occurred while generating the PDF.');
        } finally {
            downloadPdfBtn.disabled = false;
            downloadPdfBtn.innerHTML = `
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg>
                Download PDF
            `;
        }
    });

    function addStatus(message, isComplete) {
        // Mark previous as completed if it wasn't
        const items = statusList.querySelectorAll('li');
        if (items.length > 0 && !isComplete) {
            items[items.length - 1].classList.add('completed');
        }

        const li = document.createElement('li');
        li.textContent = message;
        if (isComplete) {
            li.classList.add('completed');
        }
        statusList.appendChild(li);
        
        // Auto scroll to bottom of status
        statusContainer.scrollTop = statusContainer.scrollHeight;
    }

    async function fetchHistory() {
        if (!historyList) return;
        try {
            const res = await fetch('/api/reports');
            if (!res.ok) return;
            const reports = await res.json();
            historyList.innerHTML = '';
            
            if (reports.length === 0) {
                historyList.innerHTML = '<li style="color: var(--text-secondary); font-size: 0.9rem;">No past reports found.</li>';
                return;
            }
            
            reports.forEach(report => {
                const li = document.createElement('li');
                li.className = 'history-item';
                
                // Ensure date parses correctly by assuming UTC from sqlite
                const d = new Date(report.created_at + 'Z');
                const dateStr = d.toLocaleDateString(undefined, { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
                
                li.innerHTML = `
                    <div class="history-item-content">
                        <div class="history-item-query">${report.query}</div>
                        <div class="history-item-date">${dateStr}</div>
                    </div>
                    <button class="delete-btn" title="Delete Report">
                        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
                    </button>
                `;
                
                li.querySelector('.history-item-content').addEventListener('click', () => loadReport(report.id));
                
                li.querySelector('.delete-btn').addEventListener('click', async (e) => {
                    e.stopPropagation(); // prevent triggering the list item click
                    if(confirm('Are you sure you want to delete this report?')) {
                        await deleteReport(report.id);
                    }
                });
                historyList.appendChild(li);
            });
        } catch (e) {
            console.error("Failed to fetch history", e);
        }
    }

    async function loadReport(id) {
        try {
            const res = await fetch(`/api/reports/${id}`);
            if (!res.ok) throw new Error('Report not found');
            const report = await res.json();
            
            currentMarkdown = report.report_markdown;
            reportContent.innerHTML = marked.parse(currentMarkdown);
            reportHeader.style.display = 'flex';
            
            // Hide status container if we are just viewing a past report
            statusContainer.style.display = 'none';
        } catch (e) {
            console.error("Failed to load report", e);
            alert("Could not load the report.");
        }
    }

    async function deleteReport(id) {
        try {
            const res = await fetch(`/api/reports/${id}`, { method: 'DELETE' });
            if (!res.ok) throw new Error('Failed to delete report');
            
            // Clear current view
            reportContent.innerHTML = `
                <div class="empty-state">
                    <div class="empty-icon">📊</div>
                    <p>Your research report will appear here.</p>
                </div>
            `;
            reportHeader.style.display = 'none';
            currentMarkdown = '';
            
            // Refresh history
            fetchHistory();
        } catch (e) {
            console.error("Failed to delete report", e);
            alert("Could not delete the report.");
        }
    }
});
