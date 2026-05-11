/**
 * CodeDocSearchEngine - Production-grade documentation search
 *
 * Features:
 * - BM25F field-weighted scoring: title (10), headings (5), code (3), body (1)
 * - Fuzzy matching using Bitap algorithm (Fuse.js-style, threshold 0.3)
 * - Code-aware tokenization via CodeTokenizer
 * - Confidence boosting: VERIFIED=1.0, HIGH=0.8, MEDIUM=0.5, LOW=0.2
 * - Result categorization by doc_type (reference, tutorial, howto, explanation)
 * - Faceted search and autocomplete suggestions
 *
 * BM25F is a variant of Okapi BM25 that handles multiple fields with different weights.
 * It's particularly effective for documentation search because it naturally boosts
 * matches in titles and headings while still finding relevant content in body text.
 */

import CodeTokenizer from './code-tokenizer.js';

export class CodeDocSearchEngine {
  constructor(options = {}) {
    // BM25 parameters
    this.k1 = options.k1 ?? 1.5;          // Controls term frequency saturation
    this.b = options.b ?? 0.75;           // Controls field length normalization
    this.avgFieldLengths = {};            // Will store average lengths per field

    // Field weights for BM25F
    this.fieldWeights = {
      title: options.titleWeight ?? 10,
      headings: options.headingsWeight ?? 5,
      code_symbols: options.codeWeight ?? 3,
      description: options.descriptionWeight ?? 2,
      keywords: options.keywordsWeight ?? 4,
      body: options.bodyWeight ?? 1,
      module: options.moduleWeight ?? 2
    };

    // Fuzzy matching configuration
    this.fuzzyThreshold = options.fuzzyThreshold ?? 0.3;
    this.fuzzyMaxDistance = options.fuzzyMaxDistance ?? 6;

    // Confidence multipliers
    this.confidenceMultipliers = {
      'VERIFIED': 1.0,
      'HIGH': 0.8,
      'MEDIUM': 0.5,
      'LOW': 0.2
    };

    // Initialize data structures
    this.documents = new Map();           // id -> document
    this.invertedIndex = new Map();       // token -> Set of doc ids
    this.termFrequencies = new Map();     // token -> {docId -> {field -> count}}
    this.tokenizer = new CodeTokenizer(options.tokenizerOptions);

    // Metadata
    this.docTypeFilters = new Set();
    this.moduleFilters = new Set();
    this.totalDocs = 0;

    // Cache for performance
    this.suggestionsCache = new Map();
  }

  /**
   * Add a document to the index
   * @param {Object} doc - Document with: id, title, description, module, doc_type,
   *                       confidence, keywords, code_symbols, body, headings, url
   */
  addDocument(doc) {
    if (!doc.id) throw new Error('Document must have an id');

    this.documents.set(doc.id, doc);
    this.totalDocs++;

    // Track facets
    if (doc.doc_type) this.docTypeFilters.add(doc.doc_type);
    if (doc.module) this.moduleFilters.add(doc.module);

    // Index all text fields
    const fieldsToIndex = {
      title: doc.title || '',
      description: doc.description || '',
      module: doc.module || '',
      headings: (doc.headings || []).join(' '),
      code_symbols: (doc.code_symbols || []).join(' '),
      body: doc.body || '',
      keywords: (doc.keywords || []).join(' ')
    };

    // Build inverted index and calculate term frequencies
    for (const [field, text] of Object.entries(fieldsToIndex)) {
      if (!text) continue;

      const tokens = this.tokenizer.tokenize(text);

      for (const token of tokens) {
        // Add to inverted index
        if (!this.invertedIndex.has(token)) {
          this.invertedIndex.set(token, new Set());
        }
        this.invertedIndex.get(token).add(doc.id);

        // Track term frequencies per field
        const tfKey = `${token}:${doc.id}:${field}`;
        if (!this.termFrequencies.has(tfKey)) {
          this.termFrequencies.set(tfKey, 0);
        }
        this.termFrequencies.set(tfKey, this.termFrequencies.get(tfKey) + 1);

        // Track average field lengths
        if (!this.avgFieldLengths[field]) {
          this.avgFieldLengths[field] = { sum: 0, count: 0 };
        }
        this.avgFieldLengths[field].sum += tokens.length;
        this.avgFieldLengths[field].count++;
      }
    }
  }

  /**
   * Load a pre-built index from JSON
   * Useful for pre-indexing and fast initialization
   */
  loadIndex(indexData) {
    if (!indexData.documents || !indexData.invertedIndex) {
      throw new Error('Invalid index data format');
    }

    // Restore documents
    for (const doc of indexData.documents) {
      this.documents.set(doc.id, doc);
      if (doc.doc_type) this.docTypeFilters.add(doc.doc_type);
      if (doc.module) this.moduleFilters.add(doc.module);
    }

    // Restore inverted index
    for (const [token, docIds] of Object.entries(indexData.invertedIndex)) {
      this.invertedIndex.set(token, new Set(docIds));
    }

    // Restore term frequencies
    for (const [key, count] of Object.entries(indexData.termFrequencies)) {
      this.termFrequencies.set(key, count);
    }

    // Restore average field lengths
    this.avgFieldLengths = indexData.avgFieldLengths || {};
    this.totalDocs = this.documents.size;
  }

