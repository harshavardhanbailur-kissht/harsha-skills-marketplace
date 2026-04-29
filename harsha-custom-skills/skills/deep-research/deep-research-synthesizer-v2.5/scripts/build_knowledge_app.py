#!/usr/bin/env python3
"""
Knowledge Base Web App Builder
Assembles knowledge entries JSON into a self-contained interactive HTML application.
"""

import argparse
import json
import os
import sys
import hashlib
import re
from datetime import datetime
from collections import Counter, defaultdict
from pathlib import Path


class KnowledgeValidator:
    """Validates knowledge entries against schema and constraints."""

    REQUIRED_FIELDS = ['id', 'title', 'category', 'content', 'confidence']
    VALID_CONFIDENCE_LEVELS = ['VERIFIED', 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN']
    OPTIONAL_FIELDS = ['summary', 'source', 'subcategory', 'tags', 'related', 'gaps']

    def __init__(self):
        self.errors = []
        self.warnings = []
        self.auto_fixes = []

    def validate_entries(self, entries):
        """Validate list of knowledge entries."""
        if not isinstance(entries, list):
            self.errors.append("Root must be a list of entries")
            return False

        for idx, entry in enumerate(entries):
            self._validate_entry(entry, idx)

        return len(self.errors) == 0

    def _validate_entry(self, entry, idx):
        """Validate individual entry."""
        if not isinstance(entry, dict):
            self.errors.append(f"Entry {idx}: Must be a dictionary, got {type(entry).__name__}")
            return

        # Check required fields
        for field in self.REQUIRED_FIELDS:
            if field not in entry:
                if field == 'id':
                    self.warnings.append(f"Entry {idx}: Missing 'id' field (will auto-generate)")
                else:
                    self.errors.append(f"Entry {idx}: Missing required field '{field}'")
            elif field == 'id' and not entry[field]:
                self.warnings.append(f"Entry {idx}: Empty 'id' field (will auto-generate)")

        # Validate confidence level
        if 'confidence' in entry:
            confidence = entry['confidence']
            if isinstance(confidence, str):
                upper_conf = confidence.upper()
                if upper_conf not in self.VALID_CONFIDENCE_LEVELS:
                    self.errors.append(
                        f"Entry {idx}: Invalid confidence level '{confidence}'. "
                        f"Must be one of: {', '.join(self.VALID_CONFIDENCE_LEVELS)}"
                    )
                elif upper_conf != confidence:
                    self.auto_fixes.append(f"Entry {idx}: Normalized confidence '{confidence}' to '{upper_conf}'")
            else:
                self.errors.append(f"Entry {idx}: Confidence must be string, got {type(confidence).__name__}")

        # Validate related entries references
        if 'related' in entry:
            related = entry['related']
            if not isinstance(related, list):
                self.errors.append(f"Entry {idx}: 'related' must be a list, got {type(related).__name__}")
            else:
                for rel_id in related:
                    if not isinstance(rel_id, str):
                        self.errors.append(f"Entry {idx}: Related ID must be string, got {type(rel_id).__name__}")

        # Validate tags
        if 'tags' in entry:
            tags = entry['tags']
            if not isinstance(tags, list):
                self.errors.append(f"Entry {idx}: 'tags' must be a list, got {type(tags).__name__}")
            else:
                for tag in tags:
                    if not isinstance(tag, str):
                        self.errors.append(f"Entry {idx}: Tag must be string, got {type(tag).__name__}")
                if len(tags) > 5:
                    self.warnings.append(f"Entry {idx}: Has {len(tags)} tags (max recommended: 5)")

        # Validate optional fields existence
        for field in self.OPTIONAL_FIELDS:
            if field not in entry and field not in ['id', 'summary']:
                if field in ['tags', 'related']:
                    pass  # These are truly optional
                elif field == 'gaps' and 'gaps' not in entry:
                    pass  # Gaps are optional

        # Check string fields
        for field in ['title', 'category', 'content', 'summary', 'source']:
            if field in entry and not isinstance(entry[field], str):
                self.errors.append(f"Entry {idx}: '{field}' must be string, got {type(entry[field]).__name__}")

        # Warn about missing summary
        if 'summary' not in entry:
            self.warnings.append(f"Entry {idx}: Missing 'summary' (will auto-generate)")

        # Warn about missing source
        if 'source' not in entry:
            self.warnings.append(f"Entry {idx}: Missing 'source' field")

    def get_report(self):
        """Return validation report."""
        return {
            'valid': len(self.errors) == 0,
            'error_count': len(self.errors),
            'warning_count': len(self.warnings),
            'auto_fix_count': len(self.auto_fixes),
            'errors': self.errors,
            'warnings': self.warnings,
            'auto_fixes': self.auto_fixes
        }


class EntryEnricher:
    """Enriches knowledge entries with auto-generated fields and metadata."""

    def __init__(self):
        self.enriched_entries = []
        self.all_tags = Counter()

    def enrich_entries(self, entries):
        """Enrich list of entries."""
        for entry in entries:
            enriched = self._enrich_entry(entry)
            self.enriched_entries.append(enriched)

        # Sort by category, then by title
        self.enriched_entries.sort(key=lambda e: (e.get('category', ''), e.get('title', '')))

        return self.enriched_entries

    def _enrich_entry(self, entry):
        """Enrich single entry."""
        enriched = entry.copy()

        # Auto-generate ID if missing
        if not enriched.get('id'):
            title = enriched.get('title', 'unknown')
            enriched['id'] = hashlib.sha256(title.encode()).hexdigest()[:12]

        # Auto-generate summary if missing
        if not enriched.get('summary'):
            content = enriched.get('content', '')
            # Try to get first sentence
            match = re.match(r'^([^.!?]+[.!?])', content)
            if match:
                enriched['summary'] = match.group(1).strip()
            else:
                enriched['summary'] = content[:150].strip() + ('...' if len(content) > 150 else '')

        # Normalize confidence level
        if 'confidence' in enriched:
            enriched['confidence'] = enriched['confidence'].upper()
        else:
            enriched['confidence'] = 'UNKNOWN'

        # Auto-generate tags from content if missing
        if not enriched.get('tags'):
            enriched['tags'] = self._extract_tags(enriched.get('content', ''), enriched.get('title', ''))

        # Count tags for statistics
        for tag in enriched.get('tags', []):
            self.all_tags[tag] += 1

        # Ensure related is a list
        if 'related' not in enriched:
            enriched['related'] = []

        # Ensure gaps is a list
        if 'gaps' not in enriched:
            enriched['gaps'] = []

        # Calculate metadata
        content = enriched.get('content', '')
        word_count = len(content.split())
        enriched['word_count'] = word_count
        enriched['reading_time_minutes'] = max(1, round(word_count / 200))  # Avg 200 words per minute

        # Add timestamp if not present
        if 'created_at' not in enriched:
            enriched['created_at'] = datetime.utcnow().isoformat() + 'Z'

        return enriched

    def _extract_tags(self, content, title):
        """Extract key noun phrases from content as tags."""
        # Simple approach: find capitalized words and common phrases
        text = f"{title} {content}".lower()

        # Remove common stop words
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'be', 'been',
            'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'must', 'can', 'it', 'this', 'that'
        }

        # Extract words (3-20 chars, contain letter/digit)
        words = re.findall(r'\b[a-z0-9]{3,20}\b', text)

        # Filter out stop words and count
        word_freq = Counter()
        for word in words:
            if word not in stop_words:
                word_freq[word] += 1

        # Get top 5 most frequent meaningful words
        tags = [word for word, _ in word_freq.most_common(5)]
        return tags

    def get_tag_statistics(self):
        """Return tag frequency statistics."""
        return dict(self.all_tags.most_common(20))


