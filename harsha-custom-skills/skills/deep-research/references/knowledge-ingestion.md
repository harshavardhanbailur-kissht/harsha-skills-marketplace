# Knowledge Ingestion Pipeline

**Purpose**: Convert raw input (PDFs, web pages, spreadsheets, code, text) into structured knowledge entries.
**Usage**: Implement in Phase 3 of the Deep Research Synthesizer pipeline.
**Output**: Clean, normalized knowledge entries ready for QA.
**Last Updated**: 2026-02-09

---

## Table of Contents

1. Input Type Detection
2. Document Processing Pipelines
3. Data Normalization Pipeline
4. Metadata Extraction
5. Batch Processing
6. Error Handling

---

## Input Type Detection

When a user provides input, automatically route it to the correct processor.

### Decision Tree

```
START: User provides input (file, URL, text, etc.)
│
├─ Is it a file path?
│  ├─ YES → Check extension
│  │  ├─ .pdf → PDF Processing Pipeline
│  │  ├─ .docx / .doc → DOCX Processing Pipeline
│  │  ├─ .xlsx / .csv → Spreadsheet Processing Pipeline
│  │  ├─ .py / .js / .java / etc. → Code File Processing Pipeline
│  │  └─ .txt → Raw Text Processing Pipeline
│  └─ NO → Continue to next check
│
├─ Is it a URL?
│  ├─ YES → Check domain
│  │  ├─ notion.so → Notion Page Processing
│  │  └─ Any other domain → Web Content Processing
│  └─ NO → Continue to next check
│
├─ Is it structured data?
│  ├─ YES → Check format
│  │  ├─ JSON pattern detected → Parse as JSON data
│  │  └─ CSV pattern detected → Parse as CSV data
│  └─ NO → Continue to next check
│
└─ Is it raw text?
   ├─ YES → Check for structure
   │  ├─ Headings (lines ending with ":") detected → Raw Text Processing
   │  ├─ Lists (-, *, •) detected → Raw Text Processing
   │  └─ Paragraphs only → Raw Text Processing
   └─ NO → Unknown format (log warning, attempt raw text)
```

### Implementation

```python
import os
from urllib.parse import urlparse

def detect_input_type(input_value):
    """
    Auto-detect input type and return appropriate processor.

    Args:
        input_value: File path, URL, or raw text

    Returns:
        dict: {type, processor_name, params}
    """

    # Check if file path
    if os.path.isfile(input_value):
        ext = os.path.splitext(input_value)[1].lower()
        return route_by_extension(ext, input_value)

    # Check if URL
    try:
        parsed = urlparse(input_value)
        if parsed.scheme in ["http", "https"]:
            if "notion.so" in parsed.netloc:
                return {
                    "type": "url",
                    "format": "notion",
                    "processor": "notion_page_processor",
                    "params": {"url": input_value}
                }
            else:
                return {
                    "type": "url",
                    "format": "web",
                    "processor": "web_content_processor",
                    "params": {"url": input_value}
                }
    except:
        pass

    # Check if structured data (JSON/CSV pattern)
    if is_json_pattern(input_value):
        return {
            "type": "structured",
            "format": "json",
            "processor": "json_parser",
            "params": {"data": input_value}
        }

    if is_csv_pattern(input_value):
        return {
            "type": "structured",
            "format": "csv",
            "processor": "csv_parser",
            "params": {"data": input_value}
        }

    # Default: Raw text
    return {
        "type": "text",
        "format": "raw",
        "processor": "raw_text_processor",
        "params": {"text": input_value}
    }

def route_by_extension(ext, filepath):
    """Route file to appropriate processor based on extension."""
    routes = {
        ".pdf": {"processor": "pdf_processor", "format": "pdf"},
        ".docx": {"processor": "docx_processor", "format": "docx"},
        ".doc": {"processor": "docx_processor", "format": "doc"},
        ".xlsx": {"processor": "spreadsheet_processor", "format": "xlsx"},
        ".xls": {"processor": "spreadsheet_processor", "format": "xls"},
        ".csv": {"processor": "spreadsheet_processor", "format": "csv"},
        ".py": {"processor": "code_processor", "format": "python"},
        ".js": {"processor": "code_processor", "format": "javascript"},
        ".java": {"processor": "code_processor", "format": "java"},
        ".go": {"processor": "code_processor", "format": "go"},
        ".ts": {"processor": "code_processor", "format": "typescript"},
        ".txt": {"processor": "raw_text_processor", "format": "text"},
        ".md": {"processor": "raw_text_processor", "format": "markdown"},
    }

    route = routes.get(ext, {"processor": "raw_text_processor", "format": "unknown"})
    return {
        "type": "file",
        "filepath": filepath,
        "processor": route["processor"],
        "format": route["format"],
        "params": {"filepath": filepath}
    }
```

