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
    
    let currentMarkdown = '';
    let ws = null;

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
});
