/**
 * LAP Intelligence Hub v2 - Frontend Application
 * Research-backed JIRA analytics platform with dark theme and fuzzy search
 */

// ============================================================================
// Global State
// ============================================================================

const APP = {
    // Data
    searchIndex: [],
    epics: [],
    themes: [],
    themeIndex: {},
    themeData: {},
    allTickets: [],

    // UI State
    currentTab: 'dashboard',
    currentPage: 1,
    itemsPerPage: 50,
    sortColumn: 'key',
    sortDirection: 'asc',
    searchQuery: '',
    activeFilters: {
        type: [],
        status: [],
        theme: [],
        assignee: []
    },

    // Search
    fuse: null,
    searchResults: [],

    // Charts
    charts: {
        types: null,
        timeline: null,
        assignees: null
    },

    // Modal
    currentModalTicket: null,

    // Init flag
    initialized: false
};

// ============================================================================
// Utility Functions
// ============================================================================

/**
 * Safely escape HTML content using DOM methods
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

/**
 * Fetch JSON from data directory
 */
async function fetchJSON(path) {
    try {
        const response = await fetch(path);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status} loading ${path}`);
        }
        return await response.json();
    } catch (error) {
        console.error(`Error loading ${path}:`, error);
        throw error;
    }
}

/**
 * Debounce function for search input
 */
function debounce(func, delay) {
    let timeoutId;
    return function(...args) {
        clearTimeout(timeoutId);
        timeoutId = setTimeout(() => func(...args), delay);
    };
}

/**
 * Format date to readable string
 */
function formatDate(dateString) {
    if (!dateString) return 'N/A';
    return new Date(dateString).toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'short',
        day: 'numeric'
    });
}

/**
 * Get badge class for ticket type
 */
function getTypeBadgeClass(type) {
    const typeMap = {
        'Story': 'type-story',
        'Bug': 'type-bug',
        'Task': 'type-task',
        'Epic': 'type-epic'
    };
    return typeMap[type] || 'type-task';
}

/**
 * Get badge class for ticket status
 */
function getStatusBadgeClass(status) {
    const statusMap = {
        'To Do': 'status-todo',
        'In Progress': 'status-in-progress',
        'Done': 'status-done'
    };
    return statusMap[status] || 'status-todo';
}

/**
 * Get status class for result cards
 */
function getStatusClass(status) {
    const lower = status.toLowerCase().replace(/\s+/g, '-');
    return lower;
}

/**
 * Get type class for result cards
 */
function getTypeClass(type) {
    return type.toLowerCase();
}

// ============================================================================
// Data Loading
// ============================================================================

/**
 * Load search index (plain array)
 */
async function loadSearchIndex() {
    const data = await fetchJSON('data/search_index.json');
    APP.searchIndex = Array.isArray(data) ? data : (data.tickets || []);
    console.log(`Loaded ${APP.searchIndex.length} tickets for search`);
}

/**
 * Load epics (plain array)
 */
async function loadEpics() {
    const data = await fetchJSON('data/epics.json');
    APP.epics = Array.isArray(data) ? data : (data.epics || []);
    console.log(`Loaded ${APP.epics.length} epics`);
}

/**
 * Load themes (object with theme names as keys)
 */
async function loadThemes() {
    const data = await fetchJSON('data/themes.json');
    APP.themeData = data;
    APP.themes = Object.keys(data);

    // Build theme index for reverse lookup
    APP.themeIndex = {};
    for (const [name, info] of Object.entries(data)) {
        if (info && info.tickets) {
            for (const key of info.tickets) {
                if (!APP.themeIndex[key]) {
                    APP.themeIndex[key] = [];
                }
                APP.themeIndex[key].push(name);
            }
        }
    }
    console.log(`Loaded ${APP.themes.length} themes`);
}

/**
 * Load stats for dashboard
 */
async function loadStats() {
    const data = await fetchJSON('data/stats.json');
    return data;
}

/**
 * Initialize Fuse.js for fuzzy search
 */
function initializeFuse() {
    const fuseOptions = {
        keys: [
            { name: 'key', weight: 3.0 },
            { name: 'summary', weight: 2.0 },
            { name: 'description', weight: 1.0 },
            { name: 'assignee', weight: 0.5 }
        ],
        threshold: 0.3,
        distance: 100,
        includeScore: true,
        includeMatches: true,
        minMatchCharLength: 2,
        useExtendedSearch: true
    };

    APP.fuse = new Fuse(APP.searchIndex, fuseOptions);
    console.log('Fuse.js initialized');
}

/**
 * Perform search with current query and filters
 */
function performSearch(query) {
    APP.searchQuery = query;

    if (!query.trim()) {
        APP.searchResults = [];
        renderSearchResults();
        updateResultsCount();
        return;
    }

    let results = APP.fuse.search(query).map(result => ({
        ...result.item,
        score: result.score,
        matches: result.matches
    }));

    // Apply filters
    results = results.filter(ticket => {
        if (APP.activeFilters.type.length > 0 && !APP.activeFilters.type.includes(ticket.type)) {
            return false;
        }
        if (APP.activeFilters.status.length > 0 && !APP.activeFilters.status.includes(ticket.status)) {
            return false;
        }
        if (APP.activeFilters.assignee.length > 0 && !APP.activeFilters.assignee.includes(ticket.assignee)) {
            return false;
        }
        if (APP.activeFilters.theme.length > 0) {
            const ticketThemes = APP.themeIndex[ticket.key] || [];
            return APP.activeFilters.theme.some(theme => ticketThemes.includes(theme));
        }
        return true;
    });

    APP.searchResults = results;
    renderSearchResults();
    updateResultsCount();
}

// ============================================================================
// Dashboard Rendering
// ============================================================================

/**
 * Render dashboard KPI cards
 */
function renderDashboard(stats) {
    const kpiGrid = document.querySelector('.kpi-grid');
    kpiGrid.innerHTML = '';

    const kpis = [
        {
            value: stats.total_tickets || 0,
            label: 'Total Tickets'
        },
        {
            value: `${stats.completion_percentage || 0}%`,
            label: 'Completion Rate'
        },
        {
            value: stats.open_count || 0,
            label: 'Open Items'
        },
        {
            value: APP.epics.length,
            label: 'Epics'
        }
    ];

    kpis.forEach(kpi => {
        const card = document.createElement('div');
        card.className = 'kpi-card';
        card.innerHTML = `
            <div class="kpi-value">${escapeHtml(String(kpi.value))}</div>
            <div class="kpi-label">${escapeHtml(kpi.label)}</div>
        `;
        kpiGrid.appendChild(card);
    });
}

/**
 * Initialize and render charts
 */
function renderCharts(stats) {
    renderTypeChart(stats);
    renderTimelineChart(stats);
    renderAssigneesChart(stats);
}

/**
 * Render ticket types doughnut chart
 */
function renderTypeChart(stats) {
    const ctx = document.getElementById('chart-types');
    if (!ctx) return;

    if (APP.charts.types) {
        APP.charts.types.destroy();
    }

    const typeData = stats.types_breakdown || {};
    const labels = Object.keys(typeData);
    const data = Object.values(typeData);

    APP.charts.types = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: [
                    'rgba(68, 138, 255, 0.8)',
                    'rgba(105, 240, 174, 0.8)',
                    'rgba(255, 82, 82, 0.8)',
                    'rgba(255, 215, 64, 0.8)',
                    'rgba(179, 136, 255, 0.8)'
                ],
                borderColor: [
                    'rgba(68, 138, 255, 1)',
                    'rgba(105, 240, 174, 1)',
                    'rgba(255, 82, 82, 1)',
                    'rgba(255, 215, 64, 1)',
                    'rgba(179, 136, 255, 1)'
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            plugins: {
                legend: {
                    position: 'bottom',
                    labels: {
                        padding: 20,
                        font: { size: 12 }
                    }
                },
                title: {
                    display: true,
                    text: 'Ticket Types',
                    font: { size: 14, weight: 'bold' }
                }
            }
        }
    });
}

/**
 * Render timeline bar chart
 */
function renderTimelineChart(stats) {
    const ctx = document.getElementById('chart-timeline');
    if (!ctx) return;

    if (APP.charts.timeline) {
        APP.charts.timeline.destroy();
    }

    const timelineData = stats.timeline_breakdown || {};
    const labels = Object.keys(timelineData).sort();
    const data = labels.map(label => timelineData[label]);

    APP.charts.timeline = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Tickets Created',
                data: data,
                backgroundColor: 'rgba(68, 138, 255, 0.8)',
                borderColor: 'rgba(68, 138, 255, 1)',
                borderWidth: 2,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            indexAxis: 'x',
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Timeline',
                    font: { size: 14, weight: 'bold' }
                }
            },
            scales: {
                y: {
                    beginAtZero: true
                }
            }
        }
    });
}

/**
 * Render assignees horizontal bar chart
 */
function renderAssigneesChart(stats) {
    const ctx = document.getElementById('chart-assignees');
    if (!ctx) return;

    if (APP.charts.assignees) {
        APP.charts.assignees.destroy();
    }

    const assigneeData = stats.assignees_breakdown || {};
    const labels = Object.keys(assigneeData).slice(0, 10); // Top 10
    const data = labels.map(label => assigneeData[label]);

    APP.charts.assignees = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Assigned Tickets',
                data: data,
                backgroundColor: 'rgba(105, 240, 174, 0.8)',
                borderColor: 'rgba(105, 240, 174, 1)',
                borderWidth: 2,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: true,
            indexAxis: 'y',
            plugins: {
                legend: {
                    display: false
                },
                title: {
                    display: true,
                    text: 'Top Assignees',
                    font: { size: 14, weight: 'bold' }
                }
            },
            scales: {
                x: {
                    beginAtZero: true
                }
            }
        }
    });
}

// ============================================================================
// Search Rendering
// ============================================================================

/**
 * Update results count display
 */
function updateResultsCount() {
    const countEl = document.getElementById('search-results-count');
    if (APP.searchQuery.trim()) {
        countEl.textContent = `Found ${APP.searchResults.length} result${APP.searchResults.length !== 1 ? 's' : ''}`;
    } else {
        countEl.textContent = 'Enter a search query';
    }
}

/**
 * Render search results
 */
function renderSearchResults() {
    const container = document.getElementById('search-results');
    container.innerHTML = '';

    if (!APP.searchQuery.trim()) {
        container.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--color-text-muted);">Start searching to find tickets</div>';
        return;
    }

    if (APP.searchResults.length === 0) {
        container.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--color-text-muted);">No results found</div>';
        return;
    }

    APP.searchResults.forEach(ticket => {
        const card = document.createElement('div');
        card.className = 'search-result-card';

        const themes = APP.themeIndex[ticket.key] || [];
        const themesHtml = themes.length > 0
            ? `<div style="margin-top: 8px; font-size: 12px; color: var(--color-text-muted);">Themes: ${escapeHtml(themes.join(', '))}</div>`
            : '';

        card.innerHTML = `
            <div class="result-header">
                <span class="result-key">${escapeHtml(ticket.key)}</span>
                <span class="result-type ${getTypeClass(ticket.type)}">${escapeHtml(ticket.type)}</span>
                <span class="result-status ${getStatusClass(ticket.status)}">${escapeHtml(ticket.status)}</span>
            </div>
            <div class="result-summary">${escapeHtml(ticket.summary)}</div>
            <div class="result-description">${escapeHtml(ticket.description || '')}</div>
            <div class="result-meta">
                <span>Assignee: ${escapeHtml(ticket.assignee || 'Unassigned')}</span>
            </div>
            ${themesHtml}
        `;

        card.addEventListener('click', () => APP.showTicketModal(ticket));
        container.appendChild(card);
    });
}

/**
 * Build and render filter options
 */
function renderFilterOptions() {
    // Get unique values
    const types = [...new Set(APP.searchIndex.map(t => t.type))].sort();
    const statuses = [...new Set(APP.searchIndex.map(t => t.status))].sort();
    const assignees = [...new Set(APP.searchIndex.map(t => t.assignee).filter(Boolean))].sort();

    // Render type filter
    const typeFilter = document.getElementById('filter-type');
    typeFilter.innerHTML = '';
    types.forEach(type => {
        const div = document.createElement('div');
        div.className = 'filter-checkbox';
        div.innerHTML = `
            <input type="checkbox" id="filter-type-${escapeHtml(type)}" value="${escapeHtml(type)}" onchange="APP.toggleFilter('type', '${escapeHtml(type)}')">
            <label for="filter-type-${escapeHtml(type)}">${escapeHtml(type)}</label>
        `;
        typeFilter.appendChild(div);
    });

    // Render status filter
    const statusFilter = document.getElementById('filter-status');
    statusFilter.innerHTML = '';
    statuses.forEach(status => {
        const div = document.createElement('div');
        div.className = 'filter-checkbox';
        div.innerHTML = `
            <input type="checkbox" id="filter-status-${escapeHtml(status)}" value="${escapeHtml(status)}" onchange="APP.toggleFilter('status', '${escapeHtml(status)}')">
            <label for="filter-status-${escapeHtml(status)}">${escapeHtml(status)}</label>
        `;
        statusFilter.appendChild(div);
    });

    // Render theme filter
    const themeFilter = document.getElementById('filter-theme');
    themeFilter.innerHTML = '';
    APP.themes.sort().forEach(theme => {
        const div = document.createElement('div');
        div.className = 'filter-checkbox';
        div.innerHTML = `
            <input type="checkbox" id="filter-theme-${escapeHtml(theme)}" value="${escapeHtml(theme)}" onchange="APP.toggleFilter('theme', '${escapeHtml(theme)}')">
            <label for="filter-theme-${escapeHtml(theme)}">${escapeHtml(theme)}</label>
        `;
        themeFilter.appendChild(div);
    });

    // Render assignee filter
    const assigneeFilter = document.getElementById('filter-assignee');
    assigneeFilter.innerHTML = '';
    assignees.forEach(assignee => {
        const div = document.createElement('div');
        div.className = 'filter-checkbox';
        div.innerHTML = `
            <input type="checkbox" id="filter-assignee-${escapeHtml(assignee)}" value="${escapeHtml(assignee)}" onchange="APP.toggleFilter('assignee', '${escapeHtml(assignee)}')">
            <label for="filter-assignee-${escapeHtml(assignee)}">${escapeHtml(assignee)}</label>
        `;
        assigneeFilter.appendChild(div);
    });
}

// ============================================================================
// Epic Rendering
// ============================================================================

/**
 * Render epic cards
 */
function renderEpics() {
    const container = document.getElementById('epics-grid');
    container.innerHTML = '';

    if (APP.epics.length === 0) {
        container.innerHTML = '<div style="padding: 40px; color: var(--color-text-muted);">No epics found</div>';
        return;
    }

    APP.epics.forEach(epic => {
        const card = document.createElement('div');
        card.className = 'epic-card';

        const childTickets = APP.searchIndex.filter(t => t.parent_epic === epic.key);
        const completedTickets = childTickets.filter(t => t.status === 'Done').length;

        card.innerHTML = `
            <div class="epic-name">${escapeHtml(epic.name || epic.key)}</div>
            <div class="epic-stats">
                <div class="epic-stat">
                    <span>Child Tickets:</span>
                    <span class="epic-stat-value">${childTickets.length}</span>
                </div>
                <div class="epic-stat">
                    <span>Completed:</span>
                    <span class="epic-stat-value">${completedTickets}</span>
                </div>
                <div class="epic-stat">
                    <span>Progress:</span>
                    <span class="epic-stat-value">${childTickets.length > 0 ? Math.round((completedTickets / childTickets.length) * 100) : 0}%</span>
                </div>
            </div>
        `;

        card.addEventListener('click', () => APP.showEpicModal(epic, childTickets));
        container.appendChild(card);
    });
}

/**
 * Show epic details modal
 */
APP.showEpicModal = function(epic, childTickets) {
    const modal = document.getElementById('ticket-modal');
    const body = document.getElementById('modal-body');

    const completedTickets = childTickets.filter(t => t.status === 'Done').length;
    const progress = childTickets.length > 0 ? Math.round((completedTickets / childTickets.length) * 100) : 0;

    body.innerHTML = `
        <h2>${escapeHtml(epic.name || epic.key)}</h2>
        <div class="modal-field">
            <label class="modal-field-label">Epic Key</label>
            <div class="modal-field-value mono">${escapeHtml(epic.key)}</div>
        </div>
        <div class="modal-field">
            <label class="modal-field-label">Progress</label>
            <div class="modal-field-value">${completedTickets} / ${childTickets.length} completed (${progress}%)</div>
        </div>
        <h3>Child Tickets (${childTickets.length})</h3>
        <div style="margin-top: 12px; max-height: 400px; overflow-y: auto;">
            ${childTickets.map(ticket => `
                <div style="padding: 8px; margin-bottom: 8px; background: var(--color-bg-tertiary); border-radius: 4px; cursor: pointer;" onclick="APP.showTicketModal({${Object.entries(ticket).map(([k, v]) => `'${k}': '${String(v).replace(/'/g, "\\'")}'`).join(', ')}})">
                    <div style="font-weight: bold; color: var(--color-accent-blue); margin-bottom: 4px;">
                        ${escapeHtml(ticket.key)} - ${escapeHtml(ticket.summary)}
                    </div>
                    <div style="font-size: 12px; color: var(--color-text-muted);">
                        Status: ${escapeHtml(ticket.status)} | Type: ${escapeHtml(ticket.type)}
                    </div>
                </div>
            `).join('')}
        </div>
    `;

    modal.classList.remove('hidden');
};

