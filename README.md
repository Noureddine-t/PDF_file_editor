# PDF Editor Application

## Description

The PDF Editor Application allows users to perform various operations on PDF files, such as merging multiple PDFs, deleting pages, adding pages, and reordering pages. The app also provides a graphical user interface (GUI) using Tkinter for ease of use, with drag-and-drop functionality for reordering pages and previewing thumbnails.

## Features

- **Merge PDFs**: Merge multiple PDF files into one document.
- **Delete Pages**: Remove specified pages from a PDF document.
- **Add Page**: Insert pages from another PDF into a specified position in the original PDF.
- **Reorganize Pages**: Reorder pages in a PDF by dragging and dropping thumbnails.

## Download

You can download the Windows exe file [here](https://github.com/Noureddine-t/PDF_file_editor/releases/tag/v1.0.0pyinstaller --onefile --noconsole --distpath dist --workpath build --specpath . main.py
)

## Requirements

- Python 3.12 or higher
- Required Python libraries:
  - `tkinter` (for the GUI)
  - `pypdf` (for PDF handling)
  - `fitz` (PyMuPDF for rendering PDFs and creating thumbnails)
  - `Pillow` (for image processing)

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/noureddine-t/PDF_file_editor.git
    ```

2. Install the required dependencies:
    ```bash
    pip install -r requirements.txt
    ```

3. Run the application:
    ```bash
    python main.py
    ```
