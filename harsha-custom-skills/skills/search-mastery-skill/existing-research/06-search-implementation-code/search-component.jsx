import React, { useState, useEffect, useRef, useCallback, useMemo } from 'react';

/**
 * SearchComponent - Production-quality documentation search UI
 *
 * A comprehensive search component with autocomplete, full-text search,
 * faceted filtering, and keyboard navigation. Uses Web Workers for
 * non-blocking search operations.
 *
 * @component
 * @example
 * <SearchComponent
 *   searchData={documentationIndex}
 *   onResultSelect={(result) => navigate(result.url)}
 *   onSearch={(query) => console.log('Search:', query)}
 * />
 *
 * @param {Object} props - Component props
 * @param {Array<Object>} props.searchData - Array of searchable items
 * @param {string} props.searchData[].id - Unique identifier
 * @param {string} props.searchData[].title - Display title
 * @param {string} props.searchData[].content - Full searchable content
 * @param {string} props.searchData[].type - Item type: 'function', 'module', 'guide', 'concept'
 * @param {string} props.searchData[].module - Module breadcrumb path
 * @param {string} props.searchData[].url - Navigation URL
 * @param {number} [props.searchData[].confidence=0.5] - Confidence score 0-1
 * @param {Function} [props.onResultSelect] - Callback when user selects a result
 * @param {Function} [props.onSearch] - Callback when search query changes
 * @param {string} [props.placeholder="Search documentation..."] - Placeholder text
 * @param {boolean} [props.darkMode=false] - Enable dark mode styling
 * @param {number} [props.debounceMs=200] - Debounce delay for autocomplete
 * @param {number} [props.maxSuggestions=8] - Max autocomplete suggestions shown
 * @param {number} [props.maxResults=50] - Max search results per page
 * @param {string} [props.workerPath] - Path to search-worker.js for Web Worker
 *
 * @returns {React.ReactElement} The search component
 */
