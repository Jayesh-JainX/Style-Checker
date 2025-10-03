# Style Checker

A Python application that analyzes text styling and formatting in documents. It can locate specific text within various document formats and identify the styling properties of characters before and after the target text.

## Overview

Style Checker extracts text content along with formatting information (bold, italic, underline, colors) from documents and allows you to search for specific text phrases. It then analyzes the styling of characters immediately before and after your search text, which is useful for document analysis, content validation, and formatting verification.

## Supported File Formats

| Format               | Extension       | Features Detected                                    |
| :------------------- | :-------------- | :--------------------------------------------------- |
| **HTML**             | `.html`, `.htm` | Bold, Italic, Underline, Colors, Inline styles       |
| **Microsoft Word**   | `.docx`         | Bold, Italic, Underline, Colors, Font properties     |
| **Rich Text Format** | `.rtf`          | Bold, Italic, Underline (basic parsing)              |
| **Markdown**         | `.md`           | Bold, Italic, Headers, Code blocks                   |
| **PDF**              | `.pdf`          | Bold, Italic, Font sizes (font-name based detection) |

## Features

- **Character-level styling analysis**: Tracks formatting for every character
- **Flexible text search**: Exact match or partial word matching
- **Context display**: Shows surrounding text for better understanding
- **Multiple format support**: Works with 5 different document formats
- **Font property detection**: Colors, sizes, and style attributes

## Installation

### 🐍 Python & pip Version Info

```bash
pip 22.0.4
Python 3.10.4
```

### Requirements

```bash
pip install pdfplumber beautifulsoup4 python-docx markdown
```

or

```bash
pip install -r requirements.txt
```

### Dependencies

- `pdfplumber`: PDF text extraction with formatting
- `beautifulsoup4`: HTML parsing
- `python-docx`: Microsoft Word document handling
- `markdown`: Markdown to HTML conversion

## Usage

### Basic Usage

1. **Run the application**:

```bash
python style_checker.py
```

2. **Analyze a document**:

```
File path ('quit' or 'q'): sample_files/sample.html
Search text: i work in tooliqa
```

### Command Options

| Input       | Action                          |
| :---------- | :------------------------------ |
| `quit`      | Exits the application           |
| `File path` | Analyzes the specified document |

## Example Output

```
Style Checker v2.0
Supports: HTML, DOCX, RTF, Markdown, PDF

File path ('quit' or 'q'): sample_files/sample.html
Search text: i work in tooliqa

Loaded 156 characters from file
Sample: kuWCUKAVAYUVVYEVUWVYVYYAJVACAKEUCi work in tooliqabaoiad...

Found 'i work in tooliqa' at position 32-48

Results:
Before: 'C' -> NORMAL
After:  'b' -> NORMAL
Context: ...ACAKEUCi work in tooliqabaoi...
```

## Code Structure

### Main Class: `StyleChecker`

```python
StyleChecker()
├── load_file(filepath)           # Main file loading dispatcher
├── _parse_html(filepath)         # HTML document parsing
├── _parse_docx(filepath)         # Word document parsing
├── _parse_rtf(filepath)          # RTF document parsing
├── _parse_pdf(filepath)          # PDF document parsing
├── _parse_markdown(filepath)     # Markdown document parsing
├── find_text(haystack, needle)   # Text search functionality
├── get_style_at(styles, pos)     # Style extraction at position
├── style_to_string(style_data)   # Style formatting for display
└── check_message(file_path, text) # Main analysis function
```

### Style Information Structure

Each character is stored with the following properties:

```python
{
    'char': 'a',              # The actual character
    'bold': True/False,       # Bold formatting
    'italic': True/False,     # Italic formatting
    'underline': True/False,  # Underline formatting
    'color': 'black',         # Text color
    'font_size': 12           # Font size (PDF only)
}
```

## File Format Details

### HTML Files

- Supports `<b>`, `<strong>`, `<i>`, `<em>`, `<u>` tags
- Parses inline CSS styles (font-weight, font-style, text-decoration)
- Extracts color information from style attributes
- Handles nested styling elements

### DOCX Files

- Reads formatting from Word document runs
- Extracts RGB color values
- Supports paragraph-level formatting
- Handles font properties and sizes

### RTF Files

- Basic RTF control word parsing
- Detects `\b` (bold), `\i` (italic), `\ul` (underline)
- Simplified parser for common formatting
- Handles UTF-8 and Latin-1 encodings

### PDF Files

- Uses character-level extraction via pdfplumber
- Font-name based style detection
- Identifies bold/italic from font names
- Extracts font size information
- Handles multi-page documents

### Markdown Files

- Converts to HTML first using markdown library
- Supports `**bold**`, `*italic*` syntax
- Handles headers with special styling
- Code blocks get color highlighting

### HTML Sample

```html
<p>
  kuWCUKAVAYUVVYEVUWVYVYYAJVACAKEUC<b>i</b> <i>work</i> <u>in</u>
  <strong>tooliqa</strong>baoiadcntooliqa
</p>
```

### RTF Sample

```rtf
{\rtf1\ansi\deff0 {\fonttbl {\f0 Times New Roman;}}
This is normal text with \b bold text \b0 and \i italic text\i0.
kuWCUKAVAYUVVYEVUWVYVYYAJVACAKEUC\b i\b0 \i work\i0 \ul in\ul0 \b\i tooliqa\b0\i0
}
```

### Markdown Sample

```markdown
# Sample Document

Some text here **i** _work_ in **tooliqa** more text
```

## Search Functionality

### Exact Match

Searches for the complete phrase as entered, case-insensitive.

### Partial Match

If exact match fails, attempts to find individual words:

- Finds first word of the search phrase
- Locates last word after the first word
- Returns the range from first to last word

### Case Sensitivity

All searches are case-insensitive by default.

## Output Information

### Character Analysis

- **Position**: Exact character positions in the document
- **Context**: 15 characters before and after the found text
- **Before/After Styling**: Formatting of adjacent characters

### Style Attributes

- `BOLD`: Bold formatting detected
- `ITALIC`: Italic formatting detected
- `UNDERLINED`: Underline formatting detected
- `COLOR:value`: Text color (when not black)
- `SIZE:value`: Font size (PDF files)
- `NORMAL`: No special formatting

## Troubleshooting

### Common Issues

**File Not Found**

```
File doesn't exist!
```

- Check file path spelling
- Use absolute paths if relative paths fail
- Ensure file extension is supported

**Parsing Errors**

```
Failed to read file: [error message]
```

- Verify file is not corrupted
- Check file permissions
- Ensure all dependencies are installed

**Text Not Found**

```
'search text' not found in the text
```

- Check spelling of search text
- Try searching for individual words
- Verify text exists in the document

### Installation Issues

**Missing Dependencies**

```bash
# Install all required packages
pip install pdfplumber beautifulsoup4 python-docx markdown

# For PDF support specifically
pip install pdfplumber

# For Word document support
pip install python-docx
```

### Performance Notes

- Large PDF files may take longer to process
- Character-level analysis requires more memory for large documents
- RTF parsing is simplified and may not catch all formatting

## Limitations

- RTF parsing is basic and may miss complex formatting
- PDF style detection relies on font names
- Some PDF files may not preserve formatting information
- Underline detection in PDF is limited
- Very large files may impact performance
