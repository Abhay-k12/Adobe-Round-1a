import os
import json
from pathlib import Path
from .heading_classifier import PDFOutlineExtractor
from .utils import validate_json_schema

def process_pdfs():
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    output_dir.mkdir(exist_ok=True)

    extractor = PDFOutlineExtractor()

    for pdf_file in input_dir.glob("*.pdf"):
        result = extractor.extract_outline(pdf_file)
        
        # Validate against JSON schema
        validate_json_schema(result)
        
        # Save output
        output_file = output_dir / f"{pdf_file.stem}.json"
        with open(output_file, "w") as f:
            json.dump(result, f, indent=2)

if __name__ == "__main__":
    process_pdfs()