function SearchComponent({
  searchData = [],
  onResultSelect = () => {},
  onSearch = () => {},
  placeholder = 'Search documentation...',
  darkMode = false,
  debounceMs = 200,
  maxSuggestions = 8,
  maxResults = 50,
  workerPath = null,
}) {
  // State management
  const [query, setQuery] = useState('');
  const [suggestions, setSuggestions] = useState([]);
  const [results, setResults] = useState([]);
  const [showSuggestions, setShowSuggestions] = useState(false);
  const [showResults, setShowResults] = useState(false);
  const [selectedSuggestionIndex, setSelectedSuggestionIndex] = useState(-1);
  const [isLoading, setIsLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('all');
  const [recentSearches, setRecentSearches] = useState([]);
  const [selectedFilter, setSelectedFilter] = useState({
    type: [],
    module: [],
    confidence: 0,
  });
  const [sortBy, setSortBy] = useState('relevance');
  const [currentPage, setCurrentPage] = useState(1);

  // Refs
  const inputRef = useRef(null);
  const suggestionsRef = useRef(null);
  const debounceTimerRef = useRef(null);
  const workerRef = useRef(null);
  const resultsContainerRef = useRef(null);

  // Initialize Web Worker
  useEffect(() => {
    if (!workerPath) return;

    try {
      workerRef.current = new Worker(workerPath);
      workerRef.current.onmessage = (event) => {
        const { suggestions: workerSuggestions, results: workerResults } = event.data;
        if (workerSuggestions) setSuggestions(workerSuggestions);
        if (workerResults) setResults(workerResults);
        setIsLoading(false);
      };
    } catch (error) {
      console.warn('Web Worker failed, falling back to main thread:', error);
      workerRef.current = null;
    }

    return () => {
      if (workerRef.current) {
        workerRef.current.terminate();
      }
    };
  }, [workerPath]);

  // Keyboard shortcut (Cmd/Ctrl+K to focus)
  useEffect(() => {
    const handleKeyDown = (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        inputRef.current?.focus();
      }
    };

    window.addEventListener('keydown', handleKeyDown);
    return () => window.removeEventListener('keydown', handleKeyDown);
  }, []);

  /**
   * Calculate relevance score for a search result
   * @private
   */
  const calculateRelevance = useCallback((item, searchQuery) => {
    if (!searchQuery) return 0;

    const query = searchQuery.toLowerCase();
    let score = 0;

    // Exact title match: highest priority
    if (item.title.toLowerCase() === query) {
      score += 10;
    } else if (item.title.toLowerCase().startsWith(query)) {
      score += 8;
    } else if (item.title.toLowerCase().includes(query)) {
      score += 6;
    }

    // Content match
    if (item.content.toLowerCase().includes(query)) {
      score += 3;
    }

    // Module/type boost
    if (item.type === activeTab && activeTab !== 'all') {
      score += 2;
    }

    // Confidence multiplier
    score *= (item.confidence || 0.5);

    return Math.max(0, score);
  }, [activeTab]);

  /**
   * Generate fuzzy suggestions for typos
   * @private
   */
  const generateFuzzySuggestions = useCallback((query) => {
    if (query.length < 2) return [];

    return searchData
      .filter((item) => {
        const title = item.title.toLowerCase();
        const q = query.toLowerCase();
        // Simple fuzzy: check if characters appear in order
        let j = 0;
        for (let i = 0; i < title.length && j < q.length; i++) {
          if (title[i] === q[j]) j++;
        }
        return j === q.length && j > 0;
      })
      .slice(0, 3);
  }, [searchData]);

  /**
   * Group suggestions by type
   * @private
   */
  const groupedSuggestions = useMemo(() => {
    const groups = {
      function: [],
      module: [],
      guide: [],
      concept: [],
    };

    suggestions.forEach((item) => {
      const type = item.type || 'concept';
      if (groups[type] && groups[type].length < maxSuggestions / 4) {
        groups[type].push(item);
      }
    });

    return groups;
  }, [suggestions, maxSuggestions]);

  /**
   * Perform autocomplete search (debounced)
   * @private
   */
  const performAutocomplete = useCallback(
    (searchQuery) => {
      if (!searchQuery.trim()) {
        setSuggestions([]);
        setShowSuggestions(false);
        return;
      }

      setIsLoading(true);

      if (workerRef.current) {
        // Use Web Worker
        workerRef.current.postMessage({
          type: 'autocomplete',
          query: searchQuery,
          data: searchData,
          maxSuggestions,
          activeTab,
        });
      } else {
        // Fallback to main thread
        const scored = searchData
          .map((item) => ({
            ...item,
            score: calculateRelevance(item, searchQuery),
          }))
          .filter((item) => item.score > 0)
          .sort((a, b) => b.score - a.score)
          .slice(0, maxSuggestions);

        setSuggestions(scored);
        setIsLoading(false);
      }

      setShowSuggestions(true);
      setSelectedSuggestionIndex(-1);
    },
    [searchData, maxSuggestions, calculateRelevance, activeTab]
  );

  /**
   * Handle input change with debouncing
   * @private
   */
  const handleInputChange = useCallback((e) => {
    const value = e.target.value;
    setQuery(value);
    onSearch(value);

    // Clear previous debounce timer
    if (debounceTimerRef.current) {
      clearTimeout(debounceTimerRef.current);
    }

    // Set new debounce timer
    debounceTimerRef.current = setTimeout(() => {
      performAutocomplete(value);
    }, debounceMs);
  }, [debounceMs, performAutocomplete, onSearch]);

  /**
   * Perform full search with filtering and sorting
   * @private
   */
  const performFullSearch = useCallback(() => {
    if (!query.trim()) {
      setResults([]);
      return;
    }

    setIsLoading(true);
    setCurrentPage(1);

    if (workerRef.current) {
      // Use Web Worker
      workerRef.current.postMessage({
        type: 'search',
        query,
        data: searchData,
        filters: selectedFilter,
        sortBy,
        maxResults,
        activeTab,
      });
    } else {
      // Fallback to main thread
      let filtered = searchData
        .map((item) => ({
          ...item,
          score: calculateRelevance(item, query),
        }))
        .filter((item) => item.score > 0);

      // Apply filters
      if (selectedFilter.type.length > 0) {
        filtered = filtered.filter((item) =>
          selectedFilter.type.includes(item.type)
        );
      }

      if (selectedFilter.module.length > 0) {
        filtered = filtered.filter((item) =>
          selectedFilter.module.includes(item.module)
        );
      }

      if (selectedFilter.confidence > 0) {
        filtered = filtered.filter(
          (item) => (item.confidence || 0.5) >= selectedFilter.confidence
        );
      }

      // Apply sorting
      filtered.sort((a, b) => {
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

      setResults(filtered.slice(0, maxResults));
      setIsLoading(false);
    }

    setShowResults(true);
    setShowSuggestions(false);
  }, [
    query,
    searchData,
    selectedFilter,
    sortBy,
    maxResults,
    calculateRelevance,
    activeTab,
  ]);

  /**
   * Handle Enter key to perform full search
   * @private
   */
  const handleKeyDown = useCallback(
    (e) => {
      if (e.key === 'Escape') {
        setShowSuggestions(false);
        setShowResults(false);
        return;
      }

      if (!showSuggestions && !showResults) return;

      if (showSuggestions && suggestions.length > 0) {
        if (e.key === 'ArrowDown') {
          e.preventDefault();
          setSelectedSuggestionIndex((prev) =>
            prev < suggestions.length - 1 ? prev + 1 : 0
          );
        } else if (e.key === 'ArrowUp') {
          e.preventDefault();
          setSelectedSuggestionIndex((prev) =>
            prev > 0 ? prev - 1 : suggestions.length - 1
          );
        } else if (e.key === 'Enter') {
          e.preventDefault();
          if (selectedSuggestionIndex >= 0) {
            handleSuggestionSelect(suggestions[selectedSuggestionIndex]);
          } else {
            performFullSearch();
          }
        }
      } else if (e.key === 'Enter') {
        e.preventDefault();
        performFullSearch();
      }
    },
    [suggestions, selectedSuggestionIndex, showSuggestions, showResults, performFullSearch]
  );

  /**
   * Handle suggestion selection
   * @private
   */
  const handleSuggestionSelect = useCallback(
    (suggestion) => {
      setQuery(suggestion.title);
      setShowSuggestions(false);
      addRecentSearch(suggestion.title);
      onResultSelect(suggestion);
    },
    [onResultSelect]
  );

  /**
   * Handle result selection
   * @private
   */
  const handleResultSelect = useCallback(
    (result) => {
      addRecentSearch(query);
      onResultSelect(result);
    },
    [query, onResultSelect]
  );

  /**
   * Add to recent searches
   * @private
   */
  const addRecentSearch = useCallback((searchQuery) => {
    if (!searchQuery.trim()) return;

    setRecentSearches((prev) => {
      const filtered = prev.filter((s) => s !== searchQuery);
      return [searchQuery, ...filtered].slice(0, 5);
    });
  }, []);

  /**
   * Clear recent searches
   * @private
   */
  const clearRecentSearches = useCallback(() => {
    setRecentSearches([]);
  }, []);

  /**
   * Get icon for result type
   * @private
   */
  const getTypeIcon = (type) => {
    const icons = {
      function: '𝒇',
      module: '◇',
      guide: '📖',
      concept: '💡',
    };
    return icons[type] || '●';
  };

  /**
   * Highlight search query in text
   * @private
   */
  const highlightMatch = (text, query) => {
    if (!text || !query) return text;

    const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
    return text.replace(regex, '<mark style="background-color: yellow; font-weight: bold;">$1</mark>');
  };

  /**
   * Extract excerpt around match
   * @private
   */
  const getExcerpt = (content, query, maxLength = 150) => {
    if (!query || !content) return content?.substring(0, maxLength) || '';

    const index = content.toLowerCase().indexOf(query.toLowerCase());
    if (index === -1) return content.substring(0, maxLength);

    const start = Math.max(0, index - 50);
    const end = Math.min(content.length, index + query.length + 50);

    let excerpt = content.substring(start, end);
    if (start > 0) excerpt = '...' + excerpt;
    if (end < content.length) excerpt = excerpt + '...';

    return excerpt;
  };

  const bgClass = darkMode ? 'bg-gray-900 text-white' : 'bg-white text-gray-900';
  const borderClass = darkMode ? 'border-gray-700' : 'border-gray-300';
  const hoverClass = darkMode ? 'hover:bg-gray-800' : 'hover:bg-gray-50';
  const inputBgClass = darkMode ? 'bg-gray-800 border-gray-600' : 'bg-gray-50 border-gray-300';

  return (
    <div className={`w-full max-w-2xl mx-auto ${bgClass}`}>
      {/* Search Box */}
      <div className="relative">
        <div
          className={`flex items-center gap-2 px-4 py-3 border-2 ${inputBgClass} rounded-lg focus-within:border-blue-500 transition-colors`}
        >
          <span className="text-gray-400 text-lg">🔍</span>
          <input
            ref={inputRef}
            type="text"
            value={query}
            onChange={handleInputChange}
            onKeyDown={handleKeyDown}
            onFocus={() => {
              if (query) setShowSuggestions(true);
              if (recentSearches.length > 0 && !query) setShowSuggestions(true);
            }}
            placeholder={placeholder}
            aria-label="Search documentation"
            aria-autocomplete="list"
            aria-controls="suggestions"
            aria-expanded={showSuggestions}
            className={`flex-1 outline-none ${inputBgClass} text-sm font-medium`}
          />
          {query && (
            <button
              onClick={() => {
                setQuery('');
                setSuggestions([]);
                setResults([]);
                setShowSuggestions(false);
                setShowResults(false);
                inputRef.current?.focus();
              }}
              aria-label="Clear search"
              className="text-gray-400 hover:text-gray-600 transition-colors"
            >
              ✕
            </button>
          )}
          <span className="text-xs px-2 py-1 bg-gray-300 rounded text-gray-700 font-mono">
            {navigator.platform.includes('Mac') ? '⌘' : 'Ctrl'}K
          </span>
        </div>

        {/* Suggestions Dropdown */}
        {showSuggestions && (suggestions.length > 0 || query) && (
          <div
            ref={suggestionsRef}
            id="suggestions"
            className={`absolute top-full left-0 right-0 mt-2 border ${borderClass} rounded-lg shadow-lg z-50 max-h-96 overflow-y-auto ${bgClass}`}
            role="listbox"
            aria-label="Search suggestions"
          >
            {query && suggestions.length === 0 && recentSearches.length === 0 && (
              <div className="px-4 py-3 text-sm text-gray-500">
                No suggestions found
              </div>
            )}

            {!query && recentSearches.length > 0 && (
              <div>
                <div className="px-4 py-2 text-xs font-semibold text-gray-600 uppercase tracking-wide">
                  Recent Searches
                </div>
                {recentSearches.map((search, idx) => (
                  <button
                    key={idx}
                    onClick={() => {
                      setQuery(search);
                      performAutocomplete(search);
                    }}
                    className={`w-full text-left px-4 py-2 text-sm ${hoverClass} transition-colors`}
                  >
                    🕐 {search}
                  </button>
                ))}
                <button
                  onClick={clearRecentSearches}
                  className="w-full text-left px-4 py-2 text-xs text-gray-500 hover:text-gray-700 border-t"
                >
                  Clear recent searches
                </button>
              </div>
            )}

            {query && suggestions.length > 0 && (
              <>
                {/* Functions */}
                {groupedSuggestions.function.length > 0 && (
                  <div>
                    <div className="px-4 py-2 text-xs font-semibold text-gray-600 uppercase tracking-wide">
                      Functions
                    </div>
                    {groupedSuggestions.function.map((item, idx) => (
                      <button
                        key={item.id}
                        onClick={() => handleSuggestionSelect(item)}
                        role="option"
                        aria-selected={selectedSuggestionIndex === idx}
                        className={`w-full text-left px-4 py-3 text-sm border-b ${borderClass} transition-colors ${
                          selectedSuggestionIndex === idx ? 'bg-blue-500 text-white' : hoverClass
                        }`}
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-lg">{getTypeIcon(item.type)}</span>
                          <div className="flex-1 min-w-0">
                            <div className="font-semibold truncate">{item.title}</div>
                            <div className="text-xs text-gray-500 truncate">
                              {item.module}
                            </div>
                          </div>
                          {item.confidence && (
                            <span className="text-xs px-2 py-1 bg-green-100 text-green-800 rounded">
                              {Math.round(item.confidence * 100)}%
                            </span>
                          )}
                        </div>
                      </button>
                    ))}
                  </div>
                )}

                {/* Modules */}
                {groupedSuggestions.module.length > 0 && (
                  <div>
                    <div className="px-4 py-2 text-xs font-semibold text-gray-600 uppercase tracking-wide">
                      Modules
                    </div>
                    {groupedSuggestions.module.map((item) => (
                      <button
                        key={item.id}
                        onClick={() => handleSuggestionSelect(item)}
                        className={`w-full text-left px-4 py-3 text-sm border-b ${borderClass} ${hoverClass} transition-colors`}
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-lg">{getTypeIcon(item.type)}</span>
                          <div className="flex-1 min-w-0">
                            <div className="font-semibold truncate">{item.title}</div>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                )}

                {/* Guides */}
                {groupedSuggestions.guide.length > 0 && (
                  <div>
                    <div className="px-4 py-2 text-xs font-semibold text-gray-600 uppercase tracking-wide">
                      Guides
                    </div>
                    {groupedSuggestions.guide.map((item) => (
                      <button
                        key={item.id}
                        onClick={() => handleSuggestionSelect(item)}
                        className={`w-full text-left px-4 py-3 text-sm border-b ${borderClass} ${hoverClass} transition-colors`}
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-lg">{getTypeIcon(item.type)}</span>
                          <div className="flex-1 min-w-0">
                            <div className="font-semibold truncate">{item.title}</div>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                )}

                {/* Concepts */}
                {groupedSuggestions.concept.length > 0 && (
                  <div>
                    <div className="px-4 py-2 text-xs font-semibold text-gray-600 uppercase tracking-wide">
                      Concepts
                    </div>
                    {groupedSuggestions.concept.map((item) => (
                      <button
                        key={item.id}
                        onClick={() => handleSuggestionSelect(item)}
                        className={`w-full text-left px-4 py-3 text-sm border-b ${borderClass} ${hoverClass} transition-colors`}
                      >
                        <div className="flex items-center gap-2">
                          <span className="text-lg">{getTypeIcon(item.type)}</span>
                          <div className="flex-1 min-w-0">
                            <div className="font-semibold truncate">{item.title}</div>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                )}

                {/* Did you mean section */}
                {query && suggestions.length < 3 && (
                  <div className="px-4 py-3 border-t">
                    <div className="text-xs text-gray-500 mb-2">Did you mean:</div>
                    {generateFuzzySuggestions(query).map((item) => (
                      <button
                        key={item.id}
                        onClick={() => {
                          setQuery(item.title);
                          performAutocomplete(item.title);
                        }}
                        className={`block text-left text-sm text-blue-600 hover:text-blue-800 mb-1`}
                      >
                        {item.title}
                      </button>
                    ))}
                  </div>
                )}

                <button
                  onClick={performFullSearch}
                  className={`w-full text-left px-4 py-3 text-sm font-semibold text-blue-600 border-t ${borderClass} hover:bg-blue-50 transition-colors`}
                >
                  View all results for "{query}"
                </button>
              </>
            )}
          </div>
        )}
      </div>

      {/* Search Tabs */}
      {showResults && (
        <div className={`mt-6 flex gap-2 border-b ${borderClass} overflow-x-auto`}>
          {['all', 'function', 'module', 'guide'].map((tab) => (
            <button
              key={tab}
              onClick={() => {
                setActiveTab(tab);
                setCurrentPage(1);
              }}
              className={`px-4 py-2 text-sm font-medium capitalize whitespace-nowrap transition-colors ${
                activeTab === tab
                  ? 'border-b-2 border-blue-600 text-blue-600'
                  : 'text-gray-600 hover:text-gray-900'
              }`}
            >
              {tab === 'all' ? 'All Results' : tab}
            </button>
          ))}
        </div>
      )}

      {/* Results Container */}
      {showResults && (
        <div ref={resultsContainerRef} className="mt-6 grid grid-cols-1 lg:grid-cols-4 gap-6">
          {/* Sidebar Filters */}
          <div className={`lg:col-span-1 p-4 ${borderClass} rounded-lg border`}>
            <h3 className="font-semibold mb-4 text-sm uppercase tracking-wide">
              Filters
            </h3>

            {/* Type Filter */}
            <div className="mb-4">
              <h4 className="text-xs font-semibold text-gray-600 uppercase mb-2">
                Doc Type
              </h4>
              {['function', 'module', 'guide', 'concept'].map((type) => (
                <label
                  key={type}
                  className="flex items-center gap-2 mb-2 cursor-pointer text-sm"
                >
                  <input
                    type="checkbox"
                    checked={selectedFilter.type.includes(type)}
                    onChange={(e) => {
                      setSelectedFilter((prev) => ({
                        ...prev,
                        type: e.target.checked
                          ? [...prev.type, type]
                          : prev.type.filter((t) => t !== type),
                      }));
                      setCurrentPage(1);
                    }}
                    className="w-4 h-4 rounded cursor-pointer"
                  />
                  <span className="capitalize">{type}</span>
                </label>
              ))}
            </div>

            {/* Confidence Filter */}
            <div className="mb-4">
              <h4 className="text-xs font-semibold text-gray-600 uppercase mb-2">
                Confidence
              </h4>
              <input
                type="range"
                min="0"
                max="1"
                step="0.1"
                value={selectedFilter.confidence}
                onChange={(e) => {
                  setSelectedFilter((prev) => ({
                    ...prev,
                    confidence: parseFloat(e.target.value),
                  }));
                  setCurrentPage(1);
                }}
                className="w-full"
              />
              <div className="text-xs text-gray-500 mt-1">
                {Math.round(selectedFilter.confidence * 100)}% and up
              </div>
            </div>

            {/* Sort */}
            <div>
              <h4 className="text-xs font-semibold text-gray-600 uppercase mb-2">
                Sort By
              </h4>
              <select
                value={sortBy}
                onChange={(e) => {
                  setSortBy(e.target.value);
                  setCurrentPage(1);
                }}
                className={`w-full px-2 py-1 text-sm border ${borderClass} rounded outline-none`}
              >
                <option value="relevance">Relevance</option>
                <option value="newest">Newest</option>
                <option value="confidence">Confidence</option>
              </select>
            </div>
          </div>

          {/* Results List */}
          <div className="lg:col-span-3">
            {isLoading && (
              <div className="text-center py-8">
                <div className="inline-block">
                  <div className="animate-spin text-3xl">⟳</div>
                </div>
                <p className="mt-2 text-gray-500">Searching...</p>
              </div>
            )}

            {!isLoading && results.length === 0 && (
              <div className="text-center py-12">
                <div className="text-4xl mb-4">🔍</div>
                <h3 className="text-lg font-semibold mb-2">
                  {query ? 'No results found' : 'Start searching'}
                </h3>
                <p className="text-gray-500">
                  {query
                    ? `Try adjusting your search query or filters`
                    : 'Enter a search term to begin'}
                </p>
              </div>
            )}

            {!isLoading && results.length > 0 && (
              <>
                <div
                  className="text-sm text-gray-600 mb-4"
                  role="status"
                  aria-live="polite"
                  aria-atomic="true"
                >
                  Found {results.length} result{results.length !== 1 ? 's' : ''} for "
                  {query}"
                </div>

                <div className="space-y-4">
                  {results.map((result, idx) => (
                    <button
                      key={result.id}
                      onClick={() => handleResultSelect(result)}
                      className={`w-full text-left p-4 border ${borderClass} rounded-lg transition-all hover:shadow-md hover:border-blue-400`}
                    >
                      <div className="flex items-start gap-3">
                        <span className="text-2xl flex-shrink-0">
                          {getTypeIcon(result.type)}
                        </span>
                        <div className="flex-1 min-w-0">
                          <h3 className="font-semibold text-base mb-1 truncate">
                            {result.title}
                          </h3>
                          <p className="text-xs text-gray-500 mb-2">
                            {result.module}
                          </p>
                          <p className="text-sm text-gray-700 line-clamp-2">
                            {getExcerpt(result.content, query)}
                          </p>
                        </div>
                        {result.confidence && (
                          <div className="flex-shrink-0 text-right">
                            <div className="text-xs font-semibold text-gray-600 mb-1">
                              {Math.round(result.score * 100)}%
                            </div>
                            <div className="text-xs text-gray-500">
                              {Math.round(result.confidence * 100)}% conf
                            </div>
                          </div>
                        )}
                      </div>
                    </button>
                  ))}
                </div>

                {/* Pagination */}
                {results.length >= maxResults && (
                  <div className="mt-6 text-center">
                    <button
                      onClick={() => setCurrentPage((prev) => prev + 1)}
                      className="px-4 py-2 text-sm font-semibold text-blue-600 hover:text-blue-800 transition-colors"
                    >
                      Load more results
                    </button>
                  </div>
                )}
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default SearchComponent;