---

## Document Processing Pipelines

### PDF Processing

**Goal**: Extract text, tables, metadata, and handle image-based PDFs (scanned documents).

#### Implementation

```python
import pdfplumber
import pytesseract
from PIL import Image
import io

def process_pdf(filepath):
    """
    Extract content from PDF.

    Returns:
        dict: {text, tables, metadata, images_description}
    """
    result = {
        "text": "",
        "tables": [],
        "metadata": {},
        "images": [],
        "pages": []
    }

    with pdfplumber.open(filepath) as pdf:
        # Extract metadata
        result["metadata"] = {
            "title": pdf.metadata.get("Title"),
            "author": pdf.metadata.get("Author"),
            "subject": pdf.metadata.get("Subject"),
            "creation_date": pdf.metadata.get("CreationDate"),
            "page_count": len(pdf.pages)
        }

        # Process each page
        for page_num, page in enumerate(pdf.pages, 1):
            page_content = {
                "page_num": page_num,
                "text": "",
                "tables": [],
                "images": []
            }

            # Extract text
            text = page.extract_text()
            if text:
                page_content["text"] = text
                result["text"] += f"\n--- Page {page_num} ---\n{text}"
            else:
                # Likely a scanned image, attempt OCR
                page_content["text"] = "IMAGE-BASED (requires OCR)"
                result["images"].append({
                    "page": page_num,
                    "note": "Scanned image, OCR not applied (suggest tesseract)"
                })

            # Extract tables
            tables = page.extract_tables()
            if tables:
                for table_idx, table in enumerate(tables):
                    page_content["tables"].append({
                        "table_num": table_idx,
                        "data": table,
                        "headers": table[0] if table else []
                    })
                    result["tables"].extend(page_content["tables"])

            result["pages"].append(page_content)

    return result
```

#### Usage

```python
pdf_result = process_pdf("/path/to/document.pdf")

# Output structure:
# {
#   "text": "Page 1 content...\n--- Page 2 ---\nPage 2 content...",
#   "tables": [{"table_num": 0, "headers": [...], "data": [...]}],
#   "metadata": {"title": "...", "author": "...", "page_count": 5},
#   "images": [{"page": 3, "note": "Scanned image, OCR not applied"}],
#   "pages": [...]
# }
```

#### Handling Scanned PDFs

If OCR is needed:

```python
import pytesseract
from pdf2image import convert_from_path

def extract_text_from_scanned_pdf(filepath):
    """Extract text from image-based (scanned) PDF using Tesseract OCR."""
    try:
        # Convert PDF pages to images
        images = convert_from_path(filepath)

        all_text = ""
        for page_num, image in enumerate(images, 1):
            # Apply OCR
            text = pytesseract.image_to_string(image)
            all_text += f"\n--- Page {page_num} (OCR) ---\n{text}"

        return all_text
    except Exception as e:
        return f"OCR failed: {str(e)}. Install tesseract-ocr system package."
```

#### Quality Considerations

- **Text extraction**: pdfplumber is accurate for digital PDFs (>95% accuracy)
- **Tables**: Extract as structured data when possible
- **Metadata**: Capture title, author, date (useful for normalization)
- **Scanned PDFs**: Mark as `{method: "OCR"}` with confidence warning

---

### DOCX Processing

**Goal**: Preserve document structure, headings, tables, and formatting.

#### Implementation