// ============================================================================
// Tickets Table Rendering
// ============================================================================

/**
 * Render paginated tickets table
 */
function renderTicketsTable() {
    const tbody = document.getElementById('tickets-tbody');
    tbody.innerHTML = '';

    const sorted = [...APP.searchIndex].sort((a, b) => {
        let aVal = a[APP.sortColumn];
        let bVal = b[APP.sortColumn];

        if (typeof aVal === 'string') {
            aVal = aVal.toLowerCase();
            bVal = bVal.toLowerCase();
        }

        if (aVal < bVal) return APP.sortDirection === 'asc' ? -1 : 1;
        if (aVal > bVal) return APP.sortDirection === 'asc' ? 1 : -1;
        return 0;
    });

    const start = (APP.currentPage - 1) * APP.itemsPerPage;
    const end = start + APP.itemsPerPage;
    const pageTickets = sorted.slice(start, end);

    pageTickets.forEach(ticket => {
        const row = document.createElement('tr');
        row.style.cursor = 'pointer';
        row.innerHTML = `
            <td class="ticket-key">${escapeHtml(ticket.key)}</td>
            <td class="ticket-summary">${escapeHtml(ticket.summary)}</td>
            <td><span class="ticket-type">${escapeHtml(ticket.type)}</span></td>
            <td><span class="ticket-status ${getStatusClass(ticket.status)}">${escapeHtml(ticket.status)}</span></td>
            <td>${escapeHtml(ticket.assignee || 'Unassigned')}</td>
        `;
        row.addEventListener('click', () => APP.showTicketModal(ticket));
        tbody.appendChild(row);
    });

    updatePaginationInfo(sorted.length);
    updateSortIndicators();
}

