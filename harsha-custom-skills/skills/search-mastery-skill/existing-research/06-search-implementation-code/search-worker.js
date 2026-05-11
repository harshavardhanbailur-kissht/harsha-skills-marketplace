/**
 * Search Worker
 *
 * Web Worker for non-blocking search operations on large documentation datasets.
 * This worker handles autocomplete and full-text search, returning results to the main thread.
 *
 * Usage in main thread:
 *   const worker = new Worker('search-worker.js');
 *   worker.postMessage({
 *     type: 'autocomplete',
 *     query: 'useState',
 *     data: documentationArray,
 *     maxSuggestions: 8
 *   });
 *   worker.onmessage = (event) => {
 *     console.log(event.data.suggestions);
 *   };
 */

/**
 * Calculate Levenshtein distance for fuzzy matching
 * @private
 */
function levenshteinDistance(str1, str2) {
  const m = str1.length;
  const n = str2.length;
  const dp = Array(m + 1)
    .fill(null)
    .map(() => Array(n + 1).fill(0));

  for (let i = 0; i <= m; i++) dp[i][0] = i;
  for (let j = 0; j <= n; j++) dp[0][j] = j;

  for (let i = 1; i <= m; i++) {
    for (let j = 1; j <= n; j++) {
      if (str1[i - 1] === str2[j - 1]) {
        dp[i][j] = dp[i - 1][j - 1];
      } else {
        dp[i][j] = 1 + Math.min(dp[i - 1][j], dp[i][j - 1], dp[i - 1][j - 1]);
      }
    }
  }

  return dp[m][n];
}

/**
 * Calculate relevance score for a document
 * @private
 */
function calculateRelevance(item, query, activeTab) {
  if (!query) return 0;

  const q = query.toLowerCase();
  const title = item.title.toLowerCase();
  const content = item.content.toLowerCase();
  let score = 0;

  // Title matching (highest priority)
  if (title === q) {
    score += 10;
  } else if (title.startsWith(q)) {
    score += 8;
  } else if (title.includes(q)) {
    score += 6;
  }

  // Content matching
  if (content.includes(q)) {
    const occurrences = (content.match(new RegExp(q, 'g')) || []).length;
    score += 3 * Math.min(occurrences, 5); // Cap at 5 occurrences
  }

  // Type/tab boost
  if (activeTab && item.type === activeTab && activeTab !== 'all') {
    score += 2;
  }

  // Fuzzy matching for typos (only if no exact matches found)
  if (score === 0 && q.length > 2) {
    const distance = levenshteinDistance(title, q);
    const maxDistance = Math.max(title.length, q.length) / 2;
    if (distance <= maxDistance) {
      score = (1 - distance / maxDistance) * 4;
    }
  }

  // Apply confidence multiplier
  const confidence = item.confidence || 0.5;
  score *= confidence;

  return Math.max(0, score);
}

/**
 * Extract TF-IDF term frequency
 * @private
 */
function calculateTermFrequency(text, term) {
  if (!text || !term) return 0;
  const regex = new RegExp(`\\b${term}\\b`, 'gi');
  const matches = text.match(regex) || [];
  return matches.length / (text.split(/\s+/).length || 1);
}

/**
 * Perform autocomplete search
 * Returns scored suggestions grouped by type
 * @private
 */
function performAutocomplete(query, data, maxSuggestions, activeTab = 'all') {
  if (!query.trim()) {
    return [];
  }

  const scored = data
    .map((item) => ({
      ...item,
      score: calculateRelevance(item, query, activeTab),
    }))
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, maxSuggestions);

  return scored;
}

/**
 * Perform full-text search with filtering and sorting
 * @private
 */
function performFullSearch(query, data, filters, sortBy, maxResults, activeTab) {
  if (!query.trim()) {
    return [];
  }

  // Score all items
  let results = data
    .map((item) => ({
      ...item,
      score: calculateRelevance(item, query, activeTab),
    }))
    .filter((item) => item.score > 0);

  // Apply type filter
  if (filters.type && filters.type.length > 0) {
    results = results.filter((item) => filters.type.includes(item.type));
  }

  // Apply module filter
  if (filters.module && filters.module.length > 0) {
    results = results.filter((item) => filters.module.includes(item.module));
  }

  // Apply confidence filter
  if (filters.confidence && filters.confidence > 0) {
    results = results.filter(
      (item) => (item.confidence || 0.5) >= filters.confidence
    );
  }

  // Sort results
  results.sort((a, b) => {
    switch (sortBy) {
      case 'newest':
        return (b.updatedAt || 0) - (a.updatedAt || 0);
      case 'confidence':
        return (b.confidence || 0) - (a.confidence || 0);
      case 'relevance':
      default:
        return b.score - a.score;
    }
  });

  return results.slice(0, maxResults);
}

/**
 * Main worker message handler
 */
self.onmessage = function (event) {
  const { type, query, data, maxSuggestions, maxResults, filters, sortBy, activeTab } = event.data;

  try {
    let results = null;
    let suggestions = null;

    if (type === 'autocomplete') {
      suggestions = performAutocomplete(query, data, maxSuggestions, activeTab);
    } else if (type === 'search') {
      results = performFullSearch(query, data, filters, sortBy, maxResults, activeTab);
    }

    // Send results back to main thread
    self.postMessage({
      suggestions,
      results,
      success: true,
    });
  } catch (error) {
    // Send error back to main thread
    self.postMessage({
      error: error.message,
      success: false,
    });
  }
};

/**
 * Export for testing (if using a bundler like Jest)
 */
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    calculateRelevance,
    performAutocomplete,
    performFullSearch,
    levenshteinDistance,
    calculateTermFrequency,
  };
}