class GraphDataGenerator:
    """Generates knowledge graph data for visualization."""

    def __init__(self):
        self.nodes = []
        self.edges = []
        self.clusters = {}

    def generate_graph(self, entries):
        """Generate graph data from entries."""
        # Build nodes
        entry_ids = set()
        connection_count = defaultdict(int)

        for entry in entries:
            entry_ids.add(entry['id'])
            node = {
                'id': entry['id'],
                'label': entry.get('title', 'Untitled'),
                'category': entry.get('category', 'Unknown'),
                'confidence': entry.get('confidence', 'UNKNOWN'),
                'size': 10
            }
            self.nodes.append(node)

        # Build edges from related fields
        for entry in entries:
            for related_id in entry.get('related', []):
                if related_id in entry_ids:
                    connection_count[entry['id']] += 1
                    connection_count[related_id] += 1

                    edge = {
                        'source': entry['id'],
                        'target': related_id,
                        'type': 'related'
                    }
                    self.edges.append(edge)
                else:
                    # BUG FIX 5: Warn about invalid related IDs
                    sys.stderr.write(f"WARNING: Entry '{entry['id']}' references non-existent related entry '{related_id}'\n")

        # BUG FIX 1: Generate dependency edges for learning mode
        self._generate_dependency_edges(entries, connection_count, entry_ids)

        # Detect edges from tag overlap (2+ shared tags)
        for i, entry1 in enumerate(entries):
            tags1 = set(entry1.get('tags', []))
            if len(tags1) == 0:
                continue

            for entry2 in entries[i+1:]:
                tags2 = set(entry2.get('tags', []))
                overlap = len(tags1 & tags2)

                if overlap >= 2:
                    # Check edge doesn't already exist
                    existing = any(
                        (e['source'] == entry1['id'] and e['target'] == entry2['id']) or
                        (e['source'] == entry2['id'] and e['target'] == entry1['id'])
                        for e in self.edges
                    )

                    if not existing:
                        connection_count[entry1['id']] += 1
                        connection_count[entry2['id']] += 1

                        edge = {
                            'source': entry1['id'],
                            'target': entry2['id'],
                            'type': 'tag_overlap',
                            'strength': overlap
                        }
                        self.edges.append(edge)

        # BUG FIX 6: Update node sizes based on connection count (with division by zero check)
        max_connections = max(connection_count.values()) if connection_count else 1
        for node in self.nodes:
            connections = connection_count.get(node['id'], 0)
            # Ensure max_connections is at least 1 to avoid division by zero
            node['size'] = 10 + (30 * connections / max(max_connections, 1))

        # Detect clusters by category
        category_clusters = defaultdict(list)
        for node in self.nodes:
            category = node['category']
            category_clusters[category].append(node['id'])

        self.clusters = dict(category_clusters)

        return {
            'nodes': self.nodes,
            'edges': self.edges,
            'clusters': self.clusters,
            'node_count': len(self.nodes),
            'edge_count': len(self.edges),
            'cluster_count': len(self.clusters)
        }

    def _generate_dependency_edges(self, entries, connection_count, entry_ids):
        """BUG FIX 1: Generate dependency edges for learning mode topological sort.

        A dependency exists when:
        - Entry A's content references concepts that are prerequisites for Entry B
        - Entry A has tags that are a subset of Entry B's tags AND A has fewer tags (simpler = prerequisite)
        - Entry A's category is foundation/basics/introduction and B's is more specific
        """
        foundation_indicators = {'foundation', 'basics', 'introduction', 'overview', 'primer'}

        for i, entry_a in enumerate(entries):
            cat_a = entry_a.get('category', '').lower()
            tags_a = set(entry_a.get('tags', []))
            content_a = entry_a.get('content', '') + ' ' + entry_a.get('title', '')
            content_a_lower = content_a.lower()

            for entry_b in entries[i+1:]:
                cat_b = entry_b.get('category', '').lower()
                tags_b = set(entry_b.get('tags', []))
                content_b = entry_b.get('content', '') + ' ' + entry_b.get('title', '')
                content_b_lower = content_b.lower()

                # Check if A is a prerequisite for B
                is_dependency = False
                strength = 0.5

                # Rule 1: A's tags are subset of B's AND A has fewer (simpler -> prerequisite)
                if tags_a.issubset(tags_b) and len(tags_a) > 0 and len(tags_a) < len(tags_b):
                    is_dependency = True
                    strength = 0.6

                # Rule 2: A's category is foundation-like and B's is more specific
                if cat_a in foundation_indicators and cat_b not in foundation_indicators:
                    is_dependency = True
                    strength = 0.7

                # Rule 3: A's content references keywords that appear in B's title (prerequisite concept)
                if is_dependency or (len(tags_a) > 0 and any(tag in content_b_lower for tag in tags_a)):
                    is_dependency = True
                    strength = min(0.8, strength + 0.1)

                if is_dependency:
                    # Check edge doesn't already exist
                    existing = any(
                        (e['source'] == entry_a['id'] and e['target'] == entry_b['id']) and e.get('type') == 'dependency'
                        for e in self.edges
                    )
                    if not existing:
                        connection_count[entry_a['id']] += 1
                        connection_count[entry_b['id']] += 1
                        edge = {
                            'source': entry_a['id'],
                            'target': entry_b['id'],
                            'type': 'dependency',
                            'strength': strength
                        }
                        self.edges.append(edge)


class StatisticsCalculator:
    """Calculates statistics about knowledge base."""

    def calculate_stats(self, entries):
        """Calculate comprehensive statistics."""
        if not entries:
            return self._empty_stats()

        categories = Counter()
        tags = Counter()
        sources = Counter()
        confidence_dist = Counter()
        gap_count = 0
        total_words = 0

        for entry in entries:
            categories[entry.get('category', 'Unknown')] += 1
            confidence_dist[entry.get('confidence', 'UNKNOWN')] += 1

            for tag in entry.get('tags', []):
                tags[tag] += 1

            source = entry.get('source', 'unknown')
            if source.startswith('http'):
                sources['url'] += 1
            elif source.lower() in ['notion', 'gdrive', 'slack']:
                sources[source.lower()] += 1
            else:
                sources['file'] += 1

            gap_count += len(entry.get('gaps', []))
            total_words += entry.get('word_count', 0)

        # Calculate coverage score (% with confidence >= MEDIUM)
        high_confidence_count = (
            confidence_dist.get('VERIFIED', 0) +
            confidence_dist.get('HIGH', 0) +
            confidence_dist.get('MEDIUM', 0)
        )
        coverage_score = (high_confidence_count / len(entries) * 100) if entries else 0

        avg_content_length = total_words / len(entries) if entries else 0

        return {
            'total_entries': len(entries),
            'total_categories': len(categories),
            'total_tags': len(tags),
            'total_sources': len(sources),
            'total_words': total_words,
            'average_content_length': round(avg_content_length, 1),
            'gap_count': gap_count,
            'coverage_score': round(coverage_score, 1),
            'confidence_distribution': dict(confidence_dist),
            'category_breakdown': dict(categories),
            'source_breakdown': dict(sources),
            'top_tags': dict(tags.most_common(10)),
            'generated_at': datetime.utcnow().isoformat() + 'Z'
        }

    def _empty_stats(self):
        """Return empty statistics template."""
        return {
            'total_entries': 0,
            'total_categories': 0,
            'total_tags': 0,
            'total_sources': 0,
            'total_words': 0,
            'average_content_length': 0,
            'gap_count': 0,
            'coverage_score': 0,
            'confidence_distribution': {},
            'category_breakdown': {},
            'source_breakdown': {},
            'top_tags': {},
            'generated_at': datetime.utcnow().isoformat() + 'Z'
        }


