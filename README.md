# Callimaque

Callimaque is a specialized software tool designed to assist in the digitization and cataloging of personal libraries. It is designed to work with a custom scanning setup (such as a mechanical arm with a camera) or with existing image collections.

## Features

-   **Image Viewer**: Browse through a directory of book scans or photos.
-   **Magnifying Glass**: Inspect high-resolution details of book spines or pages with a built-in magnifier tool.
-   **OCR Integration**: Automatically extracts text from the current image using Tesseract OCR (via `pytesseract`).
-   **Text Editor**: A built-in editor to review, correct, and format the extracted text.
-   **Append Workflow**: Easily append corrected text to a master catalog file.

## Requirements

-   Python 3.x
-   `tkinter` (usually included with Python)
-   `Pillow` (PIL Fork)
-   `pytesseract`
-   Tesseract-OCR engine installed on your system.

## Installation

1.  Clone the repository.
2.  Install python dependencies:
    ```bash
    pip install Pillow pytesseract
    ```
3.  Ensure Tesseract-OCR is installed and accessible in your system path.

## Usage

1.  Run the application:
    ```bash
    python GUI.py
    ```
2.  **Directory**: Select the folder containing your images using the "Browse" button next to "Directory".
3.  **Destination**: Select the output text file using the "Browse" button next to "Destination".
4.  **Navigation**: Use the `<` and `>` buttons to navigate through images.
5.  **OCR**: Text is automatically extracted and displayed in the editor when an image is loaded.
6.  **Edit & Save**: Correct the text if necessary and click "Append" to save it to your destination file.

## Concept

This software is part of a larger concept "St-Arnaud Concept", envisioning a semi-automated scanning process involving mechanical arms, mobile device cameras, and efficient workflow optimization for digitizing physical libraries.
