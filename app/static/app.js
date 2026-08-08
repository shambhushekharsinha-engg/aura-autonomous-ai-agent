let agentId = localStorage.getItem('auraAgentId');
let allDecisions = []; // store for report

// Navigation Tabs
document.querySelectorAll('.nav-btn').forEach(btn => {
    btn.addEventListener('click', (e) => {
        document.querySelectorAll('.nav-btn').forEach(b => b.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(tc => tc.classList.remove('active'));
        
        const target = e.currentTarget;
        target.classList.add('active');
        const tabId = target.getAttribute('data-tab');
        document.getElementById(`tab-${tabId}`).classList.add('active');
        
        const titleMap = {
            'feed': 'Research Feed',
            'decisions': 'Editorial Judgments',
            'persona': 'AURA Persona'
        };
        document.getElementById('current-view-title').innerText = titleMap[tabId];
        
        // Show download button only on decisions tab
        document.getElementById('btn-download-report').style.display = tabId === 'decisions' ? 'flex' : 'none';
    });
});

function downloadReport() {
    if (allDecisions.length === 0) return alert('No decisions to export yet.');
    let csv = 'Status,Score,Topic,Reason,Date\n';
    allDecisions.forEach(d => {
        const topic = `"${d.topic.replace(/"/g, '""')}"`;
        csv += `${d.decision},${Math.round(d.score)},${topic},${d.reason},${d.createdAt}\n`;
    });
    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `AURA_Decisions_Report_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
}

async function sharePost(btn, postId) {
    const originalText = btn.innerHTML;
    btn.innerHTML = `<i class="fa-solid fa-check"></i> Copied!`;
    navigator.clipboard.writeText(`Check out this AI research post published by AURA:\nhttps://aura-autonomous-ai-agent.up.railway.app/#${postId}`);
    setTimeout(() => { btn.innerHTML = originalText; }, 2000);
}

async function initAgent() {
    try {
        const res = await fetch('/api/agent/init', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                persona: { name: "AURA", domain: "AI Technology Research" }
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
    document.getElementById('cycles-count').innerText = health.cyclesCompleted;
    
    const wStatus = document.getElementById('worker-status');
    if (health.workerRunning) {
        wStatus.className = 'online';
        wStatus.innerHTML = '● Worker Online';
    } else {
        wStatus.className = 'offline';
        wStatus.innerHTML = '○ Worker Offline';
    }
    
    const timeSince = health.lastCycleAt ? Math.floor((new Date() - new Date(health.lastCycleAt)) / 1000) : '--';
    const timeUntil = health.nextCycleAt ? Math.floor((new Date(health.nextCycleAt) - new Date()) / 1000) : '--';
    
    document.getElementById('last-cycle-time').innerText = timeSince !== '--' ? `${timeSince}s ago` : '--';
    document.getElementById('next-cycle-time').innerText = timeUntil !== '--' ? (timeUntil > 0 ? `${timeUntil}s` : 'Now...') : '--';
}

function renderDecisions(decisions) {
    allDecisions = decisions;
    const container = document.getElementById('decisions-container');
    const latestContainer = document.getElementById('latest-decision-content');
    
    if (decisions.length === 0) {
        container.innerHTML = `<div class="loading-state"><p>No decisions yet...</p></div>`;
        return;
    }
    
    // Render Latest Decision in Sidebar
    const ld = decisions[0];
    const isLdPub = ld.decision === 'PUBLISH';
    const ldIcon = isLdPub ? '<i class="fa-solid fa-check"></i>' : '<i class="fa-solid fa-xmark"></i>';
    latestContainer.innerHTML = `
        <span class="ld-title" title="${ld.topic}">${ld.topic}</span>
        <div class="ld-status ${isLdPub ? 'publish' : 'reject'}">
            <span class="ld-score">${Math.round(ld.score)}</span>
            ${ldIcon} ${ld.decision} ${!isLdPub ? `<span style="color:var(--text-tertiary);font-weight:normal;font-size:0.7rem;margin-left:4px;">${ld.reason}</span>` : ''}
        </div>
    `;
    
    container.innerHTML = decisions.map(d => {
        const isPub = d.decision === 'PUBLISH';
        const icon = isPub ? '<i class="fa-solid fa-check"></i>' : '<i class="fa-solid fa-xmark"></i>';
        const statusClass = isPub ? 'publish' : 'reject';
        const reason = isPub ? 'ACCEPTED' : d.reason;
        
        return `
        <div class="dec-row">
            <div class="dec-status ${statusClass}">${icon} ${d.decision}</div>
            <div class="dec-score">${Math.round(d.score)}</div>
            <div class="dec-topic" title="${d.topic}">${d.topic}</div>
            <div class="dec-reason">${reason}</div>
        </div>
    `}).join('');
}

function renderFeed(posts) {
    const container = document.getElementById('feed-container');
    if (posts.length === 0) {
        container.innerHTML = `<div class="loading-state"><div class="spinner"></div><p>Awaiting first discovery cycle...</p></div>`;
        return;
    }
    
    container.innerHTML = posts.map(post => {
        const dateStr = new Date(post.createdAt).toLocaleString([], { dateStyle: 'short', timeStyle: 'short' });
        
        let sourcesHtml = '';
        if (post.sources && post.sources.length > 0) {
            sourcesHtml = post.sources.map(s => {
                const domain = new URL(s).hostname.replace('www.', '');
                return `<a href="${s}" target="_blank" class="source-badge">
                            <i class="fa-solid fa-link"></i> ${domain}
                        </a>`;
            }).join('');
        }

        return `
        <div class="post-card" id="${post.id}">
            <div class="post-meta">
                <div class="time"><i class="fa-regular fa-clock"></i> ${dateStr}</div>
                <button class="share-btn" onclick="sharePost(this, '${post.id}')" aria-label="Share Post">
                    <i class="fa-solid fa-share-nodes"></i> Share
                </button>
            </div>
            
            <div class="post-text colorful-lines">${post.text}</div>
            
            <div class="post-blocks">
                <div class="insight-block rationale">
                    <div class="insight-header"><i class="fa-solid fa-microscope"></i> Editorial Rationale</div>
                    <div class="insight-content">${post.rationale}</div>
                </div>
                
                <div class="insight-block memory">
                    <div class="insight-header"><i class="fa-solid fa-brain"></i> Memory Connection</div>
                    <div class="insight-content">${post.stance || 'No explicit stance recorded.'}</div>
                </div>
            </div>
            
            <div class="post-sources">${sourcesHtml}</div>
        </div>
        `;
    }).join('');
}

async function fetchData() {
    if (!agentId) return;
    
    try {
        const [healthRes, decRes, feedRes] = await Promise.all([
            fetch(`/api/agent/health`),
            fetch(`/api/agent/decisions?agentId=${agentId}`),
            fetch(`/api/agent/feed?agentId=${agentId}`)
        ]);
        
        if (decRes.status === 404 || feedRes.status === 404) {
            console.log("Agent not found in DB. Re-initializing...");
            localStorage.removeItem('auraAgentId');
            agentId = null;
            initAgent();
            return;
        }
        
        if (healthRes.ok) {
            const health = await healthRes.json();
            updateHealth(health);
            // Wake up worker if offline
            if (!health.workerRunning) {
                console.log("Worker offline. Waking it up...");
                initAgent();
            }
        }
        
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

setInterval(fetchData, 5000); // Polling faster for better demo feel