class LearningModeProcessor:
    """Performs topological sort on dependency edges and assigns learning tiers."""

    def __init__(self):
        self.sorted_order = []
        self.tier_counts = Counter()

    def process(self, entries, graph_data):
        """Assign learning tiers and reorder entries based on dependency edges."""
        # Build dependency in-degree from graph edges
        dep_in_degree = defaultdict(int)
        entry_ids = {e['id'] for e in entries}

        edges = graph_data.get('edges', [])
        dep_edges = [e for e in edges if e.get('type') == 'dependency']

        # Convention: source REQUIRES target (target is prerequisite)
        # So for topological sort: target comes before source
        adj_list = defaultdict(list)
        for edge in dep_edges:
            src = edge.get('source', '')
            tgt = edge.get('target', '')
            if src in entry_ids and tgt in entry_ids:
                dep_in_degree[src] += 1
                adj_list[tgt].append(src)

        # Ensure all entries have an in-degree entry
        for entry in entries:
            if entry['id'] not in dep_in_degree:
                dep_in_degree[entry['id']] = 0

        # Kahn's topological sort
        queue = [eid for eid in entry_ids if dep_in_degree.get(eid, 0) == 0]
        queue.sort()  # Deterministic ordering
        sorted_ids = []

        while queue:
            current = queue.pop(0)
            sorted_ids.append(current)
            for neighbor in adj_list.get(current, []):
                dep_in_degree[neighbor] -= 1
                if dep_in_degree[neighbor] == 0:
                    queue.append(neighbor)
            queue.sort()

        # Append cycle members
        sorted_set = set(sorted_ids)
        for entry in entries:
            if entry['id'] not in sorted_set:
                sorted_ids.append(entry['id'])

        self.sorted_order = sorted_ids

        # Assign learning tiers based on dependency in-degree
        for entry in entries:
            deg = 0
            for edge in dep_edges:
                if edge.get('source') == entry['id']:
                    deg += 1

            if deg == 0:
                entry['learning_tier'] = 'foundation'
                entry['tier_label'] = 'Foundation'
            elif deg <= 2:
                entry['learning_tier'] = 'intermediate'
                entry['tier_label'] = 'Intermediate'
            else:
                entry['learning_tier'] = 'advanced'
                entry['tier_label'] = 'Advanced'

            entry['dependency_in_degree'] = deg
            self.tier_counts[entry['learning_tier']] += 1

        # Reorder entries by topological sort position
        id_to_pos = {eid: i for i, eid in enumerate(sorted_ids)}
        entries.sort(key=lambda e: id_to_pos.get(e['id'], len(sorted_ids)))

        return entries

    def get_tier_report(self):
        """Return tier distribution report."""
        return dict(self.tier_counts)


