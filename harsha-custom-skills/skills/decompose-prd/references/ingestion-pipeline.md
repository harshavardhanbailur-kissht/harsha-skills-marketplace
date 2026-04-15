# PRD Ingestion Pipeline Reference

## Overview

The PRD ingestion pipeline is the first stage of decomposition, responsible for accepting PRDs in multiple formats and producing a normalized internal representation. This document covers format detection, extraction techniques for each format, normalization strategies, and output specifications.

## Format Detection Algorithm

The ingestion pipeline must detect and classify the input PRD format before extraction begins.

### Detection Priority Order

1. **File extension analysis**: Use file extension as primary indicator (`.pdf`, `.docx`, `.md`, `.html`, `.notion`, etc.)
2. **MIME type inspection**: For uploaded files, check Content-Type header
3. **Content inspection**: For pasted text or ambiguous sources:
   - HTML: Check for `<!DOCTYPE>`, `<html>` tags, or common HTML tag patterns
   - Markdown: Look for `#` headers, `[links]`, `***` separators, YAML frontmatter
   - JSON/Notion: Check for JSON structure or Notion block patterns
   - Plain text: Default fallback for unstructured content

### Format Categories

- **Binary formats**: PDF, DOCX (requires extraction libraries)
- **Markup formats**: HTML, Markdown (text-based parsing)
- **API formats**: Notion (requires MCP tool integration)
- **Structured text**: YAML frontmatter + Markdown
- **Unstructured text**: Pasted text, copy-paste content

### Detection Output

```python
FormatDetection = {
    "detected_format": "pdf" | "docx" | "markdown" | "html" | "notion" | "text",
    "confidence": 0.0 to 1.0,
    "source_type": "file" | "api" | "pasted_text",
    "encoding": "utf-8" | "binary",
    "metadata": {
        "filename": str,
        "size_bytes": int,
        "detected_language": str
    }
}
```

## PDF Extraction

### Extraction Tools

**Recommended primary tool**: `pdfplumber`
- Excellent table detection and extraction
- Maintains layout and spatial relationships
- Strong OCR capability for scanned PDFs
- Python library with straightforward API

**Fallback tool**: `PyMuPDF (fitz)`
- When pdfplumber fails or for high-fidelity text extraction
- Better handling of complex layouts
- Annotation extraction (comments, highlights)

### Extraction Strategy

#### Text Extraction with Layout Preservation

```python
import pdfplumber

with pdfplumber.open("prd.pdf") as pdf:
    for page_num, page in enumerate(pdf.pages):
        # Extract text with layout
        text = page.extract_text(layout=True)

        # Extract text with layout_mode for better structure
        text_detailed = page.extract_text_with_layout()

        # Get characters for custom parsing
        chars = page.chars

        # Extract bounding boxes for structural analysis
        bbox_data = page.objects
```

#### Table Extraction

```python
# Tables are extracted with full structure preservation
tables = page.extract_tables()

for table in tables:
    # table is a list of lists
    # Validate table structure (ragged vs rectangular)
    # Normalize missing cells
    # Preserve column headers
```

#### Image and Diagram Extraction

```python
# Extract images for later processing (OCR if needed)
images = page.images

for img in images:
    # Store image references with page/position
    # Flag for potential OCR or manual review
    # Store bounding box and context
```

#### Metadata Extraction

```python
# PDF metadata provides document context
metadata = pdf.metadata
# Extract: title, author, creation_date, subject, keywords

# Also extract outline/bookmarks
outline = pdf.outline
# Use as section markers and hierarchy indicators
```

### PDF Extraction Quality Assurance

- **Scanned PDFs**: Detect via absence of text layer, flag for OCR requirement
- **Complex layouts**: Multi-column, headers/footers, sidebars require special handling
- **Table detection**: Validate tables make semantic sense (not layout artifacts)
- **Section boundaries**: Use metadata outline + layout breaks to identify sections

## DOCX Extraction

### Extraction Tool

**Primary tool**: `python-docx`
- Native handling of Word document structure
- Preserves styling, tracked changes, comments
- Access to document properties and custom properties

### Extraction Strategy

#### Document Structure

```python
from docx import Document

doc = Document("prd.docx")

# Iterate through document elements in order
for para in doc.paragraphs:
    # para.text contains the text
    # para.style contains paragraph style info
    # para.level contains outline level (for hierarchy)

    # Extract runs for inline formatting
    for run in para.runs:
        text = run.text
        bold = run.bold
        italic = run.italic
        font_size = run.font.size

# Access sections (for headers/footers)
for section in doc.sections:
    header_text = section.header.paragraphs
    footer_text = section.footer.paragraphs
```