```python
from docx import Document
from docx.enum.text import WD_PARAGRAPH_STYLE

def process_docx(filepath):
    """
    Extract content from DOCX, preserving structure.

    Returns:
        dict: {text, structure, tables, metadata}
    """
    doc = Document(filepath)
    result = {
        "text": "",
        "structure": [],  # Hierarchical: headings + content
        "tables": [],
        "metadata": {
            "core_properties": doc.core_properties.__dict__,
            "styles": list(doc.styles)
        }
    }

    current_section = None
    current_subsection = None

    for para in doc.paragraphs:
        style_name = para.style.name

        # Detect heading level
        if style_name.startswith("Heading"):
            level = int(style_name.split()[-1]) if style_name[-1].isdigit() else 1

            heading_text = para.text
            result["text"] += f"\n{'#' * level} {heading_text}\n"

            if level == 1:
                current_section = {
                    "title": heading_text,
                    "level": level,
                    "content": [],
                    "subsections": []
                }
                result["structure"].append(current_section)
            elif level == 2 and current_section:
                current_subsection = {
                    "title": heading_text,
                    "level": level,
                    "content": []
                }
                current_section["subsections"].append(current_subsection)

        elif para.text.strip():  # Regular paragraph
            result["text"] += f"{para.text}\n"

            if current_subsection:
                current_subsection["content"].append(para.text)
            elif current_section:
                current_section["content"].append(para.text)

        # Extract text runs with formatting hints
        for run in para.runs:
            if run.bold:
                result["text"] += f"**{run.text}**"
            elif run.italic:
                result["text"] += f"*{run.text}*"

    # Extract tables
    for table_idx, table in enumerate(doc.tables):
        table_data = {
            "table_num": table_idx,
            "headers": [cell.text for cell in table.rows[0].cells] if table.rows else [],
            "rows": []
        }

        for row in table.rows[1:]:
            table_data["rows"].append([cell.text for cell in row.cells])

        result["tables"].append(table_data)
        result["text"] += f"\n[TABLE {table_idx + 1}]\n"

    # Extract core properties
    result["metadata"]["title"] = doc.core_properties.title
    result["metadata"]["author"] = doc.core_properties.author
    result["metadata"]["created"] = doc.core_properties.created
    result["metadata"]["modified"] = doc.core_properties.modified

    return result
```

#### Usage

```python
docx_result = process_docx("/path/to/document.docx")

# Output includes hierarchical structure:
# {
#   "structure": [
#     {
#       "title": "Section 1",
#       "level": 1,
#       "content": ["para 1", "para 2"],
#       "subsections": [
#         {"title": "1.1", "level": 2, "content": [...]}
#       ]
#     }
#   ],
#   "tables": [...],
#   "metadata": {...}
# }
```

---

### Spreadsheet Processing (XLSX, CSV)

**Goal**: Convert tabular data into knowledge entries.

#### Strategy

Two approaches depending on data:

**Approach A: One entry per logical group** (if data is already categorized)
```
Spreadsheet:
Category | Item | Description
---------|------|-------------
Food     | Apple| Red fruit
Food     | Banana | Yellow fruit
Tech     | Laptop | Computer

Result: 3 entries (one per row or group)
```

**Approach B: One entry per sheet** (if sheet is a coherent document)
```
Spreadsheet: "Q1-Sales.xlsx"
├─ Sheet 1: Sales by region
├─ Sheet 2: Costs by department
└─ Sheet 3: Projections

Result: 3 entries (one per sheet)
```

#### Implementation

```python
import pandas as pd
import csv

def process_spreadsheet(filepath, mode="rows"):
    """
    Process XLSX or CSV into knowledge entries.

    Args:
        filepath: Path to .xlsx or .csv file
        mode: "rows" (one entry per row), "sheets" (one entry per sheet)

    Returns:
        list: [entry, entry, ...]
    """

    entries = []

    if filepath.endswith(".csv"):
        df = pd.read_csv(filepath)
        sheets = {"default": df}
    else:  # .xlsx
        xls = pd.ExcelFile(filepath)
        sheets = {sheet: pd.read_excel(filepath, sheet_name=sheet) for sheet in xls.sheet_names}

    if mode == "sheets":
        # One entry per sheet
        for sheet_name, df in sheets.items():
            entry = {
                "title": sheet_name,
                "content": df_to_markdown(df),
                "metadata": {
                    "source_type": "spreadsheet_sheet",
                    "row_count": len(df),
                    "column_count": len(df.columns)
                }
            }
            entries.append(entry)

    elif mode == "rows":
        # One entry per row (or logical group)
        for sheet_name, df in sheets.items():
            # Detect if first row is header
            headers = df.columns.tolist()

            # Infer key column (likely "Name", "Title", "Item", etc.)
            key_column = infer_key_column(headers)

            for idx, row in df.iterrows():
                entry = {
                    "title": str(row[key_column]) if key_column else f"Row {idx}",
                    "content": row_to_text(row, headers),
                    "metadata": {
                        "source_type": "spreadsheet_row",
                        "sheet": sheet_name,
                        "row_number": idx + 2  # +2 for 1-indexing and header
                    },
                    "data": row.to_dict()
                }
                entries.append(entry)

    return entries

def infer_key_column(headers):
    """Find the most likely title/name column."""
    key_patterns = ["name", "title", "item", "label", "description", "topic"]

    for pattern in key_patterns:
        for header in headers:
            if pattern.lower() in header.lower():
                return header

    return headers[0]  # Default to first column

def df_to_markdown(df):
    """Convert DataFrame to Markdown table."""
    return df.to_markdown(index=False)

def row_to_text(row, headers):
    """Convert row to readable text."""
    lines = []
    for header, value in zip(headers, row):
        if pd.notna(value):
            lines.append(f"- **{header}**: {value}")
    return "\n".join(lines)
```