class VisualizationEntryParser:
    """Parses pre-researched data for the visualization-only entry point.

    Supports three input formats:
    1. JSON: List of dicts or dict with entries/findings/claims key
    2. Markdown: Sections split by ## headings with [Source](URL) citations
    3. Structured reports: FINDING N: pattern with Confidence/Sources/Evidence lines
    """

    CONFIDENCE_MAP = {
        'verified': 'VERIFIED', 'high': 'HIGH', 'medium': 'MEDIUM',
        'low': 'LOW', 'unknown': 'UNKNOWN'
    }

    def parse(self, data, input_format='auto'):
        """Parse pre-researched data into knowledge entries.

        Args:
            data: Parsed JSON (dict/list) or raw text string
            input_format: 'auto', 'json', 'markdown', or 'structured'

        Accepts:
        - List of dicts (JSON claims array) — pass through with normalization
        - Dict with 'findings' or 'claims' key — extract the list
        - Dict with 'entries' key — extract the list
        - String in markdown format (## headings) — parse sections
        - String in structured report format (FINDING N:) — parse findings
        """
        # If string input, route to text parsers
        if isinstance(data, str):
            if input_format == 'auto':
                input_format = self._detect_text_format(data)
            if input_format == 'markdown':
                return self._parse_markdown(data)
            elif input_format == 'structured':
                return self._parse_structured_report(data)
            else:
                raise ValueError(
                    f"Cannot parse text input with format '{input_format}'. "
                    "Use 'markdown' or 'structured' for text input."
                )

        # JSON path (existing logic)
        if isinstance(data, list):
            return [self._normalize_claim(item, i) for i, item in enumerate(data)]

        if isinstance(data, dict):
            for key in ['entries', 'findings', 'claims', 'results', 'data']:
                if key in data and isinstance(data[key], list):
                    return [self._normalize_claim(item, i) for i, item in enumerate(data[key])]

        raise ValueError(
            "Visualization-only input must be a JSON array of claims, "
            "a dict with 'entries'/'findings'/'claims' key, "
            "a markdown document with ## headings, or "
            "a structured report with FINDING N: sections."
        )

    def _detect_text_format(self, text):
        """Auto-detect whether text is markdown or structured report."""
        lines = text.strip().split('\n')
        heading_count = sum(1 for line in lines if re.match(r'^#{1,3}\s+', line))
        finding_count = sum(1 for line in lines if re.match(r'^FINDING\s+\d+', line, re.IGNORECASE))

        if finding_count >= 2:
            return 'structured'
        if heading_count >= 2:
            return 'markdown'
        # Default to markdown for any text with at least one heading
        if heading_count >= 1:
            return 'markdown'
        return 'structured'  # fallback: treat as single finding

    def _parse_markdown(self, text):
        """Parse markdown document split by ## headings.

        Expected format:
        ## Section Title
        Content paragraph with [Source Name](URL) citations.
        More content...

        ## Another Section
        ...
        """
        entries = []
        # Split on ## headings (level 2), keeping the heading text
        sections = re.split(r'^##\s+', text, flags=re.MULTILINE)

        for i, section in enumerate(sections):
            section = section.strip()
            if not section:
                continue

            # First line is the title, rest is content
            lines = section.split('\n', 1)
            title = lines[0].strip().rstrip('#').strip()
            content = lines[1].strip() if len(lines) > 1 else ''

            if not title:
                continue

            # Extract [Source](URL) citations
            citations = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            sources = '; '.join(f'{name} ({url})' for name, url in citations) if citations else ''

            # Extract tags from ### sub-headings within this section
            sub_headings = re.findall(r'^###\s+(.+)$', content, re.MULTILINE)
            tags = [h.strip() for h in sub_headings[:5]] if sub_headings else []

            # Infer category from content or default
            category = self._infer_category_from_content(title, content)

            # Infer confidence from language cues
            confidence = self._infer_confidence_from_text(content)

            entry_id = hashlib.sha256(title.encode()).hexdigest()[:12]
            entry = {
                'id': entry_id,
                'title': title,
                'content': content,
                'category': category,
                'confidence': confidence,
                'origin': 'visualization-entry-markdown',
            }
            if sources:
                entry['source'] = sources
            if tags:
                entry['tags'] = tags

            # Generate summary from first sentence
            first_sentence = re.split(r'[.!?]\s', content, maxsplit=1)
            if first_sentence and len(first_sentence[0]) > 10:
                entry['summary'] = first_sentence[0].strip()[:200]

            entries.append(entry)

        if not entries:
            raise ValueError(
                "No entries found in markdown input. "
                "Ensure your markdown has ## headings to delineate sections."
            )

        return entries

    def _parse_structured_report(self, text):
        """Parse structured report with FINDING N: pattern.

        Expected format:
        FINDING 1: Title of the Finding
        Confidence: HIGH
        Sources: source1.com, source2.com
        Evidence: Detailed evidence paragraph...

        FINDING 2: Another Finding
        ...
        """
        entries = []
        # Split on FINDING N: pattern (case-insensitive)
        finding_blocks = re.split(
            r'^FINDING\s+(\d+)\s*[:\-]\s*',
            text,
            flags=re.MULTILINE | re.IGNORECASE
        )

        # finding_blocks = ['preamble', '1', 'content1', '2', 'content2', ...]
        # Skip preamble (index 0), then pairs of (number, content)
        i = 1
        while i < len(finding_blocks) - 1:
            finding_num = finding_blocks[i].strip()
            block = finding_blocks[i + 1].strip()
            i += 2

            if not block:
                continue

            lines = block.split('\n')
            title = lines[0].strip()

            # Parse structured fields from subsequent lines
            confidence = 'MEDIUM'
            sources = ''
            evidence_lines = []
            category = 'Uncategorized'
            in_evidence = False

            for line in lines[1:]:
                line_stripped = line.strip()
                if not line_stripped:
                    if in_evidence:
                        evidence_lines.append('')
                    continue

                # Match known field patterns
                conf_match = re.match(r'^Confidence\s*[:\-]\s*(.+)$', line_stripped, re.IGNORECASE)
                src_match = re.match(r'^Sources?\s*[:\-]\s*(.+)$', line_stripped, re.IGNORECASE)
                evid_match = re.match(r'^Evidence\s*[:\-]\s*(.+)$', line_stripped, re.IGNORECASE)
                cat_match = re.match(r'^Category\s*[:\-]\s*(.+)$', line_stripped, re.IGNORECASE)
                tags_match = re.match(r'^Tags?\s*[:\-]\s*(.+)$', line_stripped, re.IGNORECASE)

                if conf_match:
                    confidence = self._normalize_confidence(conf_match.group(1).strip())
                    in_evidence = False
                elif src_match:
                    sources = src_match.group(1).strip()
                    in_evidence = False
                elif evid_match:
                    evidence_lines.append(evid_match.group(1).strip())
                    in_evidence = True
                elif cat_match:
                    category = cat_match.group(1).strip()
                    in_evidence = False
                elif tags_match:
                    pass  # handled below
                    in_evidence = False
                elif in_evidence:
                    evidence_lines.append(line_stripped)
                else:
                    # Unstructured content after title — treat as evidence
                    evidence_lines.append(line_stripped)
                    in_evidence = True

            content = '\n'.join(evidence_lines).strip()
            if not content:
                content = title  # Fallback: use title as content if no evidence

            # Extract tags if present
            tags = []
            for line in lines[1:]:
                tags_match = re.match(r'^Tags?\s*[:\-]\s*(.+)$', line.strip(), re.IGNORECASE)
                if tags_match:
                    tags = [t.strip() for t in tags_match.group(1).split(',')][:5]
                    break

            entry_id = hashlib.sha256(title.encode()).hexdigest()[:12]
            entry = {
                'id': entry_id,
                'title': title,
                'content': content,
                'category': category,
                'confidence': confidence,
                'origin': 'visualization-entry-structured',
            }
            if sources:
                entry['source'] = sources
            if tags:
                entry['tags'] = tags

            entries.append(entry)

        if not entries:
            raise ValueError(
                "No findings found in structured report. "
                "Ensure your report uses 'FINDING N: Title' format."
            )

        return entries

    def _infer_category_from_content(self, title, content):
        """Infer a category from title and content keywords."""
        combined = (title + ' ' + content[:300]).lower()
        category_keywords = {
            'Market Analysis': ['market', 'industry', 'competitor', 'share', 'growth rate'],
            'Technology': ['technology', 'platform', 'api', 'architecture', 'stack', 'framework'],
            'User Research': ['user', 'persona', 'interview', 'survey', 'feedback', 'ux'],
            'Strategy': ['strategy', 'roadmap', 'vision', 'okr', 'objective', 'initiative'],
            'Financials': ['revenue', 'cost', 'profit', 'pricing', 'budget', 'roi', 'financial'],
            'Operations': ['process', 'workflow', 'operations', 'pipeline', 'automation'],
            'Regulatory': ['regulation', 'compliance', 'legal', 'policy', 'gdpr', 'rbi'],
        }
        for cat, keywords in category_keywords.items():
            if any(kw in combined for kw in keywords):
                return cat
        return 'General'

    def _infer_confidence_from_text(self, content):
        """Infer confidence level from language cues in text."""
        lower = content.lower()
        high_cues = ['studies show', 'data confirms', 'evidence indicates', 'verified', 'proven']
        low_cues = ['might', 'possibly', 'unclear', 'anecdotal', 'unverified', 'speculative']
        if any(cue in lower for cue in high_cues):
            return 'HIGH'
        if any(cue in lower for cue in low_cues):
            return 'LOW'
        return 'MEDIUM'

    def _normalize_claim(self, raw, index):
        """Normalize a single claim to internal entry format."""
        if not isinstance(raw, dict):
            return {
                'id': f'claim-{index}',
                'title': f'Claim {index + 1}',
                'content': str(raw),
                'category': 'Uncategorized',
                'confidence': 'MEDIUM',
            }

        title = raw.get('title', raw.get('name', f'Claim {index + 1}'))
        entry = {
            'id': raw.get('id', hashlib.sha256(title.encode()).hexdigest()[:12]),
            'title': title,
            'content': raw.get('content', raw.get('evidence', raw.get('description', ''))),
            'category': raw.get('category', raw.get('theme', 'Uncategorized')),
            'confidence': self._normalize_confidence(raw.get('confidence', 'MEDIUM')),
        }

        # Optional fields
        if 'summary' in raw:
            entry['summary'] = raw['summary']
        if 'source' in raw or 'sources' in raw:
            entry['source'] = raw.get('source', raw.get('sources', ''))
            if isinstance(entry['source'], list):
                entry['source'] = '; '.join(str(s) for s in entry['source'])
        if 'tags' in raw:
            entry['tags'] = raw['tags']
        if 'related' in raw:
            entry['related'] = raw['related']
        if 'subcategory' in raw:
            entry['subcategory'] = raw['subcategory']

        # Mark origin
        entry['origin'] = 'visualization-entry'

        return entry

    def _normalize_confidence(self, value):
        """Normalize confidence from various formats."""
        if isinstance(value, (int, float)):
            if value >= 0.8:
                return 'HIGH'
            if value >= 0.5:
                return 'MEDIUM'
            if value >= 0.3:
                return 'LOW'
            return 'UNKNOWN'

        val = str(value).lower().strip()
        return self.CONFIDENCE_MAP.get(val, 'MEDIUM')


