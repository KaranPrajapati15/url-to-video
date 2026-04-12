document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyze-btn');
    const urlInput = document.getElementById('video-url');
    const loader = document.getElementById('loader');
    const resultCard = document.getElementById('result-card');
    const formatsList = document.getElementById('formats-list');

    analyzeBtn.addEventListener('click', async () => {
        const url = urlInput.value.trim();
        if (!url) {
            alert('Please paste a video URL first!');
            return;
        }

        // Reset UI
        resultCard.style.display = 'none';
        loader.style.display = 'flex';
        formatsList.innerHTML = '';

        try {
            const response = await fetch('/info', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ url }),
            });

            const data = await response.json();

            if (data.error) {
                alert('Error: ' + data.error);
                loader.style.display = 'none';
                return;
            }

            // Update UI with results
            document.getElementById('video-thumb').src = data.thumbnail;
            document.getElementById('video-title').textContent = data.title;
            document.getElementById('video-meta').textContent = `${data.uploader || 'Unknown'} • ${formatDuration(data.duration)}`;

            // Single Best Option (8K/4K/Best with Sound)
            const downloadUrl = `/download?url=${encodeURIComponent(data.url)}`;
            
            const btn = document.createElement('button');
            btn.className = 'format-btn';
            btn.style.borderColor = 'var(--primary)';
            btn.style.padding = '20px 40px';
            btn.style.fontSize = '1.2rem';
            btn.style.width = 'auto';
            btn.style.minWidth = '300px';
            btn.style.backgroundColor = 'var(--primary)';
            btn.style.color = 'white';
            
            btn.innerHTML = `
                <strong>Download Max Quality (8K)</strong>
                <span style="display:block; font-size: 0.8rem; margin-top: 5px;">Includes High-Def Audio • All resolutions supported</span>
            `;
            
            btn.addEventListener('click', () => {
                // Show a notice that server is processing
                btn.innerHTML = '<strong>Processing...</strong><span style="display:block; font-size: 0.8rem; mt-5px;">Merging 8K Video + Audio. Please wait.</span>';
                btn.disabled = true;
                btn.style.opacity = '0.7';
                
                // Trigger download
                window.location.href = downloadUrl;
                
                // Reset after some time if it doesn't refresh
                setTimeout(() => {
                    btn.innerHTML = '<strong>Download Ready</strong><span style="display:block; font-size: 0.8rem; mt-5px;">Click to restart if download fails</span>';
                    btn.disabled = false;
                    btn.style.opacity = '1';
                }, 10000);
            });
            
            formatsList.appendChild(btn);

            const note = document.createElement('p');
            note.style.fontSize = '0.8rem';
            note.style.marginTop = '1rem';
            note.style.opacity = '0.6';
            note.textContent = 'Note: 8K merging happens on the server. The download will start automatically once processing is complete (can take a few minutes).';
            formatsList.appendChild(note);

            loader.style.display = 'none';
            resultCard.style.display = 'grid';

        } catch (error) {
            console.error('Fetch error:', error);
            alert('Failed to connect to backend server. Make sure app.py is running.');
            loader.style.display = 'none';
        }
    });

    function formatDuration(seconds) {
        if (!seconds) return 'N/A';
        const hrs = Math.floor(seconds / 3600);
        const mins = Math.floor((seconds % 3600) / 60);
        const secs = seconds % 60;
        return [hrs, mins, secs]
            .map(v => v < 10 ? '0' + v : v)
            .filter((v, i) => v !== '00' || i > 0)
            .join(':');
    }
});
