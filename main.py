import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pypdf import PdfReader, PdfWriter


# --- Helper Functions ---
def ensure_pdf_extension(filename):
    if not filename.lower().endswith('.pdf'):
        return filename + '.pdf'
    return filename


def build_output_path(directory, filename):
    full = os.path.join(directory, filename)
    return ensure_pdf_extension(full)


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


def reorder_pdf(pdf_file, new_order, output):
    reader = PdfReader(pdf_file)
    writer = PdfWriter()
    for index in new_order:
        writer.add_page(reader.pages[index])
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
        self.create_reorganize_tab()

    def create_merge_tab(self):
        merge_frame = ttk.Frame(self.notebook)
        self.notebook.add(merge_frame, text="Merge PDFs")

        ttk.Label(merge_frame, text="Select PDF files to merge:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.merge_files_entry = ttk.Entry(merge_frame, width=50)
        self.merge_files_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(merge_frame, text="Browse", command=self.browse_merge_files).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(merge_frame, text="Output Directory:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.merge_output_dir_entry = ttk.Entry(merge_frame, width=50)
        self.merge_output_dir_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(merge_frame, text="Browse Dir", command=self.browse_merge_output_dir).grid(row=1, column=2, padx=5,
                                                                                              pady=5)

        ttk.Label(merge_frame, text="Filename:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.merge_filename_entry = ttk.Entry(merge_frame, width=50)
        self.merge_filename_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(merge_frame, text="Merge", command=self.merge_action).grid(row=3, column=1, pady=10)

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

        ttk.Label(delete_frame, text="Output Directory:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.delete_output_dir_entry = ttk.Entry(delete_frame, width=50)
        self.delete_output_dir_entry.grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(delete_frame, text="Browse Dir", command=self.browse_delete_output_dir).grid(row=2, column=2, padx=5,
                                                                                                pady=5)

        ttk.Label(delete_frame, text="Filename:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.delete_filename_entry = ttk.Entry(delete_frame, width=50)
        self.delete_filename_entry.grid(row=3, column=1, padx=5, pady=5)

        ttk.Button(delete_frame, text="Delete Pages", command=self.delete_action).grid(row=4, column=1, pady=10)

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

        ttk.Label(add_frame, text="Output Directory:").grid(row=3, column=0, sticky='w', padx=5, pady=5)
        self.add_output_dir_entry = ttk.Entry(add_frame, width=50)
        self.add_output_dir_entry.grid(row=3, column=1, padx=5, pady=5)
        ttk.Button(add_frame, text="Browse Dir", command=self.browse_add_output_dir).grid(row=3, column=2, padx=5,
                                                                                          pady=5)

        ttk.Label(add_frame, text="Filename:").grid(row=4, column=0, sticky='w', padx=5, pady=5)
        self.add_filename_entry = ttk.Entry(add_frame, width=50)
        self.add_filename_entry.grid(row=4, column=1, padx=5, pady=5)

        ttk.Button(add_frame, text="Add Page", command=self.add_action).grid(row=5, column=1, pady=10)

    def create_reorganize_tab(self):
        reorganize_frame = ttk.Frame(self.notebook)
        self.notebook.add(reorganize_frame, text="Reorganize PDF")

        ttk.Label(reorganize_frame, text="Select PDF file:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.reorg_file_entry = ttk.Entry(reorganize_frame, width=50)
        self.reorg_file_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(reorganize_frame, text="Browse", command=self.browse_reorg_file).grid(row=0, column=2, padx=5,
                                                                                         pady=5)

        ttk.Label(reorganize_frame, text="Output Directory:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.reorg_output_dir_entry = ttk.Entry(reorganize_frame, width=50)
        self.reorg_output_dir_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(reorganize_frame, text="Browse Dir", command=self.browse_reorg_output_dir).grid(row=1, column=2,
                                                                                                   padx=5, pady=5)

        ttk.Label(reorganize_frame, text="Filename:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.reorg_filename_entry = ttk.Entry(reorganize_frame, width=50)
        self.reorg_filename_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(reorganize_frame, text="Reorganize", command=self.reorganize_action).grid(row=3, column=1, pady=10)

    # --- File/Directory Dialog Methods ---
    def browse_merge_files(self):
        files = filedialog.askopenfilenames(title="Select PDF files", filetypes=[("PDF Files", "*.pdf")])
        if files:
            self.merge_files_entry.delete(0, tk.END)
            self.merge_files_entry.insert(0, ";".join(files))

    def browse_merge_output_dir(self):
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.merge_output_dir_entry.delete(0, tk.END)
            self.merge_output_dir_entry.insert(0, directory)

    def browse_delete_file(self):
        file = filedialog.askopenfilename(title="Select PDF file", filetypes=[("PDF Files", "*.pdf")])
        if file:
            self.delete_file_entry.delete(0, tk.END)
            self.delete_file_entry.insert(0, file)

    def browse_delete_output_dir(self):
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.delete_output_dir_entry.delete(0, tk.END)
            self.delete_output_dir_entry.insert(0, directory)

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

    def browse_add_output_dir(self):
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.add_output_dir_entry.delete(0, tk.END)
            self.add_output_dir_entry.insert(0, directory)

    def browse_reorg_file(self):
        file = filedialog.askopenfilename(title="Select PDF file", filetypes=[("PDF Files", "*.pdf")])
        if file:
            self.reorg_file_entry.delete(0, tk.END)
            self.reorg_file_entry.insert(0, file)

    def browse_reorg_output_dir(self):
        directory = filedialog.askdirectory(title="Select output directory")
        if directory:
            self.reorg_output_dir_entry.delete(0, tk.END)
            self.reorg_output_dir_entry.insert(0, directory)

    # --- Action Methods ---
    def merge_action(self):
        files_str = self.merge_files_entry.get()
        out_dir = self.merge_output_dir_entry.get()
        filename = self.merge_filename_entry.get()
        if not files_str or not out_dir or not filename:
            messagebox.showerror("Error", "Please specify input files, output directory, and filename.")
            return
        output = build_output_path(out_dir, filename)
        pdf_list = files_str.split(";")
        try:
            merge_pdfs(pdf_list, output)
            messagebox.showinfo("Success", f"PDFs merged successfully!\nSaved as:\n{output}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_action(self):
        pdf_file = self.delete_file_entry.get()
        out_dir = self.delete_output_dir_entry.get()
        filename = self.delete_filename_entry.get()
        pages_str = self.delete_pages_entry.get()
        if not pdf_file or not out_dir or not filename or not pages_str:
            messagebox.showerror("Error", "Please specify all fields.")
            return
        output = build_output_path(out_dir, filename)
        try:
            pages_to_delete = [int(x.strip()) for x in pages_str.split(",") if x.strip().isdigit()]
            delete_pages(pdf_file, pages_to_delete, output)
            messagebox.showinfo("Success", f"Pages deleted successfully!\nSaved as:\n{output}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def add_action(self):
        original = self.add_original_entry.get()
        add_file = self.add_page_entry.get()
        out_dir = self.add_output_dir_entry.get()
        filename = self.add_filename_entry.get()
        pos_str = self.add_position_entry.get()
        if not original or not add_file or not out_dir or not filename or not pos_str:
            messagebox.showerror("Error", "Please specify all fields.")
            return
        output = build_output_path(out_dir, filename)
        try:
            position = int(pos_str)
            add_page(original, add_file, position, output)
            messagebox.showinfo("Success", f"Page(s) added successfully!\nSaved as:\n{output}")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def reorganize_action(self):
        pdf_file = self.reorg_file_entry.get()
        out_dir = self.reorg_output_dir_entry.get()
        filename = self.reorg_filename_entry.get()
        if not pdf_file or not out_dir or not filename:
            messagebox.showerror("Error", "Please specify the PDF file, output directory, and filename.")
            return
        # Open pop-up window for reordering
        try:
            reader = PdfReader(pdf_file)
            num_pages = len(reader.pages)
        except Exception as e:
            messagebox.showerror("Error", f"Could not read PDF: {e}")
            return

        reorder_win = tk.Toplevel(self.root)
        reorder_win.title("Reorder Pages")
        reorder_win.geometry("300x400")

        ttk.Label(reorder_win, text="Drag to reorder pages using buttons:").pack(pady=5)

        # Create a Listbox with scrollbar
        listbox_frame = ttk.Frame(reorder_win)
        listbox_frame.pack(fill='both', expand=True, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical")
        self.page_listbox = tk.Listbox(listbox_frame, yscrollcommand=scrollbar.set, selectmode=tk.SINGLE)
        scrollbar.config(command=self.page_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.page_listbox.pack(side="left", fill="both", expand=True)

        # Populate listbox with page labels (store indices as values)
        for i in range(num_pages):
            self.page_listbox.insert(tk.END, f"Page {i + 1}")

        # Buttons for moving items up and down
        btn_frame = ttk.Frame(reorder_win)
        btn_frame.pack(pady=5)
        ttk.Button(btn_frame, text="Move Up", command=self.move_up).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Move Down", command=self.move_down).grid(row=0, column=1, padx=5)

        # Save and Cancel buttons
        action_frame = ttk.Frame(reorder_win)
        action_frame.pack(pady=10)
        ttk.Button(action_frame, text="Save Order",
                   command=lambda: self.save_reorder(pdf_file, out_dir, filename, reorder_win)).grid(row=0, column=0,
                                                                                                     padx=5)
        ttk.Button(action_frame, text="Cancel", command=reorder_win.destroy).grid(row=0, column=1, padx=5)

    def move_up(self):
        selection = self.page_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        if index == 0:
            return
        text = self.page_listbox.get(index)
        self.page_listbox.delete(index)
        self.page_listbox.insert(index - 1, text)
        self.page_listbox.selection_set(index - 1)

    def move_down(self):
        selection = self.page_listbox.curselection()
        if not selection:
            return
        index = selection[0]
        if index == self.page_listbox.size() - 1:
            return
        text = self.page_listbox.get(index)
        self.page_listbox.delete(index)
        self.page_listbox.insert(index + 1, text)
        self.page_listbox.selection_set(index + 1)

    def save_reorder(self, pdf_file, out_dir, filename, window):
        # Retrieve new order from listbox (the order of pages corresponds to their new index)
        new_order = []
        for i in range(self.page_listbox.size()):
            # The displayed text is "Page X", so subtract 1 to get the 0-indexed page number
            item = self.page_listbox.get(i)
            try:
                page_num = int(item.split()[1]) - 1
                new_order.append(page_num)
            except Exception:
                messagebox.showerror("Error", "Invalid page label encountered.")
                return
        output = build_output_path(out_dir, filename)
        try:
            reorder_pdf(pdf_file, new_order, output)
            messagebox.showinfo("Success", f"PDF reorganized successfully!\nSaved as:\n{output}")
            window.destroy()
        except Exception as e:
            messagebox.showerror("Error", str(e))
            window.destroy()


# --- Main ---
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFEditorApp(root)
    root.mainloop()