class BaseLensProcessor:
    """BUG FIX 3: Base class for lens processors (PM and FinTech).

    Extracts common patterns and reduces ~370 lines of duplicated code.
    Subclasses define: DIMENSIONS, DIMENSION_LABELS, DIMENSION_KEYWORDS, default_dimension
    and implement: _enrich_domain_fields()
    """

    # Abstract attributes (defined by subclasses)
    DIMENSIONS = []
    DIMENSION_LABELS = {}
    DIMENSION_KEYWORDS = {}
    default_dimension = 'solutions'

    def __init__(self):
        self.dimension_coverage = Counter()
        self.executive_summary_parts = {}

    def process(self, entries):
        """Add lens metadata to entries and calculate dimension coverage."""
        for entry in entries:
            self._enrich_entry(entry)

        # Calculate dimension coverage
        for dim in self.DIMENSIONS:
            lens_key = self._get_lens_key('dimensions')
            count = sum(1 for e in entries if dim in e.get(lens_key, []))
            self.dimension_coverage[dim] = count

        return entries

    def _enrich_entry(self, entry):
        """Add lens metadata fields to a single entry if not already present."""
        dimensions_key = self._get_lens_key('dimensions')
        so_what_key = self._get_lens_key('so_what')
        who_cares_key = self._get_lens_key('who_cares')
        decision_relevance_key = self._get_lens_key('decision_relevance')

        # Auto-infer dimensions from content if not provided
        if dimensions_key not in entry:
            entry[dimensions_key] = self._infer_dimensions(entry)

        # Let subclass handle domain-specific fields
        self._enrich_domain_fields(entry)

        # Default generic lens fields if not set
        if so_what_key not in entry:
            entry[so_what_key] = ''

        if who_cares_key not in entry:
            entry[who_cares_key] = []

        if decision_relevance_key not in entry:
            entry[decision_relevance_key] = ''

    def _infer_dimensions(self, entry):
        """BUG FIX 4: Infer dimensions using word-boundary matching to avoid false positives.

        Use regex word boundaries for single-word keywords and substring matching
        for multi-word keywords naturally.
        """
        combined = (
            entry.get('title', '') + ' ' +
            entry.get('content', '') + ' ' +
            entry.get('summary', '')
        ).lower()

        matched = []
        for dim, keywords in self.DIMENSION_KEYWORDS.items():
            score = 0
            for kw in keywords:
                # Use word boundaries for all keywords (works for both single and multi-word)
                if re.search(r'(?:^|\W)' + re.escape(kw) + r'(?:\W|$)', combined):
                    score += 1
            if score >= 2:
                matched.append(dim)

        # Default to default dimension if nothing matched
        if not matched:
            matched = [self.default_dimension]

        return matched[:3]  # Max 3 dimensions per entry

    def _enrich_domain_fields(self, entry):
        """Subclasses override to add domain-specific fields. Abstract method."""
        pass

    def _get_lens_key(self, field_type):
        """Get the lens-specific key for a field. Subclasses override."""
        return f"lens_{field_type}"

    def get_coverage_report(self):
        """Return dimension coverage report."""
        report = {}
        for dim in self.DIMENSIONS:
            count = self.dimension_coverage.get(dim, 0)
            label = self.DIMENSION_LABELS.get(dim, dim)
            if count >= 5:
                status = 'good'
            elif count >= 2:
                status = 'moderate'
            else:
                status = 'gap'
            report[dim] = {
                'label': label,
                'count': count,
                'status': status
            }
        return report

    def get_executive_summary_data(self, entries):
        """Generate structured data for Executive Summary. Subclasses override for specifics."""
        return {
            'dimension_coverage': self.get_coverage_report(),
            'gaps': [
                self.DIMENSION_LABELS.get(dim, dim)
                for dim, data in self.get_coverage_report().items()
                if data['status'] == 'gap'
            ],
            'total_entries': len(entries),
        }


class PMLensProcessor(BaseLensProcessor):
    """BUG FIX 3: Processes entries through the Product Management lens overlay.

    Inherits common dimension inference and coverage calculation from BaseLensProcessor.
    Adds PM-specific metadata, actionability scores, and executive summary.
    """

    # BUG FIX 3: Define class attributes for base class to use
    DIMENSIONS = [
        'opportunity', 'competitive', 'market_size', 'segments',
        'metrics', 'gtm', 'solutions', 'validation',
        'business_model', 'strategic_context'
    ]

    DIMENSION_LABELS = {
        'opportunity': 'Opportunity Landscape',
        'competitive': 'Competitive Positioning',
        'market_size': 'Market Size & Addressability',
        'segments': 'Customer Segments & Value',
        'metrics': 'Metrics & Measurement',
        'gtm': 'Go-to-Market Strategy',
        'solutions': 'Solution Patterns',
        'validation': 'Validation & Experimentation',
        'business_model': 'Business Model & Unit Economics',
        'strategic_context': 'Strategic Context & Constraints',
    }

    DIMENSION_KEYWORDS = {
        'opportunity': ['pain point', 'unmet need', 'frustration', 'struggle', 'gap', 'problem',
                        'job to be done', 'jtbd', 'workflow', 'friction'],
        'competitive': ['competitor', 'competitive', 'market leader', 'alternative', 'versus',
                        'market share', 'moat', 'switching cost', 'differentiat'],
        'market_size': ['tam', 'sam', 'som', 'market size', 'addressable', 'billion',
                        'million', 'growth rate', 'cagr', 'forecast'],
        'segments': ['segment', 'persona', 'buyer', 'customer type', 'user type',
                     'target audience', 'icp', 'ideal customer'],
        'metrics': ['metric', 'kpi', 'north star', 'benchmark', 'measure',
                    'adoption rate', 'retention', 'conversion', 'nps'],
        'gtm': ['go to market', 'gtm', 'distribution', 'channel', 'sales motion',
                'product-led', 'enterprise sales', 'adoption', 'launch'],
        'solutions': ['solution', 'product', 'feature', 'ux', 'interface',
                      'platform', 'tool', 'application', 'mvp', 'prototype'],
        'validation': ['assumption', 'experiment', 'hypothesis', 'test', 'validate',
                       'fail', 'lesson', 'pivot', 'risk'],
        'business_model': ['pricing', 'revenue', 'subscription', 'saas', 'freemium',
                          'ltv', 'cac', 'unit economics', 'margin', 'monetiz'],
        'strategic_context': ['regulation', 'compliance', 'legal', 'policy', 'dependency',
                             'constraint', 'risk', 'partnership', 'ecosystem'],
    }

    default_dimension = 'solutions'

    def _get_lens_key(self, field_type):
        """PM-specific lens key generation."""
        return f"pm_{field_type}"

    def _enrich_domain_fields(self, entry):
        """BUG FIX 3: Add PM-specific fields (actionability)."""
        if 'pm_actionability' not in entry:
            entry['pm_actionability'] = self._infer_actionability(entry)

    def _infer_actionability(self, entry):
        """Infer PM actionability from entry characteristics."""
        content = (entry.get('content', '') + ' ' + entry.get('title', '')).lower()
        confidence = entry.get('confidence', 'UNKNOWN')

        # High actionability signals
        high_signals = ['pricing', 'revenue', 'tam', 'sam', 'market size',
                       'competitor', 'adoption rate', 'conversion', 'churn']
        high_count = sum(1 for s in high_signals if s in content)

        if high_count >= 2 and confidence in ('HIGH', 'VERIFIED'):
            return 'HIGH'
        elif high_count >= 1 or confidence in ('HIGH', 'VERIFIED'):
            return 'MEDIUM'
        else:
            return 'LOW'

    def get_executive_summary_data(self, entries):
        """Generate structured data for PM Executive Summary."""
        # BUG FIX 6: Check for division by zero in coverage calculation
        summary = {
            'dimension_coverage': self.get_coverage_report(),
            'high_actionability_entries': [
                {
                    'id': e['id'],
                    'title': e.get('title', ''),
                    'pm_so_what': e.get('pm_so_what', ''),
                    'pm_dimensions': e.get('pm_dimensions', []),
                    'confidence': e.get('confidence', 'UNKNOWN'),
                }
                for e in entries
                if e.get('pm_actionability') == 'HIGH'
            ],
            'gaps': [
                self.DIMENSION_LABELS.get(dim, dim)
                for dim, data in self.get_coverage_report().items()
                if data['status'] == 'gap'
            ],
            'total_entries': len(entries),
            'pm_entries_by_dimension': dict(self.dimension_coverage),
        }
        return summary


