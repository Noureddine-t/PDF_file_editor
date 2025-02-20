import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pypdf import PdfReader, PdfWriter


# --- Helper Function ---
def ensure_pdf_extension(filename):
    if not filename.lower().endswith('.pdf'):
        return filename + '.pdf'
    return filename


# --- Backend Functions ---
def merge_pdfs(pdf_list, output):
    writer = PdfWriter()
    for pdf in pdf_list:
        reader = PdfReader(pdf)
        for page in reader.pages:
            writer.add_page(page)
    with open(output, "wb") as f:
        writer.write(f)


def delete_pages(pdf_file, pages_to_delete, output):
    reader = PdfReader(pdf_file)
    writer = PdfWriter()
    for i, page in enumerate(reader.pages):
        if i not in pages_to_delete:
            writer.add_page(page)
    with open(output, "wb") as f:
        writer.write(f)


def add_page(original_pdf, page_to_add, position, output):
    reader_orig = PdfReader(original_pdf)
    reader_new = PdfReader(page_to_add)
    writer = PdfWriter()
    # Add pages before the insertion point
    for i in range(position):
        writer.add_page(reader_orig.pages[i])
    # Insert new page(s)
    for page in reader_new.pages:
        writer.add_page(page)
    # Append remaining pages
    for i in range(position, len(reader_orig.pages)):
        writer.add_page(reader_orig.pages[i])
    with open(output, "wb") as f:
        writer.write(f)


