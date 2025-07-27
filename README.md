<p align="center">
  <img src="https://upload.wikimedia.org/wikipedia/commons/thumb/f/fa/Adobe_Corporate_Logo.png/320px-Adobe_Corporate_Logo.png" height="70" alt="Adobe Logo"/>
</p>

<h1 align="center">📄 PDF Outline Extractor</h1>
<p align="center"><i>A robust, offline, containerized solution for Adobe Hackathon Challenge 1a — built to extract document outlines intelligently, efficiently, and beautifully.</i></p>

---

## 🧠 Overview

This project is a submission for **Adobe India Hackathon 2025 – Challenge 1a**.

> ⚡ **Goal:** Automatically extract meaningful structured information (title and heading outline) from PDFs and generate corresponding `.json` outputs – fully offline and within strict resource and performance constraints.

---

## 🚀 Features

✅ Accurate extraction of **document title and outline hierarchy (H1–H3)**  
✅ Works with **card-style**, **tabular**, **narrative**, and **structured documents**  
✅ Fully **offline**, **Dockerized**, and **under 200MB**  
✅ PDFMiner-based — no dependency on large OCR or cloud APIs  
✅ Post-processing to clean artifacts (e.g. repeated headings, footers, copyright)  
✅ Conforms to Adobe's [JSON Schema](sample_dataset/schema/output_schema.json)  

---

## 🧱 Architecture

```
pdf_outline_extractor/
├── src/
│ ├── extractor.py # Orchestrates extraction logic and output generation
│ ├── heading_classifier.py # Core PDF outline classification logic (H1/H2/H3)
│ └── utils.py # JSON schema validation
├── input/ # Input PDF directory (read-only in container)
├── output/ # Output directory for JSON files
├── Dockerfile # Docker container configuration
├── requirements.txt # Python dependencies
└── README.md # This file
```


---

## 🧠 Modules & Responsibilities

| Module | Description |
|--------|-------------|
| `extractor.py` | Entry-point script that processes all PDFs from `/app/input` and saves JSON output to `/app/output`. Handles post-processing, fallback logic, and schema validation. |
| `heading_classifier.py` | Main PDF parsing logic using PDFMiner. Detects and classifies title and headings (H1, H2, H3) using heuristics based on font size, position, boldness, and numbering patterns. |
| `utils.py` | Validates the generated JSON output using the schema provided in the challenge. Ensures compliance. |

---

## 🛠️ Technologies Used

<p>
  <img src="https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/PDFMiner-20221105-lightgrey"/>
  <img src="https://img.shields.io/badge/Docker-Containerized-blue?logo=docker"/>
  <img src="https://img.shields.io/badge/JSON-Schema-yellow?logo=json"/>
</p>

---

## 🐳 Docker Usage

### 🔨 Build the Image
```bash
docker build --platform linux/amd64 -t pdf-outline-extractor .
```

---

## 🚀 Run the Container
```
docker run --rm \
  -v $(pwd)/input:/app/input:ro \
  -v $(pwd)/output:/app/output \
  --network none \
  pdf-outline-extractor
```

### ✅ JSON files will appear in the / output directory.

---

# 📋 Adobe Challenge Constraints Checklist

| Constraint                          | Status                                                  |
| ----------------------------------- | ------------------------------------------------------- |
| 🔒 **Offline execution**            | ✅ Fully offline – no internet required                  |
| 🧠 **Model size ≤ 200MB**           | ✅ No ML models used; lightweight heuristic approach     |
| ⚡ **≤ 10 seconds per 50-page PDF**  | ✅ Optimized, sub-8s on 50-page test                     |
| 📦 **Dockerized, AMD64-compatible** | ✅ Fully containerized, `--platform=linux/amd64` support |
| 🧾 **Output conforms to schema**    | ✅ JSON schema validated via `utils.py`                  |
| 🧼 **Memory-efficient**             | ✅ Uses PDFMiner with low memory footprint               |

---

# ❗ Known Limitations 

| Limitation                                                                  | Cause                                                                         | Future Fix                                                                             |
| --------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Some stylized PDFs with **missing structure** may produce fallback outlines | PDFMiner's limitation in reading graphical headers (e.g., embedded in images) | Integrate optional lightweight OCR (like Tesseract) in extended version                |
| Font/style inconsistencies in scanned PDFs                                  | Lack of embedded font info                                                    | Add preprocessing with layout detection using `pdf2image` + OCR (if constraint allows) |
| Lacks language detection for multilingual PDFs                              | Constraint to stay within size/time                                           | Extend `heading_classifier.py` with multilingual font handling heuristics              |

---

# 🧪 Example Outputs
Tested on:

-🧾 file01.pdf: Tabular application form → Extracts H1 from form header

-📚 file02.pdf: Narrative with multiple sections → Extracts all H1/H2/H3

-🗂️ file03.pdf: Detailed business plan → Captures nested headings

-🪪 file04.pdf: Card-style document → Detected as H1 with proper fallback

-💌 file05.pdf: Flyer-like design → Title fallback, card-optimized


---

# 🤝 Team & Credits
Built with ❤️ by Tech-Titans team for Adobe India Hackathon 2025.