#### Handling Formulas

Extract business logic from formulas:

```python
def extract_formulas(filepath):
    """Extract Excel formulas for documentation."""
    import openpyxl

    wb = openpyxl.load_workbook(filepath)
    formulas = []

    for sheet in wb.sheetnames:
        ws = wb[sheet]
        for row in ws.iter_rows():
            for cell in row:
                if cell.data_type == 'f':  # Formula cell
                    formulas.append({
                        "sheet": sheet,
                        "cell": cell.coordinate,
                        "formula": cell.value
                    })

    return formulas

# Example output:
# [
#   {"sheet": "Q1", "cell": "C5", "formula": "=SUM(C2:C4)"},
#   {"sheet": "Projections", "cell": "B10", "formula": "=A10*1.15"}
# ]
```

---

### Web Content Processing

**Goal**: Extract main content from web pages, ignore navigation/ads/sidebars.

#### Using WebFetch Tool

```python
def process_web_content(url):
    """
    Extract knowledge from web page.

    Args:
        url: URL to fetch

    Returns:
        dict: {title, content, metadata}
    """

    # Use WebFetch MCP tool
    response = webfetch(
        url=url,
        prompt="""
        Extract the main content from this page.
        Ignore: navigation, ads, sidebars, footer, copyright.
        Focus on: main article/content.
        Return: Title, Summary (150 words), Full Content
        Output as JSON with keys: title, summary, content
        """
    )

    parsed = json.loads(response)

    return {
        "title": parsed.get("title"),
        "summary": parsed.get("summary"),
        "content": parsed.get("content"),
        "source_url": url,
        "metadata": {
            "fetched_date": datetime.now().isoformat(),
            "page_type": infer_page_type(parsed.get("content"))
        }
    }

def infer_page_type(content):
    """Infer: article, documentation, product, news, etc."""
    content_lower = content.lower()

    if "published" in content_lower and "by" in content_lower:
        return "article"
    elif "documentation" in content_lower or "api" in content_lower:
        return "documentation"
    elif "product" in content_lower or "features" in content_lower:
        return "product"
    elif "news" in content_lower or "announcement" in content_lower:
        return "news"
    else:
        return "general"
```

#### Handling Paywalled Content

```python
def handle_paywalled_content(url):
    """Handle content behind paywall gracefully."""

    try:
        content = webfetch(url, "Extract content")
        if "subscribe" in content.lower() or "paywall" in content.lower():
            return {
                "title": "PAYWALL",
                "content": "This content is behind a paywall. Not accessible.",
                "confidence": "UNKNOWN",
                "action": "Use publicly available summary or find alternative source"
            }
        return content
    except Exception as e:
        return {
            "title": "UNREACHABLE",
            "content": f"Could not fetch: {str(e)}",
            "confidence": "UNKNOWN",
            "action": "Try later or find cached version"
        }
```

---

### Notion Page Processing

**Goal**: Preserve Notion's block structure and database properties.

#### Implementation

```python
def process_notion_page(page_url):
    """
    Extract content from Notion page using Notion MCP tools.

    Args:
        page_url: https://notion.so/page-id or page-id

    Returns:
        dict: {title, content, properties, sub_pages}
    """

    # Use Notion MCP tool: notion-fetch
    page_data = notion_fetch(page_url)

    result = {
        "title": page_data.get("properties", {}).get("Title"),
        "content": parse_notion_blocks(page_data.get("blocks")),
        "properties": page_data.get("properties", {}),
        "sub_pages": [],
        "databases": []
    }

    # Handle sub-pages recursively
    for sub_page_id in page_data.get("sub_pages", []):
        result["sub_pages"].append(process_notion_page(sub_page_id))

    # Handle linked databases
    for db_id in page_data.get("databases", []):
        result["databases"].append(process_notion_database(db_id))

    return result

def parse_notion_blocks(blocks):
    """Convert Notion blocks to markdown."""
    markdown = ""

    for block in blocks:
        block_type = block.get("type")

        if block_type == "paragraph":
            markdown += f"{block['paragraph']['rich_text']}\n"
        elif block_type == "heading_1":
            markdown += f"# {block['heading_1']['rich_text']}\n"
        elif block_type == "heading_2":
            markdown += f"## {block['heading_2']['rich_text']}\n"
        elif block_type == "bulleted_list_item":
            markdown += f"- {block['bulleted_list_item']['rich_text']}\n"
        elif block_type == "numbered_list_item":
            markdown += f"1. {block['numbered_list_item']['rich_text']}\n"
        elif block_type == "table":
            markdown += parse_notion_table(block['table']) + "\n"
        elif block_type == "code":
            markdown += f"```{block['code']['language']}\n{block['code']['rich_text']}\n```\n"

    return markdown

def process_notion_database(db_id):
    """Extract Notion database as structured data."""

    # Use Notion MCP: notion-search or notion-fetch for database
    db_data = notion_fetch(db_id)

    entries = []
    for item in db_data.get("items", []):
        entry = {
            "title": item.get("properties", {}).get("Name"),
            "properties": item.get("properties", {}),
            "id": item.get("id")
        }
        entries.append(entry)

    return {
        "title": db_data.get("title"),
        "entries": entries,
        "property_schema": db_data.get("schema", {})
    }
```

