from unstructured.partition.pdf import partition_pdf
import re

class PDFOutlineExtractor:
    def __init__(self):
        self.title_strategies = [
            lambda el: el.metadata.text_ascent > 24,
            lambda el: el.category == "Title",
            lambda el: el.metadata.page_number == 1 and "title" in el.text.lower()
        ]

    def extract_outline(self, pdf_path):
        elements = partition_pdf(str(pdf_path), strategy="hi_res")
        outline = []
        title = ""
        
        for element in elements:
            if not hasattr(element, "metadata"):
                continue
                
            current_page = element.metadata.page_number
            text = self.clean_text(element.text)
            
            # Title detection
            if not title and any(strategy(element) for strategy in self.title_strategies):
                title = text
                
            # Heading detection
            if level := self.classify_heading(element):
                outline.append({
                    "level": level,
                    "text": text,
                    "page": current_page
                })
                
        return {"title": title or os.path.basename(pdf_path), "outline": outline}

    def classify_heading(self, element):
        if not hasattr(element, "category"):
            return None
            
        if element.category == "Heading":
            if element.metadata.text_ascent > 20:
                return "H1"
            elif element.metadata.text_ascent > 16:
                return "H2"
            return "H3"
        return None

    def clean_text(self, text):
        return re.sub(r'\s+', ' ', text).strip()