#### Table Extraction

```python
for table in doc.tables:
    rows = []
    for row in table.rows:
        cells = []
        for cell in row.cells:
            # Each cell can contain paragraphs
            cell_text = '\n'.join(p.text for p in cell.paragraphs)
            cells.append(cell_text)
        rows.append(cells)
```

#### Comments and Tracked Changes

```python
# Tracked changes indicate version history
# Can be important for understanding PRD evolution
from docx.oxml.shared import OxmlElement

def get_tracked_changes(doc):
    # Access revision elements
    # Extract author, date, type (insert/delete/format)
    pass

# Comments provide reviewer feedback
def get_comments(doc):
    # Extract comment ranges
    # Include author and resolution status
    pass
```

#### Styles and Hierarchy

```python
# Document structure is implied by styles
# Extract heading hierarchy from style levels
# Example: Heading 1, Heading 2, Heading 3

for para in doc.paragraphs:
    style_name = para.style.name
    if 'Heading' in style_name:
        level = extract_heading_level(style_name)
        # Use for section hierarchy
```

## Notion Extraction

### Using Notion MCP Tool

The `notion-fetch` tool provides structured access to Notion pages, returning content in Notion-flavored Markdown format.

```python
# Tool call: notion-fetch
# Parameters:
#   id: "{notion_page_url_or_uuid}"

# Returns: Notion-flavored markdown with block structures
```

### Content Structure

Notion pages contain various block types that need careful extraction:

```
Heading blocks:     # Heading 1, ## Heading 2, ### Heading 3
Paragraph blocks:   Regular text content
List blocks:        - Bullet items, 1. Numbered items
Table blocks:       Notion table format
Toggle blocks:      <details><summary>Title</summary>Content</details>
Callout blocks:     !!! note "Title"\n    Content
Code blocks:        ```language\ncode\n```
Image blocks:       ![Alt text](url)
Link/embed blocks:  [Link text](url)
Database references: Collections and linked databases
```

### Extraction Approach

1. **Fetch the page** using `notion-fetch` tool with the page URL
2. **Parse the returned Markdown** to identify block types
3. **Extract hierarchical structure** using heading levels
4. **Handle nested content** (toggles, indented lists)
5. **Resolve links** to related Notion pages if needed
6. **Convert to normalized format** (see Normalization section)

### Multi-Page Notion Documents

For PRDs split across multiple Notion pages:

```python
# Identify linked pages in the original page
# For each linked child page:
#   - Fetch with notion-fetch
#   - Mark as appendix or related section
#   - Preserve order from page links
# Merge all content with relative positioning
```

## HTML Extraction

### Extraction Tool

**Primary tool**: `BeautifulSoup4`
- Robust HTML parsing even with malformed markup
- CSS selector support for targeted extraction
- Whitespace and formatting handling

### Extraction Strategy

```python
from bs4 import BeautifulSoup

with open("prd.html") as f:
    soup = BeautifulSoup(f, 'html.parser')

# Extract main content (avoid headers, footers, sidebars)
main_content = soup.find('main') or soup.find('article') or soup.body

# Remove script and style tags
for script in soup(['script', 'style']):
    script.decompose()

# Extract text while preserving structure
text = main_content.get_text(separator='\n', strip=True)

# Extract headings for hierarchy
headings = main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
hierarchy = [(int(h.name[1]), h.get_text()) for h in headings]

# Extract tables
tables = main_content.find_all('table')
for table in tables:
    # Parse table rows and cells
    rows = []
    for tr in table.find_all('tr'):
        cells = [td.get_text(strip=True) for td in tr.find_all(['td', 'th'])]
        rows.append(cells)

# Extract lists
lists = main_content.find_all(['ul', 'ol'])
for list_elem in lists:
    items = [li.get_text(strip=True) for li in list_elem.find_all('li')]
```

### Web-Specific Patterns

- **Navigation elements**: Exclude from content extraction
- **Metadata**: Look for `<meta>` tags with description, keywords
- **Open Graph tags**: Extract og:title, og:description for document metadata
- **Schema.org markup**: Look for structured data that indicates sections
- **Inline styles**: Preserve emphasis markers (bold, italic) from `<strong>`, `<em>` tags

## Markdown Parsing

### Frontmatter Extraction

```python
import yaml

# Markdown PRDs often include YAML frontmatter
with open("prd.md") as f:
    content = f.read()

# Extract frontmatter (between --- delimiters)
if content.startswith('---'):
    _, frontmatter_str, markdown_content = content.split('---', 2)
    frontmatter = yaml.safe_load(frontmatter_str)
    # Extract: title, author, date, version, status
else:
    markdown_content = content
    frontmatter = {}
```

