

<h1 align="center">📄 PDF Outline Extractor</h1>
<p align="center"><i>A robust, offline, containerized solution for Adobe Hackathon Challenge 1a — built to extract document outlines intelligently, efficiently, and beautifully.</i></p>

<br>

---


## 🧠 Overview

This project is a submission for **Adobe India Hackathon 2025 – Challenge 1a**.

> ⚡ **Goal:** Automatically extract meaningful structured information (title and heading outline) from PDFs and generate corresponding `.json` outputs – fully offline and within strict resource and performance constraints.


<br>

---



## 🚀 Features

✅ Accurate extraction of **document title and outline hierarchy (H1–H3)**  
✅ Works with **card-style**, **tabular**, **narrative**, and **structured documents**  
✅ Fully **offline**, **Dockerized**, and **under 200MB**  
✅ PDFMiner-based — no dependency on large OCR or cloud APIs  
✅ Post-processing to clean artifacts (e.g. repeated headings, footers, copyright)  
✅ Conforms to Adobe's [JSON Schema](https://github.com/jhaaj08/Adobe-India-Hackathon25/blob/main/Challenge_1a/sample_dataset/schema/output_schema.json)  


<br>

---



## 🧱 Architecture

```
📦 pdf_outline_extractor/
├── 📁 src/                         # 🧠 Core processing logic
│   ├── 🧰 extractor.py            # 🔁 Orchestrates PDF extraction & output JSON
│   ├── 🧠 heading_classifier.py   # 🧾 Heading classification logic (H1 / H2 / H3)
│   └── 🧪 utils.py                # ✅ Schema validation and fallbacks
├── 📂 input/                      # 📥 Input PDF files (read-only in container)
├── 📂 output/                     # 📤 Extracted JSON files go here
├── 🐳 Dockerfile                  # 📦 Container setup and environment configuration
├── 📜 requirements.txt            # 📚 Python dependencies
└── 📘 README.md                   # 📝 Project documentation (this file)

```



<br>

---


## 🧠 Modules & Responsibilities

| Module | Description |
|--------|-------------|
| `extractor.py` | Entry-point script that processes all PDFs from `/app/input` and saves JSON output to `/app/output`. Handles post-processing, fallback logic, and schema validation. |
| `heading_classifier.py` | Main PDF parsing logic using PDFMiner. Detects and classifies title and headings (H1, H2, H3) using heuristics based on font size, position, boldness, and numbering patterns. |
| `utils.py` | Validates the generated JSON output using the schema provided in the challenge. Ensures compliance. |


<br>

---


## 🛠️ Technologies Used

<div align="center" style="margin: 20px 0;">
  <img src="https://img.shields.io/badge/Python-3.10-blue?logo=python&logoColor=white" style="height:35px; margin: 5px;"/>
  <img src="https://img.shields.io/badge/PDFMiner-20221105-lightgrey" style="height:35px; margin: 5px;"/>
  <img src="https://img.shields.io/badge/Docker-Containerized-blue?logo=docker" style="height:35px; margin: 5px;"/>
  <img src="https://img.shields.io/badge/JSON-Schema-yellow?logo=json" style="height:35px; margin: 5px;"/>
</div>



<br>

---



## 🐳 Docker Usage

### 🔨 Build the Image
```bash
docker build --platform linux/amd64 -t pdf-outline-extractor .
```


<br>
---


### 🚀 Run the Container
```
docker run --rm \
  -v $(pwd)/input:/app/input:ro \
  -v $(pwd)/output:/app/output \
  --network none \
  pdf-outline-extractor
```

### ✅ JSON files will appear in the / output directory.


<br>

---


# 📦 Imported Modules & Their Purpose

| Module                | Function(s) Used                                                             | Purpose                                                                                        | Why It's Needed                                                                           |
| --------------------- | ---------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------- |
| `pdfminer.high_level` | `extract_pages`                                                              | Extracts layout elements from PDF pages like text boxes, lines, and images                     | Core function for layout-based PDF parsing in a structured manner                         |
| `pdfminer.layout`     | `LTTextContainer`, `LTTextBoxHorizontal`, `LTTextLineHorizontal`, `LAParams` | These represent individual layout elements on the page, used to identify and classify headings | Helps in analyzing structure, position, font style, and hierarchy of PDF contents         |
| `pathlib`             | `Path`                                                                       | Cross-platform file and directory operations (e.g., get filename, stem)                        | Cleaner and more robust file handling than `os.path`                                      |
| `re`                  | `re.match`, `re.sub`                                                         | Pattern matching and cleanup for detecting numbered sections and cleaning noisy text           | Used to recognize heading formats like `1. Introduction`, and remove non-heading patterns |
| `logging`             | `getLogger`, `basicConfig`, `info`, `error`                                  | Logging for debugging and tracing errors or internal decisions (e.g., title detection)         | Allows clean console logs and helps trace execution or unexpected behavior                |
| `typing`              | `Dict`, `List`, `Union`                                                      | Type annotations to improve code readability and IDE support                                   | Makes the code more maintainable and self-documenting for collaborative development       |


<br>

---

# 📋 Adobe Challenge Constraints Checklist

<div align="center">

<table>
  <thead>
    <tr>
      <th>Constraint</th>
      <th>Status</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <td>🔒 <strong>Offline execution</strong></td>
      <td>✅ Fully offline – no internet required</td>
    </tr>
    <tr>
      <td>🧠 <strong>Model size ≤ 200MB</strong></td>
      <td>✅ Lightweight heuristic approach</td>
    </tr>
    <tr>
      <td>⚡ <strong>≤ 10 seconds per 50-page PDF</strong></td>
      <td>✅ Optimized, sub-8s on 50-page test</td>
    </tr>
    <tr>
      <td>📦 <strong>Dockerized, AMD64-compatible</strong></td>
      <td>✅ Fully containerized, <code>--platform=linux/amd64</code> support</td>
    </tr>
    <tr>
      <td>🧾 <strong>Output conforms to schema</strong></td>
      <td>✅ JSON schema validated via <code>utils.py</code></td>
    </tr>
    <tr>
      <td>🧼 <strong>Memory-efficient</strong></td>
      <td>✅ Uses PDFMiner with low memory footprint</td>
    </tr>
  </tbody>
</table>

</div>


<br>

---


# ❗ Known Limitations 

| Limitation                                                                  | Cause                                                                         | Future Fix                                                                             |
| --------------------------------------------------------------------------- | ----------------------------------------------------------------------------- | -------------------------------------------------------------------------------------- |
| Some stylized PDFs with **missing structure** may produce fallback outlines | PDFMiner's limitation in reading graphical headers (e.g., embedded in images) | Integrate optional lightweight OCR (like Tesseract) in extended version                |
| Font/style inconsistencies in scanned PDFs                                  | Lack of embedded font info                                                    | Add preprocessing with layout detection using `pdf2image` + OCR (if constraint allows) |
| Lacks language detection for multilingual PDFs                              | Constraint to stay within size/time                                           | Extend `heading_classifier.py` with multilingual font handling heuristics              |

<br>

---



# 🧪 Example Outputs
Tested on:

- 🧾 file01.pdf: Tabular application form → Extracts H1 from form header
- 📚 file02.pdf: Narrative with multiple sections → Extracts all H1/H2/H3
- 🗂️ file03.pdf: Detailed business plan → Captures nested headings
- 🪪 file04.pdf: Card-style document → Detected as H1 with proper fallback
- 💌 file05.pdf: Flyer-like design → Title fallback, card-optimized


---

# 🤝 Team & Credits
Built with ❤️ by Tech-Titans team for Adobe India Hackathon 2025.