/**
 * Update pagination info
 */
function updatePaginationInfo(totalItems) {
    const totalPages = Math.ceil(totalItems / APP.itemsPerPage);
    const info = document.getElementById('pagination-info');
    info.textContent = `Page ${APP.currentPage} of ${totalPages}`;

    document.getElementById('tickets-prev').disabled = APP.currentPage === 1;
    document.getElementById('tickets-next').disabled = APP.currentPage >= totalPages;
}

/**
 * Update sort indicators in table headers
 */
function updateSortIndicators() {
    document.querySelectorAll('.sort-btn').forEach(btn => {
        btn.classList.remove('active');
        if (btn.dataset.sort === APP.sortColumn) {
            btn.classList.add('active');
            const indicator = btn.querySelector('.sort-indicator');
            if (!indicator) {
                const span = document.createElement('span');
                span.className = 'sort-indicator';
                span.textContent = APP.sortDirection === 'asc' ? '▲' : '▼';
                btn.appendChild(span);
            } else {
                indicator.textContent = APP.sortDirection === 'asc' ? '▲' : '▼';
            }
        } else {
            const indicator = btn.querySelector('.sort-indicator');
            if (indicator) indicator.remove();
        }
    });
}

// ============================================================================
// Modal Functions
// ============================================================================

/**
 * Show ticket details modal
 */