class FinTechLensProcessor(BaseLensProcessor):
    """BUG FIX 3: Processes entries through the FinTech domain lens overlay.

    Inherits common dimension inference and coverage calculation from BaseLensProcessor.
    Adds FinTech-specific metadata, viability scores, geography inference, and executive summary.
    """

    DIMENSIONS = [
        'regulatory', 'payment_rails', 'trust_security', 'unit_economics',
        'acquisition', 'embedded_finance', 'credit_risk',
        'financial_inclusion', 'cross_border', 'funding_capital'
    ]

    DIMENSION_LABELS = {
        'regulatory': 'Regulatory & Compliance',
        'payment_rails': 'Payment Rails & Infrastructure',
        'trust_security': 'Trust, Security & Identity',
        'unit_economics': 'Unit Economics & Financial Modeling',
        'acquisition': 'Customer Acquisition & Retention',
        'embedded_finance': 'Embedded Finance & Platform Strategy',
        'credit_risk': 'Credit Risk & Underwriting',
        'financial_inclusion': 'Financial Inclusion & Impact',
        'cross_border': 'Cross-Border & Multi-Currency',
        'funding_capital': 'Funding Structure & Capital Strategy',
    }

    DIMENSION_KEYWORDS = {
        'regulatory': ['regulation', 'compliance', 'rbi', 'sebi', 'fca', 'occ', 'cfpb',
                       'license', 'nbfc', 'kyc', 'aml', 'pci-dss', 'guideline', 'circular',
                       'directive', 'mandate', 'sandbox', 'dpdp', 'gdpr', 'fatf', 'basel'],
        'payment_rails': ['upi', 'imps', 'neft', 'rtgs', 'swift', 'ach', 'sepa', 'payment rail',
                          'payment gateway', 'payment aggregator', 'npci', 'iso 20022',
                          'real-time payment', 'card network', 'visa', 'mastercard', 'rupay',
                          'nach', 'autopay', 'settlement'],
        'trust_security': ['fraud', 'identity', 'ekyc', 'aadhaar', 'biometric', 'authentication',
                           'encryption', 'tokenization', 'data security', 'cybersecurity',
                           'account takeover', 'phishing', 'digilocker', 'eidas', 'mfa',
                           'two-factor', 'pci', 'soc2'],
        'unit_economics': ['unit economics', 'revenue model', 'margin', 'take rate', 'interchange',
                           'mdr', 'spread', 'subscription', 'transaction fee', 'float income',
                           'cac', 'ltv', 'break-even', 'cost-to-serve', 'gross margin',
                           'net interest margin', 'loss ratio'],
        'acquisition': ['customer acquisition', 'onboarding', 'retention', 'churn', 'activation',
                        'conversion funnel', 'referral', 'app install', 'trust barrier',
                        'vernacular', 'day 30 retention', 'engagement', 'repeat usage'],
        'embedded_finance': ['embedded finance', 'baas', 'banking as a service', 'api banking',
                            'white-label', 'b2b2c', 'platform', 'embedded lending',
                            'embedded insurance', 'embedded payments', 'distribution',
                            'api-first', 'plug-and-play'],
        'credit_risk': ['credit risk', 'underwriting', 'credit score', 'cibil', 'fico',
                        'alternative data', 'npa', 'delinquency', 'default rate', 'dpd',
                        'fldg', 'collection', 'credit bureau', 'thin file', 'credit history',
                        'scoring model', 'machine learning underwriting'],
        'financial_inclusion': ['financial inclusion', 'unbanked', 'underbanked', 'tier 2',
                                'tier 3', 'rural', 'microfinance', 'pmjdy', 'gender gap',
                                'last mile', 'jan dhan', 'financial literacy', 'impact',
                                'bottom of pyramid', 'sachet', 'nano loan'],
        'cross_border': ['cross-border', 'remittance', 'forex', 'fx', 'multi-currency',
                         'correspondent banking', 'lrs', 'trade finance', 'stablecoin',
                         'international transfer', 'swift gpi', 'corridor'],
        'funding_capital': ['funding', 'venture capital', 'series a', 'series b', 'unicorn',
                           'co-lending', 'securitization', 'abs', 'warehouse lending',
                           'balance sheet', 'marketplace lending', 'ipo', 'valuation',
                           'debt capital', 'equity', 'raise', 'investor'],
    }

    # Geography keywords for auto-tagging
    GEOGRAPHY_KEYWORDS = {
        'india': ['india', 'rbi', 'sebi', 'irdai', 'upi', 'npci', 'aadhaar', 'pmjdy',
                  'nbfc', 'rupee', 'inr', 'cibil', 'neft', 'rtgs', 'imps', 'nach',
                  'tier 2', 'tier 3', 'lakh', 'crore', 'mfin', 'nabard'],
        'us': ['us', 'usa', 'occ', 'cfpb', 'sec', 'fincen', 'fico', 'ach', 'fed',
               'federal reserve', 'dollar', 'usd', 'fdic', 'finra'],
        'eu_uk': ['eu', 'uk', 'fca', 'ecb', 'psd2', 'psd3', 'mica', 'sepa', 'gdpr',
                  'eidas', 'euro', 'eur', 'gbp', 'sterling', 'boe'],
    }

    default_dimension = 'unit_economics'

    def _get_lens_key(self, field_type):
        """FinTech-specific lens key generation."""
        return f"ft_{field_type}"

    def _enrich_domain_fields(self, entry):
        """BUG FIX 3: Add FinTech-specific fields (viability and geography)."""
        if 'ft_viability' not in entry:
            entry['ft_viability'] = self._infer_viability(entry)

        if 'ft_geography' not in entry:
            entry['ft_geography'] = self._infer_geography(entry)

    def _infer_viability(self, entry):
        """Infer FinTech viability from entry characteristics."""
        content = (entry.get('content', '') + ' ' + entry.get('title', '')).lower()
        confidence = entry.get('confidence', 'UNKNOWN')

        high_signals = ['regulation', 'license', 'rbi', 'compliance', 'npa', 'default rate',
                       'take rate', 'margin', 'unit economics', 'cac', 'ltv', 'fldg',
                       'market size', 'tam', 'sam', 'funding', 'valuation']
        high_count = sum(1 for s in high_signals if s in content)

        if high_count >= 2 and confidence in ('HIGH', 'VERIFIED'):
            return 'HIGH'
        elif high_count >= 1 or confidence in ('HIGH', 'VERIFIED'):
            return 'MEDIUM'
        else:
            return 'LOW'

    def _infer_geography(self, entry):
        """Infer geographic relevance from entry content."""
        combined = (
            entry.get('title', '') + ' ' +
            entry.get('content', '') + ' ' +
            entry.get('summary', '')
        ).lower()

        geo_scores = {}
        for geo, keywords in self.GEOGRAPHY_KEYWORDS.items():
            geo_scores[geo] = sum(1 for kw in keywords if kw in combined)

        top_geo = max(geo_scores, key=geo_scores.get)
        if geo_scores[top_geo] >= 2:
            geo_map = {'india': 'India', 'us': 'US', 'eu_uk': 'EU/UK'}
            return geo_map.get(top_geo, 'Global')
        return 'Global'

    def get_executive_summary_data(self, entries):
        """Generate structured data for FinTech Executive Summary."""
        # BUG FIX 6: Check for division by zero in coverage calculation
        summary = {
            'dimension_coverage': self.get_coverage_report(),
            'high_viability_entries': [
                {
                    'id': e['id'],
                    'title': e.get('title', ''),
                    'ft_so_what': e.get('ft_so_what', ''),
                    'ft_dimensions': e.get('ft_dimensions', []),
                    'ft_geography': e.get('ft_geography', 'Global'),
                    'confidence': e.get('confidence', 'UNKNOWN'),
                }
                for e in entries
                if e.get('ft_viability') == 'HIGH'
            ],
            'gaps': [
                self.DIMENSION_LABELS.get(dim, dim)
                for dim, data in self.get_coverage_report().items()
                if data['status'] == 'gap'
            ],
            'total_entries': len(entries),
            'ft_entries_by_dimension': dict(self.dimension_coverage),
            'geography_distribution': dict(Counter(
                e.get('ft_geography', 'Global') for e in entries
            )),
        }
        return summary


