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

        # Update node sizes based on connection count
        max_connections = max(connection_count.values()) if connection_count else 1
        for node in self.nodes:
            connections = connection_count.get(node['id'], 0)
            node['size'] = 10 + (30 * connections / max_connections) if max_connections > 0 else 10

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
        knowledge_json = json.dumps(entries, separators=(',', ':'))
        stats_json = json.dumps(stats, separators=(',', ':'))
        graph_json = json.dumps(graph_data, separators=(',', ':'))

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

    args = parser.parse_args()

    try:
        # Load JSON
        sys.stderr.write("Loading JSON input...\n")
        entries = load_json_input(args.input if not args.stdin else None)

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