### Section Hierarchy

```python
import re

# Extract heading structure using regex
heading_pattern = r'^(#{1,6})\s+(.+)$'
headings = []
current_level = 0

for line in markdown_content.split('\n'):
    match = re.match(heading_pattern, line)
    if match:
        level = len(match.group(1))
        title = match.group(2)
        headings.append({
            'level': level,
            'title': title,
            'line_num': line_number
        })
```

### Content Parsing

```python
# Preserve markdown formatting for later analysis
# Extract inline code: `code`
# Extract bold: **text** or __text__
# Extract lists: - item or 1. item
# Extract links: [text](url)
# Extract code blocks: ```language\ncode\n```
# Extract blockquotes: > quoted text
```

## Multi-File PRD Handling

Many PRDs span multiple files: main document + appendices, supplementary files, external links.

### Discovery Strategy

1. **File system scan**: Check same directory as main PRD for related files
   - Pattern: `*-appendix*`, `*-supplementary*`, `part-*`
   - Convention: numbered files like `prd.md`, `prd-2.md`, `prd-appendix.md`

2. **Document links**: Extract references from main document
   - Markdown: `[Appendix](appendix.md)`
   - DOCX: Track linked document references
   - HTML: Check for navigation links or TOC references

3. **Notion relationships**: Follow linked database entries and child pages

### Ordering and Assembly

```python
OrderedPRD = {
    "main_document": ExtractedContent,
    "appendices": [
        {
            "title": str,
            "file": str,
            "content": ExtractedContent,
            "type": "appendix" | "supplementary" | "reference"
        }
    ],
    "image_references": [
        {
            "original_reference": str,
            "resolved_path": str,
            "used_in_section": str
        }
    ]
}
```

### External References

