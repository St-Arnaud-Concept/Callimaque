# Callimaque - OCR & AI Text Correction Tool

Callimaque is a modern Python application designed to streamline the process of digitizing documents. It combines Optical Character Recognition (OCR) with advanced AI text correction to transform images of text into clean, editable digital content.

![Callimaque UI](Callimaque.png)
*(Note: Screenshot placeholder)*

## Features

*   **Image Viewer & OCR:** Browse directories of images and automatically extract text using Tesseract OCR.
*   **Magnifying Glass:** Inspect image details closely with a built-in magnifying glass tool.
*   **AI Text Correction:**
    *   Integrated AI-powered correction to fix OCR errors (typos, broken words, formatting).
    *   **Gemini 1.5 Flash** integration (requires API Key).
    *   Extensible architecture for future models (Claude, GPT, Grok).
*   **Modern UI:** Built with `customtkinter` for a sleek, dark-mode friendly interface.
*   **Text Editor:** Full-featured text area to review and edit extracted text.
*   **File Management:** Append corrected text to destination files directly from the app.

## Installation

### Prerequisites
*   **Python 3.8+**
*   **Tesseract-OCR:** You must have Tesseract installed on your system.
    *   **Linux (Debian/Ubuntu):** `sudo apt install tesseract-ocr`
    *   **Windows:** Download installer from [UB-Mannheim/tesseract](https://github.com/UB-Mannheim/tesseract/wiki).
    *   **macOS:** `brew install tesseract`

### Setup
1.  **Clone the repository:**
    ```bash
    git clone https://github.com/YourUsername/Callimaque.git
    cd Callimaque
    ```

2.  **Create a virtual environment:**
    ```bash
    python3 -m venv .venv
    source .venv/bin/activate  # Linux/macOS
    # .venv\Scripts\activate   # Windows
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r dependencies.txt
    ```

## Usage

1.  **Run the application:**
    ```bash
    python3 GUI.py
    ```

2.  **Load Images:**
    *   Click **Browse** next to the "Directory" field to select a folder containing images (JPG, PNG).
    *   The first image will load, and OCR will automatically run.

3.  **Navigate:**
    *   Use the **<** and **>** buttons to flip through images in the folder.
    *   The text editor on the left will update with the new OCR results.

4.  **AI Correction:**
    *   Click the orange **Ai Correction** button to fix the text in the editor using the selected AI model.
    *   **First Run:** You will be prompted to enter your API Key (e.g., for Google Gemini).
    *   **Change Model:** Click the **>** arrow on the button to open the settings panel. Select a model and update/save your API Key.

5.  **Save/Append:**
    *   **Save File:** Use the `File > Save` menu.
    *   **Append:** Select a destination file at the bottom and click **Append Text** to add the current editor content to the end of that file.

## AI Configuration

Currently, **Google Gemini 1.5 Flash** is fully implemented.

1.  Get a free API Key from [Google AI Studio](https://aistudio.google.com/).
2.  In Callimaque, open the AI menu (`>`), select "Gemini 1.5 Flash", paste your key, and you're ready to go.

## Project Structure

*   `GUI.py`: Main application entry point and UI logic.
*   `ai_manager.py`: Handles interactions with AI APIs (Gemini, etc.).
*   `dependencies.txt`: List of Python packages required.