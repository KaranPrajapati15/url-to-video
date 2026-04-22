document.addEventListener('DOMContentLoaded', () => {
    const analyzeBtn = document.getElementById('analyze-btn');
    const urlInput = document.getElementById('video-url');
    const loader = document.getElementById('loader');
    const resultCard = document.getElementById('result-card');
    const formatsList = document.getElementById('formats-list');

    analyzeBtn.addEventListener('click', async () => {
        const url = urlInput.value.trim();
        if (!url) {
            showToast('Please paste a video URL first!', 'warning');
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
                showToast(data.error, 'error');
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
            showToast('Failed to connect to backend server. Make sure app.py is running.', 'error');
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

    // Toast notification system (replaces ugly alert() dialogs)
    function showToast(message, type = 'info') {
        // Remove any existing toast
        const existing = document.querySelector('.toast-notification');
        if (existing) existing.remove();

        const toast = document.createElement('div');
        toast.className = 'toast-notification';

        const colors = {
            error: { bg: 'rgba(220, 38, 38, 0.95)', icon: '⚠️' },
            warning: { bg: 'rgba(234, 179, 8, 0.95)', icon: '⚡' },
            info: { bg: 'rgba(59, 130, 246, 0.95)', icon: 'ℹ️' },
            success: { bg: 'rgba(34, 197, 94, 0.95)', icon: '✅' },
        };
        const style = colors[type] || colors.info;

        toast.style.cssText = `
            position: fixed;
            top: 20px;
            left: 50%;
            transform: translateX(-50%) translateY(-100px);
            background: ${style.bg};
            color: white;
            padding: 16px 28px;
            border-radius: 12px;
            font-size: 0.95rem;
            line-height: 1.5;
            max-width: 600px;
            width: 90%;
            z-index: 10000;
            backdrop-filter: blur(10px);
            box-shadow: 0 10px 40px rgba(0,0,0,0.3);
            transition: transform 0.4s cubic-bezier(0.34, 1.56, 0.64, 1), opacity 0.4s ease;
            opacity: 0;
            cursor: pointer;
            text-align: center;
        `;

        toast.innerHTML = `<span>${style.icon}</span> ${message}`;

        document.body.appendChild(toast);

        // Animate in
        requestAnimationFrame(() => {
            toast.style.transform = 'translateX(-50%) translateY(0)';
            toast.style.opacity = '1';
        });

        // Auto dismiss after 6 seconds
        const dismiss = () => {
            toast.style.transform = 'translateX(-50%) translateY(-100px)';
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 400);
        };

        toast.addEventListener('click', dismiss);
        setTimeout(dismiss, 6000);
    }
});
