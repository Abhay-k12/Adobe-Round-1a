from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTTextBoxHorizontal
from pathlib import Path
import re
from typing import Dict, List, Union

class PDFOutlineExtractor:
    def extract_outline(self, pdf_path: Union[str, Path]) -> Dict:
        """Extract hierarchical outline from PDF document"""
        outlines = []
        title = ""
        seen_texts = set()
        
        try:
            # First pass to identify potential title from first page
            first_page = next(extract_pages(pdf_path))
            title = self._extract_title(first_page) or Path(pdf_path).stem
            
            # Process all pages for headings
            for page_num, page in enumerate(extract_pages(pdf_path), 1):
                page_elements = []
                
                for element in page:
                    if isinstance(element, (LTTextBoxHorizontal, LTTextContainer)):
                        text = self._clean_text(element.get_text())
                        if text and len(text.split()) <= 30:  # Skip long paragraphs
                            page_elements.append({
                                'text': text,
                                'bbox': (element.x0, element.y0, element.x1, element.y1),
                                'font_size': self._get_avg_fontsize(element),
                                'is_bold': self._is_bold(element),
                                'is_centered': self._is_centered(element, page),
                                'page': page_num
                            })
                
                # Process elements in reading order (top to bottom)
                page_elements.sort(key=lambda x: (-x['bbox'][1], x['bbox'][0]))
                
                for el in page_elements:
                    if self._is_valid_heading(el) and el['text'] not in seen_texts:
                        level = self._classify_heading(el)
                        outlines.append({
                            "level": level,
                            "text": el['text'],
                            "page": el['page']
                        })
                        seen_texts.add(el['text'])
            
            # Post-processing to clean up results
            outlines = self._post_process_outlines(outlines, title)
            
            return {
                "title": title,
                "outline": outlines or [{
                    "level": "H1",
                    "text": title,
                    "page": 1
                }]
            }
            
        except Exception as e:
            print(f"Error processing {pdf_path}: {str(e)}")
            return {
                "title": Path(pdf_path).stem,
                "outline": [{
                    "level": "H1",
                    "text": Path(pdf_path).stem,
                    "page": 1
                }]
            }

    def _extract_title(self, page) -> str:
        """Extract the most likely document title from first page"""
        candidates = []
        for element in page:
            if isinstance(element, (LTTextBoxHorizontal, LTTextContainer)):
                text = self._clean_text(element.get_text())
                if 3 <= len(text.split()) <= 10:
                    candidates.append({
                        'text': text,
                        'size': self._get_avg_fontsize(element),
                        'bold': self._is_bold(element),
                        'centered': self._is_centered(element, page)
                    })
        
        if candidates:
            # Prefer large, bold, centered text at top of page
            candidates.sort(key=lambda x: (
                -x['size'],
                -x['bold'],
                -x['centered'],
                -x['text'].count('\n')  # Fewer line breaks = more title-like
            ))
            return candidates[0]['text']
        return ""

    def _clean_text(self, text: str) -> str:
        """Normalize text by removing excessive whitespace and special chars"""
        # First remove bullet characters
        text = re.sub(r'[\u2022\u2023\u25E6\u2043\u2219•▪]', ' ', text)
        
        # Keep letters, numbers, basic punctuation and some special chars
        text = re.sub(r'[^\w\s\-.,:;()\u2013\u2014]', '', text)  # Note the escaped hyphen
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text

    def _get_avg_fontsize(self, element) -> float:
        """Calculate average font size of text elements"""
        sizes = []
        for obj in getattr(element, '_objs', []):
            if hasattr(obj, 'size'):
                sizes.append(obj.size)
        return sum(sizes)/len(sizes) if sizes else 10

    def _is_bold(self, element) -> bool:
        """Check if text contains bold formatting"""
        for obj in getattr(element, '_objs', []):
            if getattr(obj, 'fontname', '').lower().endswith('bold'):
                return True
            if getattr(obj, 'fontname', '').lower().find('bold') != -1:
                return True
        return False

    def _is_centered(self, element, page) -> bool:
        """Check if element is centered on page"""
        if not hasattr(page, 'width'):
            return False
        page_center = page.width / 2
        elem_center = (element.x0 + element.x1) / 2
        return abs(elem_center - page_center) < 20

    def _is_valid_heading(self, element: Dict) -> bool:
        """Determine if element should be considered a heading"""
        text = element['text']
        words = text.split()
        
        # Basic filters
        if len(words) > 15 or len(words) < 2:
            return False
        if text.isdigit() or re.match(r'^\d+\.?\d*$', text):
            return False
            
        # Formatting clues
        is_upper = text == text.upper()
        is_bold = element['is_bold']
        large_font = element['font_size'] > 12
        is_centered = element['is_centered']
        
        # Structural patterns
        starts_with_number = re.match(r'^\d+\.\d*', text)  # e.g. "1.1 Introduction"
        starts_with_heading_word = re.match(
            r'^(chapter|section|part|appendix|article|clause|paragraph|table|figure)\b', 
            text.lower()
        )
        ends_with_colon = text.strip().endswith(':')
        
        return any([
            is_upper and len(words) <= 8,
            is_bold and large_font,
            is_centered and large_font,
            starts_with_number,
            starts_with_heading_word,
            ends_with_colon and large_font
        ])

    def _classify_heading(self, element: Dict) -> str:
        """Determine heading level based on formatting and content"""
        text = element['text']
        
        # H1: Largest, most prominent headings
        if (element['font_size'] > 14 and element['is_bold']) or text == text.upper():
            return "H1"
        if re.match(r'^(chapter|part)\b', text, re.IGNORECASE):
            return "H1"
            
        # H2: Sub-headings with numbering or medium size
        if re.match(r'^\d+\.\d+\s', text):  # e.g. "1.1 Introduction"
            return "H2"
        if element['font_size'] > 12 or (element['is_bold'] and not element['is_centered']):
            return "H2"
            
        # H3: Smaller headings or those ending with colons
        if text.strip().endswith(':'):
            return "H3"
        if re.match(r'^\d+\.\d+\.\d+\s', text):  # e.g. "1.1.1 Details"
            return "H3"
            
        # Default to H2 for other valid headings
        return "H2"

    def _post_process_outlines(self, outlines: List[Dict], title: str) -> List[Dict]:
        """Clean up and validate the extracted outlines"""
        # Remove duplicates while preserving order
        seen = set()
        unique_outlines = []
        for item in outlines:
            text = item['text']
            if text not in seen:
                seen.add(text)
                unique_outlines.append(item)
        
        # Ensure first heading matches document title if similar
        if unique_outlines and self._text_similarity(title, unique_outlines[0]['text']) > 0.7:
            unique_outlines[0]['text'] = title
        
        return unique_outlines

    def _text_similarity(self, text1: str, text2: str) -> float:
        """Calculate simple text similarity ratio (0-1)"""
        words1 = set(text1.lower().split())
        words2 = set(text2.lower().split())
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        return len(intersection) / len(union) if union else 0