  /**
   * Export index to JSON for persistence
   */
  exportIndex() {
    return {
      documents: Array.from(this.documents.values()),
      invertedIndex: Object.fromEntries(
        Array.from(this.invertedIndex.entries()).map(([token, docIds]) => [
          token,
          Array.from(docIds)
        ])
      ),
      termFrequencies: Object.fromEntries(this.termFrequencies),
      avgFieldLengths: this.avgFieldLengths,
      version: '1.0'
    };
  }

  /**
   * Core search method using BM25F scoring
   * @param {string} query - Search query
   * @param {Object} options - Search options (filters, limit, etc.)
   * @returns {Array} - Ranked results with scores
   */
  search(query, options = {}) {
    const {
      limit = 20,
      docTypeFilter = null,
      moduleFilter = null,
      boostRecency = false,
      minScore = 0
    } = options;

    if (!query || typeof query !== 'string') return [];

    const queryTokens = this.tokenizer.tokenizeQuery(query);
    const scores = new Map(); // docId -> score

    // BM25F scoring
    for (const token of queryTokens) {
      const docIds = this.invertedIndex.get(token) || new Set();

      if (docIds.size === 0) {
        // Try fuzzy matching for this token
        const fuzzyMatches = this._fuzzyMatchToken(token);
        for (const fuzzyToken of fuzzyMatches) {
          const fuzzyDocIds = this.invertedIndex.get(fuzzyToken) || new Set();
          for (const docId of fuzzyDocIds) {
            this._updateScore(scores, docId, token, 0.5); // Fuzzy hits get 50% weight
          }
        }
      } else {
        for (const docId of docIds) {
          this._updateScore(scores, docId, token, 1.0);
        }
      }
    }

    // Convert to results array and apply filters
    let results = Array.from(scores.entries()).map(([docId, score]) => {
      const doc = this.documents.get(docId);
      return {
        id: doc.id,
        title: doc.title,
        description: doc.description,
        module: doc.module,
        doc_type: doc.doc_type,
        url: doc.url,
        score: score,
        confidence: doc.confidence,
        confidence_multiplier: this.confidenceMultipliers[doc.confidence] ?? 0.5,
        final_score: score * (this.confidenceMultipliers[doc.confidence] ?? 0.5)
      };
    });

    // Apply filters
    if (docTypeFilter) {
      results = results.filter(r => r.doc_type === docTypeFilter);
    }
    if (moduleFilter) {
      results = results.filter(r => r.module === moduleFilter);
    }

    // Filter by minimum score
    results = results.filter(r => r.final_score >= minScore);

    // Sort by final score
    results.sort((a, b) => b.final_score - a.final_score);

    // Optional: boost recent documents (if timestamp available)
    if (boostRecency && results[0]) {
      const now = Date.now();
      results = results.map(r => ({
        ...r,
        recency_boost: this.documents.get(r.id).updated_at ?
          1 + (1 - Math.min((now - this.documents.get(r.id).updated_at) / (90 * 24 * 60 * 60 * 1000), 1)) * 0.1 :
          1,
        final_score: (this.documents.get(r.id).updated_at ?
          1 + (1 - Math.min((now - this.documents.get(r.id).updated_at) / (90 * 24 * 60 * 60 * 1000), 1)) * 0.1 :
          1) * r.final_score
      }));
      results.sort((a, b) => b.final_score - a.final_score);
    }

    return results.slice(0, limit);
  }

  /**
   * Calculate and update BM25F score for a document
   * @private
   */
  _updateScore(scores, docId, token, matchQuality = 1.0) {
    if (!scores.has(docId)) {
      scores.set(docId, 0);
    }

    let fieldScore = 0;

    // Calculate score contribution from each field
    for (const [field, weight] of Object.entries(this.fieldWeights)) {
      const tfKey = `${token}:${docId}:${field}`;
      const tf = this.termFrequencies.get(tfKey) || 0;

      if (tf === 0) continue;

      // Inverse document frequency
      const docFreq = this.invertedIndex.get(token)?.size || 1;
      const idf = Math.log((this.totalDocs - docFreq + 0.5) / (docFreq + 0.5) + 1);

      // Field length normalization
      const avgLen = this.avgFieldLengths[field]?.sum /
                     (this.avgFieldLengths[field]?.count || 1) || 1;
      const fieldLength = this._getFieldLength(this.documents.get(docId), field);

      // BM25 formula
      const numerator = tf * (this.k1 + 1);
      const denominator = tf + this.k1 * (1 - this.b + this.b * (fieldLength / avgLen));
      const bm25Score = idf * (numerator / denominator);

      fieldScore += weight * bm25Score;
    }

    // Apply match quality (for fuzzy matches)
    scores.set(docId, scores.get(docId) + (fieldScore * matchQuality));
  }

