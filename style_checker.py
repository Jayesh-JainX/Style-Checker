import re
import os
from pathlib import Path
import xml.etree.ElementTree as ET
from bs4 import BeautifulSoup
import docx
import markdown
from markdown.extensions import codehilite
import pdfplumber


class StyleChecker:
    def __init__(self):
        self.formats = ['.html', '.htm', '.docx', '.rtf', '.md', '.pdf']
        
    def load_file(self, filepath):
        p = Path(filepath)
        ext = p.suffix.lower()
        
        if ext in ['.html', '.htm']:
            return self._parse_html(filepath)
        elif ext == '.docx':
            return self._parse_docx(filepath)
        elif ext == '.rtf':
            return self._parse_rtf(filepath)
        elif ext == '.md':
            return self._parse_markdown(filepath)
        elif ext == '.pdf':
            return self._parse_pdf(filepath)
        else:
            raise Exception(f"Don't support {ext} files")
    
    def _parse_html(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        soup = BeautifulSoup(content, 'html.parser')
        text_data = ""
        char_styles = []
        
        def extract_from_element(elem, styles=None):
            if styles is None:
                styles = {'bold': False, 'italic': False, 'underline': False, 'color': 'black'}
            
            current_style = styles.copy()
            
            if elem.name in ['b', 'strong']:
                current_style['bold'] = True
            if elem.name in ['i', 'em']:
                current_style['italic'] = True
            if elem.name == 'u':
                current_style['underline'] = True
                
            if hasattr(elem, 'attrs') and 'style' in elem.attrs:
                style_str = elem.attrs['style']
                if 'font-weight:bold' in style_str or 'font-weight: bold' in style_str:
                    current_style['bold'] = True
                if 'font-style:italic' in style_str:
                    current_style['italic'] = True
                if 'text-decoration:underline' in style_str:
                    current_style['underline'] = True
                    
                color_match = re.search(r'color:\s*([^;]+)', style_str)
                if color_match:
                    current_style['color'] = color_match.group(1).strip()
            
            for child in elem.children:
                if hasattr(child, 'children'):
                    extract_from_element(child, current_style)
                else:
                    text_content = str(child)
                    for c in text_content:
                        if c.strip() or c == ' ':
                            nonlocal text_data, char_styles
                            text_data += c
                            char_styles.append({
                                'char': c,
                                **current_style
                            })
        
        body = soup.find('body') or soup
        extract_from_element(body)
        return text_data, char_styles
    
    def _parse_docx(self, filepath):
        doc = docx.Document(filepath)
        full_text = ""
        styles_list = []
        
        for para in doc.paragraphs:
            for r in para.runs:
                text_chunk = r.text
                for ch in text_chunk:
                    full_text += ch
                    
                    color_val = 'black'
                    if r.font.color and r.font.color.rgb:
                        rgb = r.font.color.rgb
                        color_val = f"rgb({rgb.red},{rgb.green},{rgb.blue})"
                    
                    styles_list.append({
                        'char': ch,
                        'bold': bool(r.bold),
                        'italic': bool(r.italic),
                        'underline': bool(r.underline),
                        'color': color_val
                    })
            
            full_text += '\n'
            styles_list.append({
                'char': '\n',
                'bold': False,
                'italic': False,
                'underline': False,
                'color': 'black'
            })
        
        return full_text, styles_list
    
    def _parse_rtf(self, filepath):
        with open(filepath, 'rb') as f:
            raw_data = f.read()
        
        try:
            content = raw_data.decode('utf-8')
        except:
            content = raw_data.decode('latin-1', errors='ignore')
        
        # Better RTF parsing
        text_parts = []
        styles_parts = []
        
        # Track RTF state
        bold_state = False
        italic_state = False
        underline_state = False
        
        # Simple RTF parser
        i = 0
        while i < len(content):
            if content[i] == '\\':
                # Found RTF control
                i += 1
                if i < len(content):
                    if content[i:i+1] == 'b':
                        # Bold control
                        if i+1 < len(content) and content[i+1] in '0 ':
                            bold_state = False
                        else:
                            bold_state = True
                        # Skip past control
                        while i < len(content) and content[i] not in ' \n':
                            i += 1
                    elif content[i:i+1] == 'i':
                        # Italic control
                        if i+1 < len(content) and content[i+1] in '0 ':
                            italic_state = False
                        else:
                            italic_state = True
                        while i < len(content) and content[i] not in ' \n':
                            i += 1
                    elif content[i:i+2] == 'ul':
                        # Underline control
                        if i+2 < len(content) and content[i+2] in '0 ':
                            underline_state = False
                        else:
                            underline_state = True
                        while i < len(content) and content[i] not in ' \n':
                            i += 1
                    else:
                        # Skip other controls
                        while i < len(content) and content[i] not in ' \n':
                            i += 1
            elif content[i] in '{}':
                # Skip braces
                pass
            elif content[i].isprintable() or content[i].isspace():
                # Regular text
                text_parts.append(content[i])
                styles_parts.append({
                    'char': content[i],
                    'bold': bold_state,
                    'italic': italic_state,
                    'underline': underline_state,
                    'color': 'black'
                })
            i += 1
        
        return ''.join(text_parts), styles_parts
    
    def _parse_pdf(self, filepath):
        text_content = ""
        char_styles = []
        
        try:
            with pdfplumber.open(filepath) as pdf:
                for page in pdf.pages:
                    # Extract text with character-level info
                    chars = page.chars
                    
                    for char_info in chars:
                        char = char_info.get('text', '')
                        if char.strip() or char == ' ':
                            text_content += char
                            
                            # Extract formatting info
                            font_name = char_info.get('fontname', '').lower()
                            font_size = char_info.get('size', 12)
                            
                            # Detect styling from font name
                            is_bold = 'bold' in font_name or 'black' in font_name
                            is_italic = 'italic' in font_name or 'oblique' in font_name
                            
                            char_styles.append({
                                'char': char,
                                'bold': is_bold,
                                'italic': is_italic,
                                'underline': False,  # Hard to detect in PDF
                                'color': 'black',
                                'font_size': font_size
                            })
                    
                    # Add page break
                    if len(pdf.pages) > 1:
                        text_content += '\n'
                        char_styles.append({
                            'char': '\n',
                            'bold': False,
                            'italic': False,
                            'underline': False,
                            'color': 'black',
                            'font_size': 12
                        })
        
        except Exception as e:
            print(f"PDF parsing error: {e}")
            return "", []
        
        return text_content, char_styles
    
    def _parse_markdown(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            md_content = f.read()
        
        md = markdown.Markdown(extensions=['extra'])
        html_content = md.convert(md_content)
        
        html_doc = f"<html><body>{html_content}</body></html>"
        
        soup = BeautifulSoup(html_doc, 'html.parser')
        text_result = ""
        style_result = []
        
        def process_md_element(elem, inherited=None):
            if inherited is None:
                inherited = {'bold': False, 'italic': False, 'underline': False, 'color': 'black'}
            
            styles = inherited.copy()
            
            if elem.name in ['strong', 'b']:
                styles['bold'] = True
            elif elem.name in ['em', 'i']:
                styles['italic'] = True
            elif elem.name == 'code':
                styles['color'] = 'red'
            elif elem.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                styles['bold'] = True
                styles['color'] = 'blue'
            
            for child in elem.children:
                if hasattr(child, 'children'):
                    process_md_element(child, styles)
                else:
                    content = str(child)
                    for c in content:
                        nonlocal text_result, style_result
                        text_result += c
                        style_result.append({
                            'char': c,
                            **styles
                        })
        
        process_md_element(soup.body)
        return text_result, style_result
    
    def find_text(self, haystack, needle):
        lower_hay = haystack.lower()
        lower_needle = needle.lower()
        
        pos = lower_hay.find(lower_needle)
        if pos >= 0:
            return pos, pos + len(needle) - 1
        
        words = needle.lower().split()
        if len(words) > 1:
            first_word_pos = lower_hay.find(words[0])
            if first_word_pos >= 0:
                last_word_pos = lower_hay.find(words[-1], first_word_pos)
                if last_word_pos >= 0:
                    return first_word_pos, last_word_pos + len(words[-1]) - 1
        
        return None, None
    
    def get_style_at(self, styles, pos):
        if 0 <= pos < len(styles):
            return styles[pos]
        return None
    
    def style_to_string(self, style_data):
        if not style_data:
            return "Not found"
        
        char = repr(style_data['char'])
        attrs = []
        
        if style_data.get('bold'):
            attrs.append('BOLD')
        if style_data.get('italic'):
            attrs.append('ITALIC')
        if style_data.get('underline'):
            attrs.append('UNDERLINED')
        
        color = style_data.get('color', 'black')
        if color != 'black':
            attrs.append(f'COLOR:{color}')
        
        font_size = style_data.get('font_size')
        if font_size and font_size != 'normal':
            attrs.append(f'SIZE:{font_size}')
        
        if not attrs:
            attrs.append('NORMAL')
        
        return f"{char} -> {' | '.join(attrs)}"
    
    def check_message(self, file_path, search_text):
        if not os.path.exists(file_path):
            print("File doesn't exist!")
            return
        
        try:
            text, styles = self.load_file(file_path)
        except Exception as e:
            print(f"Failed to read file: {e}")
            return
        
        print(f"Loaded {len(text)} characters from file")
        print(f"Sample: {text[:50]}{'...' if len(text) > 50 else ''}")
        
        start, end = self.find_text(text, search_text)
        if start is None:
            print(f"'{search_text}' not found in the text")
            return
        
        print(f"Found '{search_text}' at position {start}-{end}")
        
        before_char = self.get_style_at(styles, start - 1)
        after_char = self.get_style_at(styles, end + 1)
        
        print("\nResults:")
        print(f"Before: {self.style_to_string(before_char)}")
        print(f"After:  {self.style_to_string(after_char)}")
        
        ctx_start = max(0, start - 15)
        ctx_end = min(len(text), end + 16)
        context = text[ctx_start:ctx_end]
        print(f"Context: ...{context}...")
        
        return {
            'found_at': (start, end),
            'before_style': before_char,
            'after_style': after_char,
            'context': context
        }



def run():
    checker = StyleChecker()
    print("Style Checker v2.0")
    print("Supports: HTML, DOCX, RTF, Markdown, PDF")
    
    while True:
        file_input = input("\nFile path ('quit' or 'q'): ").strip()
        if file_input.lower() == 'quit':
            break
        elif file_input.lower() == 'q':
            break
        
        if not file_input:
            continue
            
        search_input = input("Search text: ").strip()
        if not search_input:
            print("Need search text!")
            continue
        
        result = checker.check_message(file_input, search_input)
        
        if result:
            print("=" * 40)


if __name__ == "__main__":
    run()