APP.showTicketModal = function(ticket) {
    const modal = document.getElementById('ticket-modal');
    const body = document.getElementById('modal-body');

    const themes = APP.themeIndex[ticket.key] || [];

    body.innerHTML = `
        <h2>${escapeHtml(ticket.key)}</h2>
        <div style="margin-bottom: 16px;">
            <span class="badge ${getTypeBadgeClass(ticket.type)}">${escapeHtml(ticket.type)}</span>
            <span class="badge ${getStatusBadgeClass(ticket.status)}">${escapeHtml(ticket.status)}</span>
        </div>
        <h3>Summary</h3>
        <p>${escapeHtml(ticket.summary)}</p>
        <div class="modal-field">
            <label class="modal-field-label">Description</label>
            <div class="modal-field-value">${escapeHtml(ticket.description || 'No description')}</div>
        </div>
        <div class="modal-field">
            <label class="modal-field-label">Assignee</label>
            <div class="modal-field-value">${escapeHtml(ticket.assignee || 'Unassigned')}</div>
        </div>
        ${ticket.parent_epic ? `
        <div class="modal-field">
            <label class="modal-field-label">Parent Epic</label>
            <div class="modal-field-value mono">${escapeHtml(ticket.parent_epic)}</div>
        </div>
        ` : ''}
        ${themes.length > 0 ? `
        <div class="modal-field">
            <label class="modal-field-label">Themes</label>
            <div class="modal-field-value">${escapeHtml(themes.join(', '))}</div>
        </div>
        ` : ''}
        <div class="modal-field">
            <label class="modal-field-label">Created</label>
            <div class="modal-field-value">${escapeHtml(formatDate(ticket.created))}</div>
        </div>
        ${ticket.updated ? `
        <div class="modal-field">
            <label class="modal-field-label">Updated</label>
            <div class="modal-field-value">${escapeHtml(formatDate(ticket.updated))}</div>
        </div>
        ` : ''}
    `;

    modal.classList.remove('hidden');
};

