let agentId = localStorage.getItem('auraAgentId');

async function initAgent() {
    try {
        const res = await fetch('/api/agent/init', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                persona: {
                    name: "AURA",
                    domain: "AI Technology Research"
                }
            })
        });
        const data = await res.json();
        agentId = data.agentId;
        localStorage.setItem('auraAgentId', agentId);
        fetchData();
    } catch (e) {
        console.error("Failed to init agent", e);
    }
}

async function fetchData() {
    if (!agentId) return;
    
    try {
        // Fetch Stats
        const statsRes = await fetch(`/api/agent/stats?agentId=${agentId}`);
        if (statsRes.ok) {
            const stats = await statsRes.json();
            document.getElementById('stat-discovered').innerText = stats.discovered;
            document.getElementById('stat-published').innerText = stats.published;
            document.getElementById('stat-rejected').innerText = stats.rejected;
        }

        // Fetch Feed
        const feedRes = await fetch(`/api/agent/feed?agentId=${agentId}`);
        if (feedRes.ok) {
            const feed = await feedRes.json();
            renderFeed(feed.posts);
        }
    } catch (e) {
        console.error("Failed fetching data", e);
    }
}

function renderFeed(posts) {
    const container = document.getElementById('feed-container');
    if (posts.length === 0) {
        container.innerHTML = '<div class="loading-state">Awaiting first discovery cycle...</div>';
        return;
    }
    
    container.innerHTML = '';
    posts.forEach(post => {
        const dateStr = new Date(post.createdAt).toLocaleString();
        
        const card = document.createElement('div');
        card.className = 'post-card';
        
        let sourcesHtml = '';
        if (post.sources && post.sources.length > 0) {
            sourcesHtml = post.sources.map(s => `<a href="${s}" target="_blank">View Source ↗</a>`).join('');
        }

        card.innerHTML = `
            <div class="post-meta">
                <span>PUBLISHED: ${dateStr}</span>
            </div>
            <div class="post-text">${post.text}</div>
            
            <div class="post-section-title">AURA'S STANCE</div>
            <div class="post-stance">${post.stance || 'No explicit stance recorded.'}</div>
            
            <div class="post-section-title">WHY SELECTED</div>
            <div class="post-rationale">${post.rationale}</div>
            
            <div class="post-sources">${sourcesHtml}</div>
        `;
        container.appendChild(card);
    });
}

// Initial Boot
if (!agentId) {
    initAgent();
} else {
    fetchData();
}

// Poll every 10 seconds
setInterval(fetchData, 10000);
