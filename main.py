import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pypdf import PdfReader, PdfWriter
import fitz  # PyMuPDF
from PIL import Image, ImageTk


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
    for i in range(position):
        writer.add_page(reader_orig.pages[i])
    for page in reader_new.pages:
        writer.add_page(page)
    for i in range(position, len(reader_orig.pages)):
        writer.add_page(reader_orig.pages[i])
    with open(output, "wb") as f:
        writer.write(f)


def reorder_pdf(pdf_file, new_order, output):
    reader = PdfReader(pdf_file)
    writer = PdfWriter()
    for idx in new_order:
        writer.add_page(reader.pages[idx])
    with open(output, "wb") as f:
        writer.write(f)


# --- Drag & Drop Reorder Window using Thumbnails ---
class DragDropReorder(tk.Toplevel):
    def __init__(self, parent, pdf_file, save_callback):
        tk.Toplevel.__init__(self, parent)
        self.title("Reorder Pages")
        self.geometry("420x650")  # increased window size
        self.save_callback = save_callback
        self.pdf_file = pdf_file
        self.thumbs = []         # keep PhotoImage references
        self.page_order = []     # original page indices
        self.items = []          # list of tuples: (canvas item, width, height)
        self.margin = 10
        self.canvas_width = 400  # fixed canvas width

        # Create canvas with vertical scrollbar and fixed width
        self.canvas = tk.Canvas(self, width=self.canvas_width, bg="white")
        vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=vsb.set)
        vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)

        self.load_thumbnails()
        self.drag_data = {"item": None, "y": 0, "index": None}

        self.canvas.bind("<ButtonPress-1>", self.on_start_drag)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_drop)

        # Bind mouse wheel for scrolling:
        # Windows and macOS:
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        # Linux uses Button-4 (scroll up) and Button-5 (scroll down)
        self.canvas.bind("<Button-4>", self._on_mousewheel)
        self.canvas.bind("<Button-5>", self._on_mousewheel)

        save_button = ttk.Button(self, text="Save Order", command=self.on_save)
        save_button.pack(pady=5)

    def _on_mousewheel(self, event):
        # Windows: event.delta is a multiple of 120
        if event.num == 4 or event.delta > 0:
            self.canvas.yview_scroll(-1, "units")
        elif event.num == 5 or event.delta < 0:
            self.canvas.yview_scroll(1, "units")

    def load_thumbnails(self):
        try:
            doc = fitz.open(self.pdf_file)
        except Exception as e:
            messagebox.showerror("Error", f"Could not open PDF: {e}")
            self.destroy()
            return
        y = self.margin
        # Use full available width minus margins
        desired_width = self.canvas_width - 2 * self.margin
        for i in range(len(doc)):
            page = doc.load_page(i)
            # Compute zoom factor so that page width equals desired_width
            zoom = desired_width / page.rect.width
            thumb_height = page.rect.height * zoom
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat)
            mode = "RGB" if pix.alpha == 0 else "RGBA"
            img = Image.frombytes(mode, [pix.width, pix.height], pix.samples)
            photo = ImageTk.PhotoImage(img)
            self.thumbs.append(photo)
            self.page_order.append(i)
            # Center the image horizontally on the canvas
            x = self.margin  # image width == desired_width
            item = self.canvas.create_image(x, y, anchor="nw", image=photo)
            # Center label below the image
            self.canvas.create_text(self.canvas_width/2, y + thumb_height + 2, anchor="n", text=f"Page {i+1}")
            self.items.append((item, pix.width, thumb_height))
            y += thumb_height + self.margin * 2
        self.canvas.config(scrollregion=self.canvas.bbox("all"))

    def on_start_drag(self, event):
        x = self.canvas.canvasx(event.x)
        y = self.canvas.canvasy(event.y)
        item = self.canvas.find_closest(x, y)[0]
        for idx, (itm, w, h) in enumerate(self.items):
            if itm == item:
                self.drag_data["item"] = idx  # store index
                self.drag_data["y"] = y
                break

    def on_drag(self, event):
        if self.drag_data["item"] is None:
            return
        new_y = self.canvas.canvasy(event.y)
        dy = new_y - self.drag_data["y"]
        idx = self.drag_data["item"]
        item, w, h = self.items[idx]
        self.canvas.move(item, 0, dy)
        self.drag_data["y"] = new_y

    def on_drop(self, event):
        if self.drag_data["item"] is None:
            return
        # Get current y-coordinates and sort items
        positions = []
        for idx, (item, w, h) in enumerate(self.items):
            pos = self.canvas.coords(item)[1]
            positions.append((idx, pos))
        positions.sort(key=lambda x: x[1])
        new_order = [self.page_order[idx] for idx, pos in positions]
        self.items = [self.items[idx] for idx, pos in positions]
        self.page_order = new_order
        self.redraw_items()
        self.drag_data = {"item": None, "y": 0, "index": None}

    def redraw_items(self):
        y = self.margin
        new_items = []
        for (item, w, h) in self.items:
            new_x = (self.canvas_width - w) / 2
            self.canvas.coords(item, new_x, y)
            y += h + self.margin * 2
            new_items.append((item, w, h))
        self.items = new_items

    def on_save(self):
        self.save_callback(self.page_order)
        self.destroy()


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
        reorg_frame = ttk.Frame(self.notebook)
        self.notebook.add(reorg_frame, text="Reorganize PDF")

        ttk.Label(reorg_frame, text="Select PDF file:").grid(row=0, column=0, sticky='w', padx=5, pady=5)
        self.reorg_file_entry = ttk.Entry(reorg_frame, width=50)
        self.reorg_file_entry.grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(reorg_frame, text="Browse", command=self.browse_reorg_file).grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(reorg_frame, text="Output Directory:").grid(row=1, column=0, sticky='w', padx=5, pady=5)
        self.reorg_output_dir_entry = ttk.Entry(reorg_frame, width=50)
        self.reorg_output_dir_entry.grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(reorg_frame, text="Browse Dir", command=self.browse_reorg_output_dir).grid(row=1, column=2, padx=5,
                                                                                              pady=5)

        ttk.Label(reorg_frame, text="Filename:").grid(row=2, column=0, sticky='w', padx=5, pady=5)
        self.reorg_filename_entry = ttk.Entry(reorg_frame, width=50)
        self.reorg_filename_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Button(reorg_frame, text="Reorganize", command=self.reorganize_action).grid(row=3, column=1, pady=10)

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

        def save_order_callback(new_order):
            output = build_output_path(out_dir, filename)
            try:
                reorder_pdf(pdf_file, new_order, output)
                messagebox.showinfo("Success", f"PDF reorganized successfully!\nSaved as:\n{output}")
            except Exception as e:
                messagebox.showerror("Error", str(e))

        # Open the drag-and-drop reorder window that shows thumbnails
        DragDropReorder(self.root, pdf_file, save_order_callback)


# --- Main ---
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFEditorApp(root)
    root.mainloop()