- Store URLs to external documents (don't download unless explicitly needed)
- Mark as "reference" vs "required" content
- Include contextual snippet from PRD showing how it's referenced

## Normalization: Converting to Unified Representation

All extracted content, regardless of source format, is normalized to a standard internal structure.

### NormalizedPRD Schema

```python
NormalizedPRD = {
    "metadata": {
        "title": str,
        "version": str,
        "status": str,
        "last_updated": datetime,
        "source_format": "pdf" | "docx" | "markdown" | "html" | "notion",
        "source_file": str,
        "author": str,
    },
    "sections": [
        {
            "id": "section_{number}",
            "heading": str,
            "level": int,  # 1-6, representing hierarchy depth
            "content": str,
            "subsections": [SectionNode],
            "type": "inferred_section_type"  # see Section Identification
        }
    ],
    "structured_elements": {
        "tables": [
            {
                "id": "table_{number}",
                "title": str,
                "headers": [str],
                "rows": [[str]]
            }
        ],
        "lists": [
            {
                "id": "list_{number}",
                "items": [str],
                "ordered": bool
            }
        ],
        "code_blocks": [
            {
                "id": "code_{number}",
                "language": str,
                "content": str
            }
        ],
        "images": [
            {
                "id": "image_{number}",
                "reference": str,
                "alt_text": str,
                "context": str  # surrounding text
            }
        ]
    },
    "requirements": [
        {
            "id": "req_{number}",
            "text": str,
            "category": "functional" | "non-functional" | "constraint",
            "source_section": str,
            "priority": "must" | "should" | "could",
            "acceptance_criteria": [str]
        }
    ]
}
```

### Normalization Process

1. **Text cleaning**:
   - Remove excessive whitespace
   - Normalize line endings
   - Preserve intentional formatting (lists, tables, code blocks)

2. **Section hierarchy assignment**:
   - Assign numeric IDs to sections
   - Maintain parent-child relationships
   - Flatten or restructure if inconsistent

3. **Element extraction**:
   - Identify and extract tables, lists, code blocks, images
   - Assign sequential IDs
   - Store references to original location

4. **Requirement extraction**:
   - See Section Identification below

5. **Metadata enrichment**:
   - Infer missing metadata from document
   - Standardize date formats
   - Normalize version strings

## Section Identification Heuristics

PRD sections can have many different naming conventions. The pipeline uses pattern matching and keyword analysis to identify the semantic type regardless of the actual heading name.

### Problem/Context Section

**Patterns**:
- "Problem", "Problem Statement", "Background", "Context", "Current State", "As-is", "Situation"
- "Why are we building this?", "What problem are we solving?"

**Content signals**:
- Describes current pain points, user frustrations
- May include metrics showing the problem's scope
- References existing systems or processes

### Goals/Objectives Section

**Patterns**:
- "Goals", "Objectives", "Desired Outcomes", "Vision", "Success Criteria", "OKRs"
- "What do we want to achieve?", "Desired end state"

**Content signals**:
- Measurable outcomes (numbers, percentages)
- Business impact statements
- Timeframe indicators

### Requirements Section

**Patterns**:
- "Requirements", "Functional Requirements", "FR", "User Stories", "Features", "Specifications"
- May be subdivided: "Functional Requirements", "Non-Functional Requirements", "Technical Requirements"

**Content signals**:
- Use of "shall", "must", "should", "could"
- Acceptance criteria (Given/When/Then format)
- Referenced to user roles or personas

### Timeline/Roadmap Section

**Patterns**:
- "Timeline", "Roadmap", "Milestones", "Schedule", "Phases", "Release Plan"
- "Execution Plan", "Implementation Plan"

**Content signals**:
- Dates, quarters, sprint numbers
- Sequencing information
- Dependencies between milestones

### Constraints/Assumptions Section

**Patterns**:
- "Constraints", "Assumptions", "Dependencies", "Risks", "Out of Scope", "Non-Goals"

**Content signals**:
- "We assume...", "Given that...", "Constraint: ...", "Risk: ..."
- "Out of scope", "Will not", "Not covered in this PRD"

### Identification Algorithm

```python
def identify_section_type(heading: str, content: str) -> str:
    heading_lower = heading.lower()

    # Check for exact keyword matches first (highest priority)
    if any(kw in heading_lower for kw in ['problem', 'context', 'background']):
        return 'problem'
    if any(kw in heading_lower for kw in ['goal', 'objective', 'vision']):
        return 'goals'
    if any(kw in heading_lower for kw in ['requirement', 'feature', 'specification']):
        return 'requirements'
    if any(kw in heading_lower for kw in ['timeline', 'roadmap', 'milestone']):
        return 'timeline'
    if any(kw in heading_lower for kw in ['constraint', 'assumption', 'risk', 'scope']):
        return 'constraints'

    # Check content patterns (secondary)
    requirement_indicators = count_pattern_matches(content, [
        r'\bmust\b', r'\bshall\b', r'\bshould\b', r'\bcould\b',
        r'Given.*When.*Then', r'Acceptance Criteria'
    ])
    if requirement_indicators > 3:
        return 'requirements'

    goal_indicators = count_pattern_matches(content, [
        r'\bmetric', r'\bKPI', r'\bobjective', r'\btarget', r'\d+%'
    ])
    if goal_indicators > 2:
        return 'goals'

    return 'general'
```

## Output Format

The normalized PRD is output as JSON or Python dict with the structure defined in NormalizedPRD Schema above. This normalized form is the input to the Decomposition Engine.

### Example Normalized Output

```json
{
  "metadata": {
    "title": "User Authentication Platform PRD",
    "version": "1.0",
    "status": "Active",
    "source_format": "docx",
    "source_file": "auth-prd.docx"
  },
  "sections": [
    {
      "id": "section_1",
      "heading": "Problem Statement",
      "level": 1,
      "type": "problem",
      "content": "Currently, users cannot securely authenticate across our platform...",
      "subsections": []
    },
    {
      "id": "section_2",
      "heading": "Success Metrics",
      "level": 1,
      "type": "goals",
      "content": "We aim to achieve 99.99% authentication uptime..."
    }
  ],
  "requirements": [
    {
      "id": "req_001",
      "text": "System must support OAuth 2.0 and SAML authentication methods",
      "category": "functional",
      "priority": "must",
      "source_section": "section_2"
    }
  ]
}
```

## Quality Assurance

### Extraction Validation Checks

- ✓ No blank required fields (title, version, main content)
- ✓ Section hierarchy is consistent (no gaps in levels)
- ✓ All extracted elements (tables, lists, code) are validly formatted
- ✓ Image references point to accessible locations
- ✓ No content loss (extracted text ≥ 95% of original by character count)

### Format-Specific Validation

- **PDF**: Verify text layer exists; scanned PDFs need OCR flag
- **DOCX**: Check tracked changes are captured; comments preserved
- **Notion**: Verify all block types converted correctly; nested blocks flattened appropriately
- **HTML**: Confirm main content identified correctly; navigation excluded
- **Markdown**: Validate YAML frontmatter parsed; hierarchy correct

### Normalization Validation

- Section types identified with reasonable confidence
- Requirement extraction yields 3-20 requirements per major section
- No duplicate content between sections
- Cross-references to other sections are preserved as annotations