---

### Code File Processing

**Goal**: Extract documentation, architecture, and notable patterns from code.

#### Implementation

```python
import ast
import re

def process_code_file(filepath, language=None):
    """
    Extract documentation and structure from code file.

    Args:
        filepath: Path to code file
        language: Programming language (auto-detect from extension)

    Returns:
        dict: {title, content, structure, documentation}
    """

    with open(filepath, 'r', encoding='utf-8') as f:
        code = f.read()

    if language is None:
        language = detect_language(filepath)

    if language == "python":
        return process_python_file(code, filepath)
    elif language == "javascript":
        return process_javascript_file(code, filepath)
    else:
        return process_generic_code_file(code, filepath, language)

def process_python_file(code, filepath):
    """Extract Python docstrings, classes, functions, TODOs."""

    result = {
        "title": os.path.basename(filepath),
        "language": "python",
        "content": "",
        "functions": [],
        "classes": [],
        "todos": [],
        "docstrings": []
    }

    # Parse module docstring
    tree = ast.parse(code)

    if ast.get_docstring(tree):
        result["docstrings"].append({
            "type": "module",
            "text": ast.get_docstring(tree)
        })

    # Extract functions
    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            func_info = {
                "name": node.name,
                "docstring": ast.get_docstring(node),
                "args": [arg.arg for arg in node.args.args],
                "line_number": node.lineno
            }
            result["functions"].append(func_info)

        elif isinstance(node, ast.ClassDef):
            class_info = {
                "name": node.name,
                "docstring": ast.get_docstring(node),
                "methods": [n.name for n in node.body if isinstance(n, ast.FunctionDef)],
                "line_number": node.lineno
            }
            result["classes"].append(class_info)

    # Extract TODOs and FIXMEs
    for match in re.finditer(r"#\s*(TODO|FIXME|BUG|HACK):\s*(.+)", code):
        result["todos"].append({
            "type": match.group(1),
            "text": match.group(2)
        })

    # Build content summary
    result["content"] = generate_code_summary(result, filepath)

    return result

def generate_code_summary(parsed, filepath):
    """Generate readable summary of code file."""
    lines = [f"# {os.path.basename(filepath)}"]

    if parsed.get("docstrings"):
        lines.append("\n## Overview\n")
        lines.append(parsed["docstrings"][0].get("text", ""))

    if parsed.get("classes"):
        lines.append("\n## Classes\n")
        for cls in parsed["classes"]:
            lines.append(f"- **{cls['name']}**: {cls.get('docstring', 'No description')}")
            if cls.get("methods"):
                for method in cls["methods"]:
                    lines.append(f"  - `{method}()`")

    if parsed.get("functions"):
        lines.append("\n## Functions\n")
        for func in parsed["functions"]:
            args = ", ".join(func.get("args", []))
            lines.append(f"- **{func['name']}**({args})")
            if func.get("docstring"):
                lines.append(f"  - {func['docstring']}")

    if parsed.get("todos"):
        lines.append("\n## TODOs\n")
        for todo in parsed["todos"]:
            lines.append(f"- [{todo['type']}] {todo['text']}")

    return "\n".join(lines)
```

---

### Raw Text Processing

**Goal**: Detect structure in plain text (headings, lists, paragraphs) and segment by topic.

#### Implementation

