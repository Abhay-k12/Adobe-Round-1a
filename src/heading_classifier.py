from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTTextBoxHorizontal, LTTextLineHorizontal, LAParams
from pathlib import Path
import re
import logging
from typing import Dict, List, Union

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PDFOutlineExtractor:
    def __init__(self):
        self.laparams = LAParams(
            line_margin=0.5,
            char_margin=2.0,
            boxes_flow=0.5
        )

    def extract_outline(self, pdf_path: Union[str, Path]) -> Dict:
        """Final robust PDF outline extractor with all fixes"""
        outlines = []
        title = ""
        
        try:
            # Extract first page with layout analysis
            first_page = next(extract_pages(pdf_path, laparams=self.laparams))
            
            # Improved title extraction
            title = self._extract_document_title(first_page) or Path(pdf_path).stem
            logger.info(f"Using title: {title}")

            # Process all pages
            seen_texts = set()
            for page_num, page in enumerate(extract_pages(pdf_path, laparams=self.laparams), 1):
                for element in page:
                    if isinstance(element, (LTTextBoxHorizontal, LTTextContainer, LTTextLineHorizontal)):
                        text = self._clean_text(element.get_text())
                        if not text or text in seen_texts:
                            continue
                            
                        if self._is_valid_heading(element, text, page):  # Pass page object here
                            level = self._classify_heading(element, text)
                            outlines.append({
                                "level": level,
                                "text": text,
                                "page": page_num
                            })
                            seen_texts.add(text)
            
            # Final fallback
            if not outlines:
                outlines = [{"level": "H1", "text": title, "page": 1}]
            
            return {
                "title": title,
                "outline": outlines
            }
            
        except Exception as e:
            logger.error(f"Critical error processing {pdf_path}: {str(e)}")
            return {
                "title": Path(pdf_path).stem,
                "outline": [{
                    "level": "H1",
                    "text": Path(pdf_path).stem,
                    "page": 1
                }]
            }

    def _extract_document_title(self, page) -> str:
        """Final title extraction with multiple fallbacks"""
        # Try centered large text first
        for element in page:
            if isinstance(element, (LTTextBoxHorizontal, LTTextContainer)):
                text = self._clean_text(element.get_text())
                if (len(text.split()) >= 3 and 
                    self._get_avg_fontsize(element) > 14 and 
                    self._is_centered(element, page)):
                    return text
        
        # Then try any large bold text
        for element in page:
            if isinstance(element, (LTTextBoxHorizontal, LTTextContainer)):
                text = self._clean_text(element.get_text())
                if (len(text.split()) >= 2 and 
                    self._get_avg_fontsize(element) > 12 and 
                    self._is_bold(element)):
                    return text
        
        # Finally try first meaningful text
        for element in page:
            if isinstance(element, (LTTextBoxHorizontal, LTTextContainer)):
                text = self._clean_text(element.get_text())
                if len(text.split()) >= 2:
                    return text
        
        return ""

    def _clean_text(self, text: str) -> str:
        """Final text cleaning that preserves meaningful content"""
        text = re.sub(r'\s+', ' ', text).strip()
        # Remove common artifacts but keep main content
        text = re.sub(r'^[\W\d]+', '', text)
        text = re.sub(r'[\W\d]+$', '', text)
        return text if len(text) > 2 else ""

    def _get_avg_fontsize(self, element) -> float:
        """Safe font size calculation"""
        sizes = [obj.size for obj in getattr(element, '_objs', []) if hasattr(obj, 'size')]
        return sum(sizes)/len(sizes) if sizes else 0

    def _is_bold(self, element) -> bool:
        """Comprehensive bold detection"""
        for obj in getattr(element, '_objs', []):
            fontname = getattr(obj, 'fontname', '').lower()
            if any(x in fontname for x in ['bold', 'black', 'heavy', 'demi']):
                return True
        return False

    def _is_centered(self, element, page) -> bool:
        """Safe centering check with page reference"""
        if not hasattr(page, 'width'):
            return False
        elem_center = (element.x0 + element.x1) / 2
        page_center = page.width / 2
        return abs(elem_center - page_center) < (page.width * 0.3)

    def _is_valid_heading(self, element, text: str, page) -> bool:
        """Final heading validation with all fixes"""
        # Quick rejection
        if len(text) < 3 or len(text.split()) > 10:
            return False
        
        # Blacklist patterns
        blacklist = ['page', 'continued', 'copyright', '©', 'http://', 'www.']
        if any(x in text.lower() for x in blacklist):
            return False
        
        # Formatting checks
        font_size = self._get_avg_fontsize(element)
        is_bold = self._is_bold(element)
        is_centered = self._is_centered(element, page)  # Use passed page parameter
        
        # Content patterns
        is_upper = text == text.upper()
        starts_with_num = re.match(r'^\d+[\.\)]', text)
        is_section = re.match(r'^(section|chapter|part|clause)\b', text, re.I)
        
        # Final validation
        return any([
            is_upper and len(text.split()) <= 5,
            is_bold and font_size > 11,
            is_centered and font_size > 12,
            starts_with_num,
            is_section
        ])
    
    def _classify_heading(self, element, text: str) -> str:
        """Final heading classification"""
        font_size = self._get_avg_fontsize(element)
        is_bold = self._is_bold(element)
        
        if (font_size >= 16 and is_bold) or text == text.upper():
            return "H1"
        if re.match(r'^(chapter|part)\b', text, re.I):
            return "H1"
        if re.match(r'^\d+\.\d+\s', text):
            return "H2"
        if font_size >= 12 or is_bold:
            return "H2"
        return "H3"