/**
 * Close modal
 */
APP.closeModal = function() {
    const modal = document.getElementById('ticket-modal');
    modal.classList.add('hidden');
};

// ============================================================================
// Filter Functions
// ============================================================================

/**
 * Toggle filter state
 */
APP.toggleFilter = function(category, value) {
    const filters = APP.activeFilters[category];
    const index = filters.indexOf(value);

    if (index > -1) {
        filters.splice(index, 1);
    } else {
        filters.push(value);
    }

    performSearch(APP.searchQuery);
};

/**
 * Clear all filters
 */
APP.clearFilters = function() {
    APP.activeFilters = {
        type: [],
        status: [],
        theme: [],
        assignee: []
    };

    document.querySelectorAll('.filter-checkbox input[type="checkbox"]').forEach(input => {
        input.checked = false;
    });

    performSearch(APP.searchQuery);
};

// ============================================================================
// Tab Navigation
// ============================================================================

/**
 * Switch to tab
 */
APP.switchTab = function(tabName) {
    if (APP.currentTab === tabName) return;

    // Hide current tab
    const currentContent = document.getElementById(`${APP.currentTab}-tab`);
    if (currentContent) {
        currentContent.classList.remove('active');
    }

    // Update nav state
    document.querySelectorAll('.tab-link').forEach(link => {
        link.classList.remove('active');
    });
    document.querySelector(`[data-tab="${tabName}"]`).classList.add('active');

    // Show new tab
    APP.currentTab = tabName;
    const newContent = document.getElementById(`${tabName}-tab`);
    if (newContent) {
        newContent.classList.add('active');
    }

    // Update URL hash
    window.location.hash = tabName;
};

