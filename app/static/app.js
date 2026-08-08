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

function updateHealth(health) {
    document.getElementById('stat-discovered').innerText = health.topicsDiscovered;
    document.getElementById('stat-published').innerText = health.postsPublished;
    document.getElementById('stat-rejected').innerText = health.topicsRejected;
    
    document.getElementById('worker-status').innerText = health.workerRunning ? '● Worker online' : '○ Worker offline';
    document.getElementById('worker-status').style.color = health.workerRunning ? 'var(--accent)' : 'var(--reject)';
    
    const timeSince = health.lastCycleAt ? Math.floor((new Date() - new Date(health.lastCycleAt)) / 1000) : '--';
    const timeUntil = health.nextCycleAt ? Math.floor((new Date(health.nextCycleAt) - new Date()) / 1000) : '--';
    
    document.getElementById('last-cycle-time').innerText = timeSince !== '--' ? `${timeSince} sec ago` : '--';
    document.getElementById('next-cycle-time').innerText = timeUntil !== '--' ? (timeUntil > 0 ? `${timeUntil} sec` : 'Running now...') : '--';
    document.getElementById('cycles-count').innerText = health.cyclesCompleted;
}

function renderDecisions(decisions) {
    const container = document.getElementById('decisions-container');
    if (decisions.length === 0) {
        container.innerHTML = '<div class="loading-state">No decisions yet...</div>';
        return;
    }
    
    container.innerHTML = decisions.map(d => `
        <div class="decision-item">
            <div class="decision-icon ${d.decision.toLowerCase()}">${d.decision === 'PUBLISH' ? '✓' : '✕'}</div>
            <div class="decision-score">${Math.round(d.score)}</div>
            <div class="decision-title" title="${d.topic}">${d.topic}</div>
        </div>
    `).join('');
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
            sourcesHtml = post.sources.map(s => {
                let cls = 'secondary';
                if (s.includes('arxiv.org') || s.includes('github.com')) cls = 'primary';
                const domain = new URL(s).hostname.replace('www.', '');
                return `<a href="${s}" target="_blank" class="source-badge ${cls}">
                            <span class="badge-dot"></span>${domain} ↗
                        </a>`;
            }).join('');
        }

        card.innerHTML = `
            <div class="post-meta">
                <span>PUBLISHED: ${dateStr}</span>
            </div>
            <div class="post-text">${post.text}</div>
            
            <div class="post-section-title">MEMORY CONNECTION</div>
            <div class="post-stance">${post.stance || 'No explicit stance recorded.'}</div>
            
            <div class="post-section-title">WHY AURA PUBLISHED THIS</div>
            <div class="post-rationale">${post.rationale}</div>
            
            <div class="post-sources">${sourcesHtml}</div>
        `;
        container.appendChild(card);
    });
}

async function fetchData() {
    if (!agentId) return;
    
    try {
        const [healthRes, decRes, feedRes] = await Promise.all([
            fetch(`/api/agent/health`),
            fetch(`/api/agent/decisions?agentId=${agentId}`),
            fetch(`/api/agent/feed?agentId=${agentId}`)
        ]);
        
        if (healthRes.ok) updateHealth(await healthRes.json());
        if (decRes.ok) renderDecisions((await decRes.json()).decisions);
        if (feedRes.ok) renderFeed((await feedRes.json()).posts);
        
    } catch (e) {
        console.error("Failed fetching data", e);
    }
}

if (!agentId) {
    initAgent();
} else {
    fetchData();
}

setInterval(fetchData, 10000);
