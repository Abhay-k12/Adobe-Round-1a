from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer, LTTextBoxHorizontal, LTTextLineHorizontal, LTRect, LTLine, LAParams
from pdf2image import convert_from_path
import pytesseract
from pathlib import Path
import re
import logging
from typing import Dict, List, Union


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class PDFOutlineExtractor:
    def __init__(self, ocr_languages: str = "eng"):
        self.ocr_languages = ocr_languages
        self.laparams = LAParams(
            line_margin=0.5,
            char_margin=2.0,
            boxes_flow=0.5,
            detect_vertical=True,
            all_texts=True
        )


    def extract_outline(self, pdf_path: Union[str, Path]) -> Dict:
        outlines = []
        title = ""
        try:
            pages = list(extract_pages(pdf_path, laparams=self.laparams))
            title = self._extract_title_fallback(pages[0]) if pages else Path(pdf_path).stem

            for page_num, page in enumerate(pages, 1):
                classification = self._classify_page(page)

                if classification in ["card", "tabular"]:
                    continue

                found_heading = False
                for element in page:
                    if isinstance(element, (LTTextBoxHorizontal, LTTextContainer, LTTextLineHorizontal)):
                        text = self._clean_text(element.get_text())
                        if not text or not self._is_valid_heading(element, text, page):
                            continue
                        level = self._classify_heading(element, text)
                        outlines.append({
                            "level": level,
                            "text": text,
                            "page": page_num
                        })
                        found_heading = True

                if not found_heading:
                    # *** using OCR if no heading found ***
                    ocr_text = self._ocr_page(str(pdf_path), page_num)
                    for line in ocr_text.split('\n'):
                        line = self._clean_text(line)
                        if self._is_valid_heading_from_text(line):
                            outlines.append({"level": "H2", "text": line, "page": page_num})

            if not outlines:
                outlines = [{"level": "H1", "text": title, "page": 1}]

            return {
                "title": title,
                "outline": outlines
            }

        except Exception as e:
            logger.error(f"Error processing {pdf_path}: {e}")
            return {
                "title": Path(pdf_path).stem,
                "outline": [{"level": "H1", "text": Path(pdf_path).stem, "page": 1}]
            }


    def _ocr_page(self, pdf_path: str, page_num: int) -> str:
        images = convert_from_path(pdf_path, first_page=page_num, last_page=page_num)
        if images:
            return pytesseract.image_to_string(images[0], lang=self.ocr_languages)
        return ""


    def _classify_page(self, page) -> str:
        text_elems = [e for e in page if isinstance(e, LTTextContainer)]
        total_text = sum(len(e.get_text().strip()) for e in text_elems)
        if total_text < 300:
            for elem in text_elems:
                text = elem.get_text().lower()
                if any(w in text for w in ["you're invited", "hope to see", "party", "rsvp"]):
                    return "card"
                if abs(((elem.x0 + elem.x1)/2) - (page.width/2)) < 50:
                    return "card"
        line_count = sum(1 for e in page if isinstance(e, (LTRect, LTLine)))
        short_text_count = sum(1 for e in text_elems if len(e.get_text().strip()) < 20)
        if line_count > 20 and short_text_count > 10:
            return "tabular"
        return "normal"


    def _extract_title_fallback(self, page) -> str:
        for element in page:
            if isinstance(element, (LTTextBoxHorizontal, LTTextContainer)):
                text = self._clean_text(element.get_text())
                if len(text.split()) >= 3:
                    return text
        return ""


    def _clean_text(self, text: str) -> str:
        text = re.sub(r'\s+', ' ', text.strip())
        return text


    def _get_avg_fontsize(self, element) -> float:
        sizes = [obj.size for obj in getattr(element, '_objs', []) if hasattr(obj, 'size')]
        return sum(sizes)/len(sizes) if sizes else 0


    def _is_bold(self, element) -> bool:
        for obj in getattr(element, '_objs', []):
            fontname = getattr(obj, 'fontname', '').lower()
            if any(x in fontname for x in ['bold', 'black', 'heavy']):
                return True
        return False


    def _is_centered(self, element, page) -> bool:
        if not hasattr(page, 'width'):
            return False
        elem_center = (element.x0 + element.x1) / 2
        page_center = page.width / 2
        return abs(elem_center - page_center) < (page.width * 0.3)


    def _is_valid_heading(self, element, text: str, page) -> bool:
        if len(text) < 3 or len(text.split()) > 12:
            return False
        if re.fullmatch(r'[-\s.]{5,}', text):  # ***reject dashed/line-only text***
            return False
        if re.fullmatch(r'(\d+\s?){2,}', text):  # ***repeated digit-only***
            return False
        if any(x in text.lower() for x in ['page', 'continued', 'copyright', '©']):
            return False

        font_size = self._get_avg_fontsize(element)
        is_bold = self._is_bold(element)
        is_centered = self._is_centered(element, page)
        is_upper = text == text.upper()
        starts_with_num = re.match(r'^\d+[\.\)]', text)
        is_section = re.match(r'^(section|chapter|part|clause)\b', text, re.I)

        return any([
            is_upper and len(text.split()) <= 5,
            is_bold and font_size > 11,
            is_centered and font_size > 12,
            starts_with_num,
            is_section
        ])


    def _is_valid_heading_from_text(self, text: str) -> bool:
        if not text or len(text.split()) > 12 or len(text) < 5:
            return False
        if re.fullmatch(r'[-\s.]{5,}', text):
            return False
        if re.fullmatch(r'(\d+\s?){2,}', text):
            return False
        if any(x in text.lower() for x in ['page', 'continued', 'copyright', '©']):
            return False
        return True


    def _classify_heading(self, element, text: str) -> str:
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