/**
 * Handle hash-based navigation
 */
function handleHashChange() {
    const hash = window.location.hash.slice(1) || 'dashboard';
    const validTabs = ['dashboard', 'search', 'epics', 'tickets'];

    if (validTabs.includes(hash)) {
        APP.switchTab(hash);
    }
}

// ============================================================================
// Event Listeners & Keyboard Shortcuts
// ============================================================================

/**
 * Setup global keyboard shortcuts
 */
function setupKeyboardShortcuts() {
    document.addEventListener('keydown', (e) => {
        // Cmd+K or Ctrl+K for search
        if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
            e.preventDefault();
            APP.switchTab('search');
            document.getElementById('header-search').focus();
        }

        // Escape to close modal
        if (e.key === 'Escape') {
            APP.closeModal();
        }
    });
}

/**
 * Setup event listeners
 */
function setupEventListeners() {
    // Tab links
    document.querySelectorAll('.tab-link').forEach(link => {
        link.addEventListener('click', (e) => {
            e.preventDefault();
            APP.switchTab(link.dataset.tab);
        });
    });

    // Search input with debounce
    const searchInput = document.getElementById('header-search');
    searchInput.addEventListener('input', debounce((e) => {
        performSearch(e.target.value);
    }, 300));

    // Clear filters button
    document.getElementById('clear-filters').addEventListener('click', APP.clearFilters);

    // Pagination
    document.getElementById('tickets-prev').addEventListener('click', () => {
        if (APP.currentPage > 1) {
            APP.currentPage--;
            renderTicketsTable();
            document.querySelector('.tickets-container').scrollIntoView({ behavior: 'smooth' });
        }
    });

    document.getElementById('tickets-next').addEventListener('click', () => {
        const totalPages = Math.ceil(APP.searchIndex.length / APP.itemsPerPage);
        if (APP.currentPage < totalPages) {
            APP.currentPage++;
            renderTicketsTable();
            document.querySelector('.tickets-container').scrollIntoView({ behavior: 'smooth' });
        }
    });

    // Sort buttons
    document.querySelectorAll('.sort-btn').forEach(btn => {
        btn.addEventListener('click', (e) => {
            e.preventDefault();
            const column = btn.dataset.sort;

            if (APP.sortColumn === column) {
                APP.sortDirection = APP.sortDirection === 'asc' ? 'desc' : 'asc';
            } else {
                APP.sortColumn = column;
                APP.sortDirection = 'asc';
            }

            APP.currentPage = 1;
            renderTicketsTable();
        });
    });

    // Hash change for browser back/forward
    window.addEventListener('hashchange', handleHashChange);
}

