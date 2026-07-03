document.addEventListener('DOMContentLoaded', () => {
    // 1. App State
    let appData = {
        last_updated: null,
        articles: []
    };

    let activeCategory = 'AI'; // Default selected category

    // 2. DOM Elements
    const lastUpdatedTime = document.getElementById('last-updated-time');
    const feedHeaderSection = document.querySelector('.feed-header-section');
    const feedCategoryTitle = document.getElementById('feed-category-title');
    const feedCategoryDesc = document.getElementById('feed-category-desc');
    const newsFeedGrid = document.getElementById('news-feed-grid');
    const loadingState = document.getElementById('loading-state');
    const emptyState = document.getElementById('empty-state');
    
    // Story navigation buttons
    const storyTabs = {
        'AI': document.getElementById('story-tab-ai'),
        'SCMP': document.getElementById('story-tab-scmp'),
        'Aeon': document.getElementById('story-tab-aeon')
    };

    // Stats counts
    const countAI = document.getElementById('count-ai');
    const countSCMP = document.getElementById('count-scmp');
    const countAeon = document.getElementById('count-aeon');

    // Error Overlay
    const errorOverlay = document.getElementById('error-overlay');
    const errorDetailsText = document.getElementById('error-details-text');

    // 3. Initialize Feed Dashboard
    async function init() {
        try {
            showLoading(true);
            console.log("Fetching news aggregator JSON database...");
            const response = await fetch('data/news_data.json?t=' + Date.now());
            if (!response.ok) {
                throw new Error(`HTTP Error ${response.status}: ${response.statusText}`);
            }
            
            const rawData = await response.text();
            appData = JSON.parse(rawData);
            
            // Validate data structure
            if (!appData.articles || !Array.isArray(appData.articles)) {
                appData.articles = [];
            }
            
            showLoading(false);
            setupTabs();
            renderDashboard();
            switchTab('AI'); // Start with AI feed
            
        } catch (error) {
            console.error("Aggregation Database Loading Failure:", error);
            showLoading(false);
            showError(error.message);
        }
    }

    // 4. Set Event Listeners for Story Circular Tabs
    function setupTabs() {
        Object.entries(storyTabs).forEach(([category, tabBtn]) => {
            if (tabBtn) {
                tabBtn.addEventListener('click', () => {
                    switchTab(category);
                });
            }
        });
    }

    // 5. Switch Active Feed Tab
    function switchTab(category) {
        activeCategory = category;
        
        // Toggle active class on circular buttons
        Object.entries(storyTabs).forEach(([cat, btn]) => {
            if (btn) {
                if (cat === category) {
                    btn.classList.add('active');
                    btn.querySelector('.story-ring').classList.remove('unread');
                    btn.querySelector('.story-ring').classList.add('read');
                } else {
                    btn.classList.remove('active');
                }
            }
        });

        // Update active header themes & titles
        feedHeaderSection.className = 'feed-header-section'; // reset
        feedHeaderSection.classList.add(`theme-${category.toLowerCase()}`);

        if (category === 'AI') {
            feedCategoryTitle.textContent = '🤖 AI & Tech Breakthroughs';
            feedCategoryDesc.textContent = 'Curated news from top AI labs, companies, and web releases.';
        } else if (category === 'SCMP') {
            feedCategoryTitle.textContent = '🌐 SCMP Geopolitics';
            feedCategoryDesc.textContent = 'Strategic geopolitical, chip war, and tech updates from China/Asia.';
        } else {
            feedCategoryTitle.textContent = '📖 Aeon Philosophical Essays';
            feedCategoryDesc.textContent = 'Thought-provoking essays and summaries from Aeon & Psyche.';
        }

        // Render card feed
        renderFeed();
    }

    // 6. Render News Feed Cards
    function renderFeed() {
        newsFeedGrid.innerHTML = '';
        
        const filtered = appData.articles.filter(a => a.category === activeCategory);
        
        if (filtered.length === 0) {
            emptyState.style.display = 'flex';
            newsFeedGrid.style.display = 'none';
            return;
        }

        emptyState.style.display = 'none';
        newsFeedGrid.style.display = 'grid';

        filtered.forEach(article => {
            const card = document.createElement('article');
            card.className = `news-card card-${activeCategory.toLowerCase()}`;
            
            const relativeTime = formatRelativeTime(article.published_date);
            const sourceText = article.source || 'Unknown';
            const titleText = article.title || 'Untitled Article';
            
            // Build card header
            let cardHtml = `
                <div class="card-meta">
                    <span class="source-tag">${escapeHtml(sourceText)}</span>
                    <span class="card-date">${relativeTime}</span>
                </div>
                <div class="card-body">
                    <h3 class="card-title">${escapeHtml(titleText)}</h3>
            `;
            
            // Build card body based on category
            if (activeCategory === 'Aeon') {
                const bulletText = article.summary || '';
                // Split bullets on line breaks or bullet markers
                const bullets = bulletText.split(/\n|•|-/g)
                    .map(b => b.trim())
                    .filter(b => b.length > 5);
                
                if (bullets.length > 0) {
                    cardHtml += `<ul class="card-bullets">`;
                    bullets.forEach(b => {
                        cardHtml += `<li>${escapeHtml(b.replace(/^[•\-\*\s]+/, ''))}</li>`;
                    });
                    cardHtml += `</ul>`;
                } else {
                    cardHtml += `<p class="card-summary">${escapeHtml(bulletText)}</p>`;
                }
            } else {
                const summaryText = article.summary || 'No summary available.';
                cardHtml += `<p class="card-summary">${escapeHtml(summaryText)}</p>`;
            }
            
            // Close card body and add footer link
            const linkUrl = article.link || '#';
            const linkLabel = activeCategory === 'Aeon' ? 'Read full essay' : 'Read full story';
            
            cardHtml += `
                </div>
                <div class="card-footer">
                    <a href="${linkUrl}" target="_blank" rel="noopener noreferrer" class="read-link">
                        ${linkLabel} <span>&rarr;</span>
                    </a>
                </div>
            `;
            
            card.innerHTML = cardHtml;
            newsFeedGrid.appendChild(card);
        });
    }

    // 7. Render Dashboard Indicators & Counts
    function renderDashboard() {
        // Last updated time stamp
        if (appData.last_updated) {
            const dt = new Date(appData.last_updated);
            lastUpdatedTime.textContent = "Synced: " + dt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' ' + dt.toLocaleDateString([], { month: 'short', day: 'numeric' });
        } else {
            lastUpdatedTime.textContent = "No data found";
        }

        // Count items in each category
        const aiCount = appData.articles.filter(a => a.category === 'AI').length;
        const scmpCount = appData.articles.filter(a => a.category === 'SCMP').length;
        const aeonCount = appData.articles.filter(a => a.category === 'Aeon').length;

        // Display numbers on circular tab labels
        countAI.textContent = aiCount > 0 ? `${aiCount} updates` : "No news";
        countSCMP.textContent = scmpCount > 0 ? `${scmpCount} updates` : "No news";
        countAeon.textContent = aeonCount > 0 ? `${aeonCount} essays` : "No essays";

        // Set dimness states
        toggleTabAvailability('AI', aiCount);
        toggleTabAvailability('SCMP', scmpCount);
        toggleTabAvailability('Aeon', aeonCount);
    }

    function toggleTabAvailability(category, count) {
        const btn = storyTabs[category];
        if (!btn) return;
        
        const ring = btn.querySelector('.story-ring');
        if (count > 0) {
            ring.classList.add('unread');
            ring.classList.remove('read');
            btn.style.opacity = '';
            btn.style.pointerEvents = '';
        } else {
            ring.classList.remove('unread');
            ring.classList.add('read');
            btn.style.opacity = '0.4';
            btn.style.pointerEvents = 'none'; // Disable click if no content
        }
    }

    // 8. Helper UIs: Spinner & Error states
    function showLoading(isLoading) {
        if (loadingState) {
            loadingState.style.display = isLoading ? 'flex' : 'none';
        }
    }

    function showError(message) {
        if (errorOverlay) {
            errorOverlay.style.display = 'flex';
            if (errorDetailsText) {
                errorDetailsText.textContent = message;
            }
        }
    }

    // Convert ISO Timestamps to Relative Date-Time Text
    function formatRelativeTime(dateStr) {
        if (!dateStr) return '';
        try {
            const date = new Date(dateStr);
            const now = new Date();
            const diffMs = now.getTime() - date.getTime();
            
            // Safeguard against future clock differences
            if (diffMs <= 0) return 'Just now';
            
            const diffMins = Math.floor(diffMs / (60 * 1000));
            const diffHours = Math.floor(diffMs / (60 * 60 * 1000));
            
            if (diffMins < 60) {
                return `${diffMins}m ago`;
            } else {
                return `${diffHours}h ago`;
            }
        } catch (e) {
            return '';
        }
    }

    function escapeHtml(str) {
        if (!str) return '';
        return str
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;')
            .replace(/'/g, '&#039;');
    }

    // Fire application start
    init();
});