```python
def process_raw_text(text):
    """
    Detect structure in raw text: headings, lists, Q&A format.

    Returns:
        dict: {title, structure, segments}
    """

    result = {
        "title": "Raw Text Document",
        "structure": [],
        "segments": [],
        "detected_format": None
    }

    # Detect format
    if is_qa_format(text):
        result["detected_format"] = "Q&A"
        return process_qa_format(text)

    if is_markdown_format(text):
        result["detected_format"] = "Markdown"
        return process_markdown_format(text)

    # Default: Generic structure detection
    lines = text.split("\n")
    current_section = None
    current_content = []

    for line in lines:
        if is_heading(line):
            # Start new section
            if current_section:
                current_section["content"] = "\n".join(current_content).strip()
                result["structure"].append(current_section)

            current_section = {
                "title": clean_heading(line),
                "level": detect_heading_level(line),
                "content": ""
            }
            current_content = []

        elif is_list_item(line):
            current_content.append(f"- {extract_list_item(line)}")

        elif line.strip():
            current_content.append(line.strip())

    # Save final section
    if current_section:
        current_section["content"] = "\n".join(current_content).strip()
        result["structure"].append(current_section)

    return result

def is_heading(line):
    """Detect: 'Title:' or '## Title' or 'Title\\n----'"""
    stripped = line.strip()

    # Pattern 1: "Title:"
    if stripped.endswith(":") and len(stripped) > 3:
        return True

    # Pattern 2: "## Title"
    if stripped.startswith("#"):
        return True

    return False

def is_list_item(line):
    """Detect: '- Item', '* Item', '• Item'"""
    stripped = line.lstrip()
    return stripped.startswith(("-", "*", "•"))

def is_qa_format(text):
    """Detect Q&A format: Lines starting with 'Q:' and 'A:'"""
    return bool(re.search(r"^[Qq]:\s+.+\n^[Aa]:\s+.+", text, re.MULTILINE))

def process_qa_format(text):
    """Convert Q&A to structured format."""
    qa_pairs = re.findall(
        r"^[Qq]:\s+(.+?)\n^[Aa]:\s+(.+?)(?=\n[Qq]:|$)",
        text,
        re.MULTILINE | re.DOTALL
    )

    segments = []
    for q, a in qa_pairs:
        segments.append({
            "type": "q_and_a",
            "question": q.strip(),
            "answer": a.strip()
        })

    return {
        "title": "Q&A Document",
        "detected_format": "Q&A",
        "segments": segments
    }
```

---

## Data Normalization Pipeline

### 5-Step Normalization

```python
def normalize_entry(raw_entry):
    """
    Normalize raw entry through 5 steps.

    Input: Raw content from any processor
    Output: Clean, structured knowledge entry
    """

    # Step 1: Clean
    cleaned = clean_content(raw_entry.get("content", ""))

    # Step 2: Structure
    structured = detect_structure(cleaned)

    # Step 3: Segment
    segmented = segment_content(structured, max_words=500)

    # Step 4: Enrich
    enriched = enrich_metadata(segmented)

    # Step 5: Deduplicate
    deduplicated = check_deduplication(enriched)

    return deduplicated

def clean_content(content):
    """Step 1: Remove HTML tags, fix encoding, trim whitespace."""

    # Remove HTML tags
    content = re.sub(r"<[^>]+>", "", content)

    # Fix common encoding issues
    content = content.replace("\u00a0", " ")  # Non-breaking space
    content = content.replace("\u2018", "'")  # Curly quote
    content = content.replace("\u2019", "'")

    # Normalize whitespace
    content = re.sub(r"\n{3,}", "\n\n", content)  # Max 2 newlines
    content = re.sub(r" {2,}", " ", content)  # Single spaces

    # Trim
    content = content.strip()

    return content

def detect_structure(content):
    """Step 2: Identify headings, lists, paragraphs."""

    lines = content.split("\n")
    structure = {
        "title": extract_first_heading(content),
        "sections": []
    }

    current_section = None

    for line in lines:
        if is_heading(line):
            if current_section:
                structure["sections"].append(current_section)

            current_section = {
                "heading": clean_heading(line),
                "content": []
            }

        elif current_section is not None:
            if line.strip():
                current_section["content"].append(line)

    if current_section:
        structure["sections"].append(current_section)

    return structure

def segment_content(structured, max_words=500):
    """Step 3: Break into logical chunks (max ~500 words per segment)."""

    segments = []

    for section in structured.get("sections", []):
        text = "\n".join(section.get("content", []))
        words = text.split()

        if len(words) <= max_words:
            segments.append({
                "heading": section.get("heading"),
                "content": text,
                "word_count": len(words)
            })
        else:
            # Split long sections
            chunks = [words[i:i + max_words] for i in range(0, len(words), max_words)]

            for idx, chunk in enumerate(chunks):
                segments.append({
                    "heading": f"{section.get('heading')} (Part {idx + 1})",
                    "content": " ".join(chunk),
                    "word_count": len(chunk)
                })

    return {
        "title": structured.get("title"),
        "segments": segments
    }

def enrich_metadata(segmented):
    """Step 4: Add computed metadata."""

    for segment in segmented.get("segments", []):
        segment["word_count"] = len(segment.get("content", "").split())
        segment["reading_time_minutes"] = max(1, segment["word_count"] // 200)
        segment["language"] = detect_language(segment.get("content", ""))

    return segmented

def check_deduplication(entry):
    """Step 5: Generate hash for deduplication detection."""

    import hashlib

    content_hash = hashlib.md5(
        entry.get("content", "").encode()
    ).hexdigest()

    entry["content_hash"] = content_hash
    entry["is_potential_duplicate"] = False  # Flag during batch processing

    return entry
```