// ============================================================================
// Initialization
// ============================================================================

/**
 * Initialize application
 */
async function initializeApp() {
    const loadingOverlay = document.getElementById('loading-overlay');
    const errorContainer = document.getElementById('error-container');
    const errorMessage = document.getElementById('error-message');

    try {
        // Load stats first for quick dashboard display
        console.log('Loading stats...');
        const stats = await loadStats();

        // Show dashboard skeleton while loading other data
        renderDashboard(stats);
        renderCharts(stats);

        // Load all data in parallel
        console.log('Loading all data...');
        await Promise.all([
            loadSearchIndex(),
            loadEpics(),
            loadThemes()
        ]);

        // Initialize search
        initializeFuse();

        // Render all tabs
        renderFilterOptions();
        renderEpics();
        renderTicketsTable();

        // Setup event listeners
        setupEventListeners();
        setupKeyboardShortcuts();

        // Handle initial hash
        handleHashChange();

        APP.initialized = true;
        loadingOverlay.classList.add('hidden');

        console.log('LAP Intelligence Hub v2 initialized successfully');
    } catch (error) {
        console.error('Failed to initialize app:', error);
        loadingOverlay.classList.add('hidden');
        errorContainer.classList.remove('hidden');
        errorMessage.textContent = `Failed to load: ${error.message}. Please check that all data files are available in the data/ directory.`;
    }
}

// ============================================================================
// Configure Chart.js theme
// ============================================================================

function configureChartTheme() {
    Chart.defaults.color = '#9fa8da';
    Chart.defaults.borderColor = '#2a3075';
    Chart.defaults.plugins.legend.labels.color = '#e8eaf6';
    Chart.defaults.font.family = '-apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Oxygen, Ubuntu, Cantarell, sans-serif';
}

// ============================================================================
// Start application when DOM is ready
// ============================================================================

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        configureChartTheme();
        initializeApp();
    });
} else {
    configureChartTheme();
    initializeApp();
}