class HTMLBuilder:
    """Builds final HTML web app from template and data."""

    def __init__(self, template_path):
        self.template_path = template_path
        self.template_content = None
        self._load_template()

    def _load_template(self):
        """Load HTML template from file."""
        if not os.path.exists(self.template_path):
            raise FileNotFoundError(f"Template not found: {self.template_path}")

        with open(self.template_path, 'r', encoding='utf-8') as f:
            self.template_content = f.read()

    def build(self, entries, title, stats, graph_data):
        """Build final HTML."""
        html = self.template_content

        # Minify JSON for embedding (compact)
        # BUG FIX 2: Escape < and > to prevent XSS injection in JSON strings
        knowledge_json = json.dumps(entries, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e')
        stats_json = json.dumps(stats, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e')
        graph_json = json.dumps(graph_data, separators=(',', ':')).replace('<', '\\u003c').replace('>', '\\u003e')

        # Replace placeholders
        html = html.replace('__KNOWLEDGE_DATA_PLACEHOLDER__', knowledge_json)
        html = html.replace('__TITLE_PLACEHOLDER__', title)
        html = html.replace('__GENERATED_DATE__', datetime.utcnow().isoformat() + 'Z')
        html = html.replace('__STATS_DATA__', stats_json)
        html = html.replace('__GRAPH_DATA__', graph_json)

        return html


def load_json_input(input_file=None):
    """Load JSON from file or stdin."""
    if input_file:
        if not os.path.exists(input_file):
            raise FileNotFoundError(f"Input file not found: {input_file}")
        with open(input_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    else:
        return json.load(sys.stdin)


def save_html_output(html_content, output_file):
    """Save HTML to file."""
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Assemble knowledge entries JSON into interactive HTML web app'
    )

    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--input', help='Input JSON file path')
    input_group.add_argument('--stdin', action='store_true', help='Read JSON from stdin')

    parser.add_argument('--output', required=True, help='Output HTML file path')
    parser.add_argument('--title', default='Knowledge Base', help='Knowledge base title')
    parser.add_argument('--template', help='Custom HTML template path')
    parser.add_argument('--theme', choices=['light', 'dark'], default='light', help='Default theme')
    parser.add_argument('--validate-only', action='store_true', help='Validate JSON without building')
    parser.add_argument('--stats', action='store_true', help='Print statistics to stderr')
    parser.add_argument('--no-graph', action='store_true', help='Disable knowledge graph')
    parser.add_argument('--max-entries', type=int, help='Limit entries (warn if exceeded)')
    parser.add_argument('--min-confidence', choices=['VERIFIED', 'HIGH', 'MEDIUM', 'LOW'],
                       help='Filter entries below confidence threshold')
    parser.add_argument('--learning-mode', action='store_true',
                       help='Activate learning mode: topological sort on dependencies, '
                            'assign learning tiers (Foundation/Intermediate/Advanced), '
                            'reorder entries by prerequisite chain')
    parser.add_argument('--visualization-only', action='store_true',
                       help='Accept pre-researched data (JSON claims/findings) and '
                            'skip to graph building + webapp assembly. '
                            'Input format: JSON array of claims or dict with entries/findings key')
    parser.add_argument('--input-format', choices=['auto', 'json', 'markdown', 'structured'],
                       default='auto',
                       help='Input format for --visualization-only mode. '
                            'auto: detect format, json: JSON claims, '
                            'markdown: ## heading sections, '
                            'structured: FINDING N: pattern (default: auto)')
    parser.add_argument('--fintech-lens', action='store_true',
                       help='Activate FinTech lens: tag entries with FinTech dimensions, '
                            'calculate viability scores, infer geography, generate '
                            'FinTech dimension coverage report and executive summary data. '
                            'See references/domain-fintech.md for full specification.')
    parser.add_argument('--pm-lens', action='store_true',
                       help='Activate PM lens: tag entries with PM dimensions, '
                            'calculate PM actionability scores, generate PM '
                            'dimension coverage report and executive summary data. '
                            'Adds pm_dimensions, pm_actionability, pm_so_what fields.')

    args = parser.parse_args()

    try:
        # ========== SECTION 1: INPUT LOADING & PARSING ==========
        # Determine input format for visualization-only mode
        input_format = getattr(args, 'input_format', 'auto')

        # Handle visualization-only with non-JSON formats
        if args.visualization_only and input_format in ('markdown', 'structured'):
            sys.stderr.write(f"Loading {input_format} input...\n")
            input_path = args.input if not args.stdin else None
            if input_path:
                with open(input_path, 'r', encoding='utf-8') as f:
                    raw_text = f.read()
            else:
                raw_text = sys.stdin.read()
            sys.stderr.write(f"Visualization-only mode: parsing {input_format} data...\n")
            viz_parser = VisualizationEntryParser()
            entries = viz_parser.parse(raw_text, input_format=input_format)
            sys.stderr.write(f"Parsed {len(entries)} entries from {input_format} data\n")
        elif args.visualization_only and input_format == 'auto':
            # Auto-detect: try JSON first, fall back to text parsing
            sys.stderr.write("Loading input (auto-detecting format)...\n")
            input_path = args.input if not args.stdin else None
            if input_path:
                with open(input_path, 'r', encoding='utf-8') as f:
                    raw_text = f.read()
            else:
                raw_text = sys.stdin.read()

            viz_parser = VisualizationEntryParser()
            try:
                raw_data = json.loads(raw_text)
                sys.stderr.write("Visualization-only mode: detected JSON input...\n")
                entries = viz_parser.parse(raw_data, input_format='json')
            except json.JSONDecodeError:
                sys.stderr.write("Visualization-only mode: not JSON, parsing as text...\n")
                entries = viz_parser.parse(raw_text, input_format='auto')
            sys.stderr.write(f"Parsed {len(entries)} entries from pre-researched data\n")
        else:
            # Standard JSON loading path
            sys.stderr.write("Loading JSON input...\n")
            raw_data = load_json_input(args.input if not args.stdin else None)

            if args.visualization_only:
                sys.stderr.write("Visualization-only mode: parsing pre-researched JSON...\n")
                viz_parser = VisualizationEntryParser()
                entries = viz_parser.parse(raw_data, input_format='json')
                sys.stderr.write(f"Parsed {len(entries)} entries from pre-researched data\n")
            else:
                entries = raw_data

        # ========== SECTION 2: VALIDATION & ENRICHMENT ==========
        # Validate
        sys.stderr.write("Validating entries...\n")
        validator = KnowledgeValidator()

        if not validator.validate_entries(entries):
            report = validator.get_report()
            sys.stderr.write(f"Validation failed with {report['error_count']} errors:\n")
            for error in report['errors'][:10]:
                sys.stderr.write(f"  - {error}\n")
            if len(report['errors']) > 10:
                sys.stderr.write(f"  ... and {len(report['errors']) - 10} more errors\n")
            return 1

        # Print validation report
        report = validator.get_report()
        if report['warning_count'] > 0:
            sys.stderr.write(f"Warnings ({report['warning_count']}):\n")
            for warning in report['warnings'][:5]:
                sys.stderr.write(f"  - {warning}\n")
            if len(report['warnings']) > 5:
                sys.stderr.write(f"  ... and {len(report['warnings']) - 5} more warnings\n")

        if report['auto_fix_count'] > 0:
            sys.stderr.write(f"Auto-fixes ({report['auto_fix_count']}):\n")
            for fix in report['auto_fixes'][:5]:
                sys.stderr.write(f"  - {fix}\n")
            if len(report['auto_fixes']) > 5:
                sys.stderr.write(f"  ... and {len(report['auto_fixes']) - 5} more auto-fixes\n")

        if args.validate_only:
            sys.stderr.write("Validation complete. Exiting due to --validate-only.\n")
            return 0

        # ========== SECTION 3: ENTRY ENRICHMENT & FILTERING ==========
        # Enrich entries
        sys.stderr.write("Enriching entries...\n")
        enricher = EntryEnricher()
        entries = enricher.enrich_entries(entries)

        # Filter by confidence if specified
        if args.min_confidence:
            confidence_levels = ['VERIFIED', 'HIGH', 'MEDIUM', 'LOW', 'UNKNOWN']
            min_idx = confidence_levels.index(args.min_confidence)
            orig_count = len(entries)
            entries = [e for e in entries if confidence_levels.index(e.get('confidence', 'UNKNOWN')) <= min_idx]
            filtered_count = orig_count - len(entries)
            sys.stderr.write(f"Filtered {filtered_count} entries below {args.min_confidence} confidence\n")

        # Check max entries
        if args.max_entries and len(entries) > args.max_entries:
            sys.stderr.write(f"WARNING: {len(entries)} entries exceeds max {args.max_entries}\n")

        # ========== SECTION 4: STATISTICS & KNOWLEDGE GRAPH ==========
        # Calculate statistics
        sys.stderr.write("Calculating statistics...\n")
        stats_calc = StatisticsCalculator()
        stats = stats_calc.calculate_stats(entries)

        if args.stats:
            sys.stderr.write("\n=== STATISTICS ===\n")
            sys.stderr.write(f"Total entries: {stats['total_entries']}\n")
            sys.stderr.write(f"Categories: {stats['total_categories']}\n")
            sys.stderr.write(f"Average content length: {stats['average_content_length']} words\n")
            sys.stderr.write(f"Coverage score: {stats['coverage_score']}%\n")
            sys.stderr.write(f"Confidence distribution: {stats['confidence_distribution']}\n")

        # Generate graph data
        graph_data = {}
        if not args.no_graph:
            sys.stderr.write("Generating knowledge graph...\n")
            graph_gen = GraphDataGenerator()
            graph_data = graph_gen.generate_graph(entries)
            sys.stderr.write(f"Graph: {graph_data['node_count']} nodes, {graph_data['edge_count']} edges\n")

        # ========== SECTION 5: DOMAIN LENS PROCESSING ==========
        # PM Lens: tag dimensions, calculate actionability, coverage
        if args.pm_lens:
            sys.stderr.write("PM Lens: tagging entries with PM dimensions and actionability...\n")
            pm_processor = PMLensProcessor()
            entries = pm_processor.process(entries)
            pm_coverage = pm_processor.get_coverage_report()
            pm_summary = pm_processor.get_executive_summary_data(entries)
            stats['pm_lens'] = True
            stats['pm_dimension_coverage'] = pm_coverage
            stats['pm_executive_summary'] = pm_summary
            stats['pm_high_actionability_count'] = len(pm_summary['high_actionability_entries'])
            stats['pm_gaps'] = pm_summary['gaps']
            sys.stderr.write(f"PM Lens: {stats['pm_high_actionability_count']} high-actionability entries\n")
            if pm_summary['gaps']:
                sys.stderr.write(f"PM Lens gaps: {', '.join(pm_summary['gaps'])}\n")

        # FinTech Lens: tag dimensions, calculate viability, infer geography, coverage
        if args.fintech_lens:
            sys.stderr.write("FinTech Lens: tagging entries with FinTech dimensions and viability...\n")
            ft_processor = FinTechLensProcessor()
            entries = ft_processor.process(entries)
            ft_coverage = ft_processor.get_coverage_report()
            ft_summary = ft_processor.get_executive_summary_data(entries)
            stats['fintech_lens'] = True
            stats['ft_dimension_coverage'] = ft_coverage
            stats['ft_executive_summary'] = ft_summary
            stats['ft_high_viability_count'] = len(ft_summary['high_viability_entries'])
            stats['ft_gaps'] = ft_summary['gaps']
            stats['ft_geography_distribution'] = ft_summary['geography_distribution']
            sys.stderr.write(f"FinTech Lens: {stats['ft_high_viability_count']} high-viability entries\n")
            if ft_summary['gaps']:
                sys.stderr.write(f"FinTech Lens gaps: {', '.join(ft_summary['gaps'])}\n")
            sys.stderr.write(f"FinTech Lens geography: {ft_summary['geography_distribution']}\n")

        # ========== SECTION 6: LEARNING MODE (OPTIONAL) ==========
        # Learning mode: topological sort and tier assignment
        if args.learning_mode:
            sys.stderr.write("Learning mode: performing topological sort on dependencies...\n")
            lm_processor = LearningModeProcessor()
            entries = lm_processor.process(entries, graph_data)
            tier_report = lm_processor.get_tier_report()
            sys.stderr.write(f"Learning tiers assigned: {tier_report}\n")
            stats['learning_mode'] = True
            stats['learning_tiers'] = tier_report

        # ========== SECTION 7: HTML BUILD & OUTPUT ==========
        # Build HTML
        sys.stderr.write("Building HTML...\n")
        template_path = args.template or os.path.join(
            os.path.dirname(__file__), '..', 'templates', 'web-app-shell.html'
        )

        if not os.path.exists(template_path):
            sys.stderr.write(f"ERROR: Template not found at {template_path}\n")
            return 2

        builder = HTMLBuilder(template_path)
        html = builder.build(entries, args.title, stats, graph_data)

        # Write output
        sys.stderr.write(f"Writing output to {args.output}...\n")
        save_html_output(html, args.output)

        output_size = os.path.getsize(args.output) / (1024 * 1024)
        sys.stderr.write(f"Success! Output: {output_size:.1f} MB\n")
        sys.stderr.write(f"Web app ready at: {os.path.abspath(args.output)}\n")

        return 0

    except json.JSONDecodeError as e:
        sys.stderr.write(f"JSON parse error: {e}\n")
        return 1
    except FileNotFoundError as e:
        sys.stderr.write(f"File not found: {e}\n")
        return 2
    except Exception as e:
        sys.stderr.write(f"Build error: {e}\n")
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 2


if __name__ == '__main__':
    sys.exit(main())