# --- GUI Application using Tkinter ---
class PDFEditorApp:
    def __init__(self, root):
        self.root = root
        root.title("PDF Editor")
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True)

        self.create_merge_tab()
        self.create_delete_tab()
        self.create_add_tab()

    def create_merge_tab(self):
        merge_frame = ttk.Frame(self.notebook)
        self.notebook.add(merge_frame, text="Merge PDFs")

        ttk.Label(merge_frame, text="Select PDF files to merge:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.merge_files_entry = ttk.Entry(merge_frame, width=50)
        self.merge_files_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(merge_frame, text="Browse", command=self.browse_merge_files).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(merge_frame, text="Output file:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.merge_output_entry = ttk.Entry(merge_frame, width=50)
        self.merge_output_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(merge_frame, text="Save As", command=self.save_merge_output).grid(row=1, column=2, padx=5, pady=5)

        ttk.Button(merge_frame, text="Merge", command=self.merge_action).grid(row=2, column=1, pady=10)

    def create_delete_tab(self):
        delete_frame = ttk.Frame(self.notebook)
        self.notebook.add(delete_frame, text="Delete Pages")

        ttk.Label(delete_frame, text="Select PDF file:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.delete_file_entry = ttk.Entry(delete_frame, width=50)
        self.delete_file_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(delete_frame, text="Browse", command=self.browse_delete_file).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(delete_frame, text="Pages to delete (0-indexed, comma separated):").grid(row=1, column=0, sticky='w',
                                                                                           padx=5, pady=5)
        self.delete_pages_entry = ttk.Entry(delete_frame, width=50)
        self.delete_pages_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(delete_frame, text="Output file:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.delete_output_entry = ttk.Entry(delete_frame, width=50)
        self.delete_output_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(delete_frame, text="Save As", command=self.save_delete_output).grid(row=2, column=2, padx=5, pady=5)

        ttk.Button(delete_frame, text="Delete Pages", command=self.delete_action).grid(row=3, column=1, pady=10)

    def create_add_tab(self):
        add_frame = ttk.Frame(self.notebook)
        self.notebook.add(add_frame, text="Add Page")

        ttk.Label(add_frame, text="Select original PDF file:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.add_original_entry = ttk.Entry(add_frame, width=50)
        self.add_original_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(add_frame, text="Browse", command=self.browse_add_original).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(add_frame, text="Select PDF file with page(s) to add:").grid(row=1, column=0, sticky='w', padx=5,
                                                                               pady=5)
        self.add_page_entry = ttk.Entry(add_frame, width=50)
        self.add_page_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(add_frame, text="Browse", command=self.browse_add_page).grid(row=1, column=2, padx=5, pady=5)

        ttk.Label(add_frame, text="Insert position (0-indexed):").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.add_position_entry = ttk.Entry(add_frame, width=50)
        self.add_position_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(add_frame, text="Output file:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.add_output_entry = ttk.Entry(add_frame, width=50)
        self.add_output_entry.grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(add_frame, text="Save As", command=self.save_add_output).grid(row=3, column=2, padx=5, pady=5)

        ttk.Button(add_frame, text="Add Page", command=self.add_action).grid(row=4, column=1, pady=10)

    # --- File Dialog Methods ---
    def browse_merge_files(self):
        files = filedialog.askopenfilenames(title="Select PDF files", filetypes=[("PDF Files", "*.pdf")])
        if files:
            self.merge_files_entry.delete(0, tk.END)
            self.merge_files_entry.insert(0, ";".join(files))

    def save_merge_output(self):
        file = filedialog.asksaveasfilename(title="Save Merged PDF", defaultextension=".pdf",
                                            filetypes=[("PDF Files", "*.pdf")])
        if file:
            self.merge_output_entry.delete(0, tk.END)
            self.merge_output_entry.insert(0, file)

    def browse_delete_file(self):
        file = filedialog.askopenfilename(title="Select PDF file", filetypes=[("PDF Files", "*.pdf")])
        if file:
            self.delete_file_entry.delete(0, tk.END)
            self.delete_file_entry.insert(0, file)

    def save_delete_output(self):
        file = filedialog.asksaveasfilename(title="Save PDF", defaultextension=".pdf",
                                            filetypes=[("PDF Files", "*.pdf")])
        if file:
            self.delete_output_entry.delete(0, tk.END)
            self.delete_output_entry.insert(0, file)

    def browse_add_original(self):
        file = filedialog.askopenfilename(title="Select original PDF", filetypes=[("PDF Files", "*.pdf")])
        if file:
            self.add_original_entry.delete(0, tk.END)
            self.add_original_entry.insert(0, file)

    def browse_add_page(self):
        file = filedialog.askopenfilename(title="Select PDF with page(s)", filetypes=[("PDF Files", "*.pdf")])
        if file:
            self.add_page_entry.delete(0, tk.END)
            self.add_page_entry.insert(0, file)

    def save_add_output(self):
        file = filedialog.asksaveasfilename(title="Save PDF", defaultextension=".pdf",
                                            filetypes=[("PDF Files", "*.pdf")])
        if file:
            self.add_output_entry.delete(0, tk.END)
            self.add_output_entry.insert(0, file)

    # --- Action Methods ---
    def merge_action(self):
        files_str = self.merge_files_entry.get()
        output = ensure_pdf_extension(self.merge_output_entry.get())
        if not files_str or not output:
            messagebox.showerror("Error", "Please specify input files and output file.")
            return
        pdf_list = files_str.split(";")
        try:
            merge_pdfs(pdf_list, output)
            messagebox.showinfo("Success", "PDFs merged successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_action(self):
        pdf_file = self.delete_file_entry.get()
        output = ensure_pdf_extension(self.delete_output_entry.get())
        pages_str = self.delete_pages_entry.get()
        if not pdf_file or not output or not pages_str:
            messagebox.showerror("Error", "Please specify all fields.")
            return
        try:
            pages_to_delete = [int(x.strip()) for x in pages_str.split(",") if x.strip().isdigit()]
            delete_pages(pdf_file, pages_to_delete, output)
            messagebox.showinfo("Success", "Pages deleted successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_action(self):
        original = self.add_original_entry.get()
        add_file = self.add_page_entry.get()
        output = ensure_pdf_extension(self.add_output_entry.get())
        pos_str = self.add_position_entry.get()
        if not original or not add_file or not output or not pos_str:
            messagebox.showerror("Error", "Please specify all fields.")
            return
        try:
            position = int(pos_str)
            add_page(original, add_file, position, output)
            messagebox.showinfo("Success", "Page(s) added successfully!")
        except Exception as e:
            messagebox.showerror("Error", str(e))


# --- Main ---
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFEditorApp(root)
    root.mainloop()