  /**
   * Get the length of a field in a document
   * @private
   */
  _getFieldLength(doc, field) {
    switch (field) {
      case 'title':
        return this.tokenizer.tokenize(doc.title || '').length;
      case 'description':
        return this.tokenizer.tokenize(doc.description || '').length;
      case 'body':
        return this.tokenizer.tokenize(doc.body || '').length;
      case 'module':
        return this.tokenizer.tokenize(doc.module || '').length;
      case 'headings':
        return this.tokenizer.tokenize((doc.headings || []).join(' ')).length;
      case 'code_symbols':
        return (doc.code_symbols || []).length;
      case 'keywords':
        return (doc.keywords || []).length;
      default:
        return 0;
    }
  }

  /**
   * Find tokens similar to the query token using Bitap algorithm
   * @private
   */
  _fuzzyMatchToken(token) {
    const matches = [];
    const maxDistance = Math.max(1, Math.floor(token.length * (1 - this.fuzzyThreshold)));

    for (const indexedToken of this.invertedIndex.keys()) {
      const distance = this._calculateBitapDistance(token, indexedToken);
      if (distance <= maxDistance) {
        matches.push(indexedToken);
      }
    }

    return matches;
  }

  /**
   * Calculate Bitap edit distance (simplified Levenshtein variant)
   * Used for fuzzy matching in autocomplete and search
   * @private
   */
  _calculateBitapDistance(a, b) {
    const maxLen = Math.max(a.length, b.length);
    const minLen = Math.min(a.length, b.length);

    let distance = Math.abs(a.length - b.length);

    for (let i = 0; i < minLen; i++) {
      if (a[i] !== b[i]) distance++;
    }

    return distance;
  }

  /**
   * Get autocomplete suggestions for a prefix
   * @param {string} prefix - Prefix to complete
   * @param {number} limit - Maximum suggestions to return
   * @returns {Array} - Suggestions with frequency info
   */
  suggest(prefix, limit = 10) {
    if (!prefix || prefix.length < 2) return [];

    const cacheKey = prefix;
    if (this.suggestionsCache.has(cacheKey)) {
      return this.suggestionsCache.get(cacheKey).slice(0, limit);
    }

    const suggestions = new Map(); // token -> frequency

    // Find all tokens that start with prefix
    for (const token of this.invertedIndex.keys()) {
      if (token.startsWith(prefix.toLowerCase())) {
        const freq = this.invertedIndex.get(token).size;
        suggestions.set(token, freq);
      }
    }

    // Also include fuzzy matches
    const fuzzyMatches = this._fuzzyMatchToken(prefix);
    for (const token of fuzzyMatches) {
      if (!suggestions.has(token)) {
        suggestions.set(token, this.invertedIndex.get(token).size);
      }
    }

    // Sort by frequency (descending) then alphabetically
    const result = Array.from(suggestions.entries())
      .sort((a, b) => {
        if (b[1] !== a[1]) return b[1] - a[1]; // Frequency first
        return a[0].localeCompare(b[0]); // Then alphabetical
      })
      .slice(0, limit)
      .map(([token, freq]) => ({ token, frequency: freq }));

    // Cache for future requests
    this.suggestionsCache.set(cacheKey, result);

    return result;
  }

  /**
   * Get available filter options
   * @returns {Object} - Available facet values
   */
  getFilters() {
    return {
      doc_types: Array.from(this.docTypeFilters).sort(),
      modules: Array.from(this.moduleFilters).sort(),
      confidences: ['VERIFIED', 'HIGH', 'MEDIUM', 'LOW']
    };
  }

  /**
   * Get index statistics (useful for debugging and monitoring)
   */
  getStats() {
    return {
      total_documents: this.totalDocs,
      total_tokens: this.invertedIndex.size,
      doc_types: Array.from(this.docTypeFilters),
      modules: Array.from(this.moduleFilters),
      avg_docs_per_token: this.totalDocs > 0 ?
        Array.from(this.invertedIndex.values())
          .reduce((sum, set) => sum + set.size, 0) / this.invertedIndex.size :
        0,
      field_lengths: Object.entries(this.avgFieldLengths).reduce((acc, [field, data]) => {
        acc[field] = data.count > 0 ? data.sum / data.count : 0;
        return acc;
      }, {})
    };
  }

  /**
   * Clear the index
   */
  clear() {
    this.documents.clear();
    this.invertedIndex.clear();
    this.termFrequencies.clear();
    this.avgFieldLengths = {};
    this.docTypeFilters.clear();
    this.moduleFilters.clear();
    this.totalDocs = 0;
    this.suggestionsCache.clear();
  }
}

export default CodeDocSearchEngine;