---

## Metadata Extraction

For each input, extract:

```python
def extract_metadata(raw_entry, source_info):
    """
    Extract and infer metadata for entry.

    Args:
        raw_entry: Parsed content from processor
        source_info: Original source information

    Returns:
        dict: {title, date, author, language, word_count, ...}
    """

    metadata = {
        "title": extract_title(raw_entry),
        "date": extract_date(raw_entry, source_info),
        "author": extract_author(raw_entry),
        "language": detect_language(raw_entry.get("content", "")),
        "word_count": count_words(raw_entry.get("content", "")),
        "source_url": source_info.get("url"),
        "source_type": source_info.get("type"),
    }

    metadata["reading_time_minutes"] = max(1, metadata["word_count"] // 200)

    return metadata

def extract_title(entry):
    """Extract or infer title from entry."""

    # Try explicit title
    if entry.get("title"):
        return entry["title"]

    # Try first heading
    if entry.get("structure") and entry["structure"]:
        first_section = entry["structure"][0]
        if first_section.get("heading"):
            return first_section["heading"]

    # Try first sentence
    content = entry.get("content", "")
    first_sentence = re.split(r'[.!?]', content)[0]
    if first_sentence:
        return first_sentence[:100]

    return "Untitled Document"

def extract_date(entry, source_info):
    """Extract or infer publication date."""

    # Try metadata
    if entry.get("metadata", {}).get("date"):
        return entry["metadata"]["date"]

    # Try content (look for dates)
    content = entry.get("content", "")
    date_match = re.search(r"(\d{4}-\d{2}-\d{2}|\w+ \d{1,2}, \d{4})", content)
    if date_match:
        return date_match.group(0)

    # Try source (URL might have date)
    if "2026" in source_info.get("url", ""):
        return datetime.now().isoformat()

    return None

def extract_author(entry):
    """Extract author if available."""

    # Try metadata
    if entry.get("metadata", {}).get("author"):
        return entry["metadata"]["author"]

    # Try content search
    content = entry.get("content", "").lower()
    if "by " in content:
        match = re.search(r"by\s+([A-Z][a-z]+ [A-Z][a-z]+)", content)
        if match:
            return match.group(1)

    return None

def detect_language(text):
    """Detect language of text."""
    try:
        import textstat
        # Simplified: return based on character detection
        if any(ord(char) > 127 for char in text):
            return "multilingual"
        return "english"
    except:
        return "unknown"
```

---

## Batch Processing

When user provides multiple files/URLs:

```python
def batch_process(inputs):
    """
    Process multiple inputs, cross-reference, deduplicate.

    Args:
        inputs: list of file paths, URLs, or texts

    Returns:
        dict: {entries, deduplication_report, cross_references}
    """

    print(f"Processing {len(inputs)} inputs...")

    # Step 1: Inventory
    print("\n1. Creating inventory...")
    inventory = {}
    for input_val in inputs:
        detection = detect_input_type(input_val)
        input_type = detection.get("type")

        if input_type not in inventory:
            inventory[input_type] = []

        inventory[input_type].append(input_val)

    print(f"   Inventory: {[(k, len(v)) for k, v in inventory.items()]}")

    # Step 2: Group by type
    print("\n2. Grouping by type...")
    grouped = {
        "files": [],
        "urls": [],
        "text": []
    }

    for input_type, inputs_list in inventory.items():
        if input_type == "file":
            grouped["files"].extend(inputs_list)
        elif input_type == "url":
            grouped["urls"].extend(inputs_list)
        else:
            grouped["text"].extend(inputs_list)

    # Step 3: Process each group
    print("\n3. Processing groups...")
    all_entries = []

    for group_type, inputs_list in grouped.items():
        if not inputs_list:
            continue

        print(f"   Processing {len(inputs_list)} {group_type}...")

        for input_val in inputs_list:
            try:
                detection = detect_input_type(input_val)
                processor_name = detection.get("processor")
                params = detection.get("params")

                # Call appropriate processor
                processor = get_processor(processor_name)
                raw_result = processor(**params)

                # Normalize
                entries = normalize_entries(raw_result)
                all_entries.extend(entries)

                print(f"      ✓ Processed: {len(entries)} entries")

            except Exception as e:
                print(f"      ✗ Error processing {input_val}: {str(e)}")

    # Step 4: Cross-reference
    print(f"\n4. Cross-referencing {len(all_entries)} entries...")
    cross_refs = find_cross_references(all_entries)

    # Step 5: Deduplicate
    print("\n5. Deduplicating...")
    final_entries, duplicates = deduplicate_entries(all_entries)

    # Step 6: Report
    print(f"\n6. Batch processing complete!")
    print(f"   Final entries: {len(final_entries)}")
    print(f"   Duplicates removed: {len(duplicates)}")
    print(f"   Cross-references: {len(cross_refs)}")

    return {
        "entries": final_entries,
        "duplicates": duplicates,
        "cross_references": cross_refs,
        "ingestion_report": generate_ingestion_report(
            len(inputs),
            len(final_entries),
            len(duplicates),
            cross_refs
        )
    }

def deduplicate_entries(entries):
    """Find and remove duplicate entries by content hash."""

    seen_hashes = {}
    final_entries = []
    duplicates = []

    for entry in entries:
        content_hash = entry.get("content_hash")

        if content_hash in seen_hashes:
            # Duplicate found
            duplicates.append({
                "original": seen_hashes[content_hash],
                "duplicate": entry
            })
        else:
            seen_hashes[content_hash] = entry
            final_entries.append(entry)

    return final_entries, duplicates

def find_cross_references(entries):
    """Find which entries reference each other."""

    cross_refs = []

    for entry_a in entries:
        content_a = entry_a.get("content", "").lower()

        for entry_b in entries:
            if entry_a == entry_b:
                continue

            title_b = entry_b.get("title", "").lower()

            # Check if A mentions B's title
            if len(title_b) > 5 and title_b in content_a:
                cross_refs.append({
                    "from": entry_a.get("title"),
                    "to": entry_b.get("title"),
                    "type": "title_mention"
                })

    return cross_refs

def generate_ingestion_report(input_count, output_count, duplicates_count, cross_refs):
    """Generate summary report."""

    return f"""
BATCH INGESTION REPORT
======================
Inputs processed: {input_count}
Entries created: {output_count}
Duplicates removed: {duplicates_count}
Cross-references found: {len(cross_refs)}

Deduplication rate: {duplicates_count / max(1, input_count) * 100:.1f}%
Average entries per input: {output_count / max(1, input_count):.1f}
"""
```

---

## Error Handling

### Error Recovery Table

| Error | Cause | Recovery | User Action |
|-------|-------|----------|-------------|
| File unreadable | Corrupted/encrypted | Log warning, skip file, note in gap report | Provide uncorrupted version |
| URL unreachable | 404/timeout/DNS | Try cached version, mark UNKNOWN | Check URL, provide alternative |
| PDF no text | Scanned image | Suggest OCR, mark as image-based | Apply OCR tool if needed |
| Large file >10MB | Memory limits | Process in chunks | Split file or provide summary |
| Unknown format | Unsupported extension | Extract raw text, mark confidence LOW | Convert to supported format |
| Invalid JSON/CSV | Parse error | Log error, skip field | Validate structure |
| Notion permission | Access denied | Note as private, request share | Share Notion page |
| Rate limit (URLs) | Too many requests | Implement exponential backoff | Wait before retrying |
| Encoding error | Non-UTF8 file | Try alternative encodings (Latin-1, UTF-16) | Re-save as UTF-8 |
| Missing metadata | No title/date/author | Use inferred values, mark uncertain | Provide explicit metadata |

### Implementation

```python
def safe_process(input_val, error_log=None):
    """Process input with error recovery."""

    if error_log is None:
        error_log = []

    try:
        detection = detect_input_type(input_val)
        processor = get_processor(detection["processor"])
        result = processor(**detection["params"])

        return result

    except FileNotFoundError:
        error_log.append(f"File not found: {input_val}")
        return {"status": "error", "message": "File not found"}

    except json.JSONDecodeError as e:
        error_log.append(f"Invalid JSON: {input_val} - {str(e)}")
        return {"status": "error", "message": "Invalid JSON format"}

    except requests.exceptions.RequestException as e:
        error_log.append(f"URL unreachable: {input_val} - {str(e)}")
        return {"status": "error", "message": "URL unreachable"}

    except Exception as e:
        error_log.append(f"Unexpected error processing {input_val}: {str(e)}")
        return {"status": "error", "message": str(e)}
```

---

**Version**: 2.0
**Last Updated**: 2026-02-09
**Status**: Production
