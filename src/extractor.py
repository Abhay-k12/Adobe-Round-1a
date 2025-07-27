import json
from pathlib import Path
from heading_classifier import PDFOutlineExtractor

def process_pdfs():
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    output_dir.mkdir(exist_ok=True)

    extractor = PDFOutlineExtractor()

    for pdf_file in input_dir.glob("*.pdf"):
        result = extractor.extract_outline(pdf_file)
        
        # Final validation
        if not result["title"] or len(result["title"].split()) > 20:
            result["title"] = Path(pdf_file).stem
            
        with open(output_dir / f"{pdf_file.stem}.json", "w") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)

if __name__ == "__main__":
    process_pdfs()
    