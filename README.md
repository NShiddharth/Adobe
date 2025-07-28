# PDF Outline Extractor

This project extracts a structured outline (Title, H1, H2, H3) from PDF documents. It is built to run entirely offline in a Docker container, adhering to the hackathon constraints for performance, size, and connectivity.

## Approach

The solution uses a robust, multi-stage, rule-based pipeline designed for multilingual support:

1.  **Layout Parsing (\PyMuPDF\):** The process begins by using the powerful \PyMuPDF\ (Fitz) library to parse the PDF. This library excels at handling complex layouts and a wide variety of character encodings (including CJK languages), reliably extracting structured text blocks.

2.  *Heading Classification (Rule-Based):* Instead of a less predictable ML model, a fast and effective rule-based engine classifies text blocks. The rules are designed to be multilingual, identifying patterns from both English documents (e.g., "Chapter 1", "1.1.2") and Japanese documents (e.g., \●\, \第1章\).

3.  *Intelligent Post-Processing:* This is the most critical stage. A sophisticated post-processor cleans the classified headings. It intelligently finds the correct title, automatically detects and removes repeating page headers and footers, filters out noise and duplicates from the Table of Contents, and formats the final, clean outline.

## Libraries Used

-   **\PyMuPDF\**: For robust, high-performance PDF text and layout extraction.
-   **\fasttext\**: For fast, offline language detection (used in earlier development stages).
-   *Other core libraries*: \scikit-learn\, \pandas\, \joblib\ for data handling and model training during development.

## How to Build and Run

The entire solution is containerized with Docker for portability and offline execution.

### Prerequisites

-   Docker must be installed and running on your system.
-   All Python package dependencies must be downloaded into the \packages/\ directory first.

### Step 1: Download Offline Dependencies

To ensure the Docker build works completely offline, first run this command to download all necessary Python packages into a local \packages\ folder:

\\\`bash
pip download -r requirements.txt -d packages/
\\\`

### Step 2: Build the Docker Image

Navigate to the project's root directory in your terminal and run the build command. This bundles all dependencies and application code into a self-contained image.

\\\`bash
docker build -t pdf-extractor .
\\\`

### Step 3: Run the Container

1.  Place your PDF files into the \input\ folder.

2.  Run the container using the appropriate command for your system. It will process all PDFs from the \input\ folder and save the JSON results to the \output\ folder.

    *For PowerShell (Windows):*

    \\\`powershell
    docker run --rm -v "${pwd}/input:/app/input" -v "${pwd}/output:/app/output" pdf-extractor
    \\\`

    *For Linux, macOS, or Git Bash:*

    \\\`bash
    docker run --rm -v $(pwd)/input:/app/input -v $(pwd)/output:/app/output pdf-extractor
    \\\`

3.  Check the \output\ folder for your generated JSON files.
