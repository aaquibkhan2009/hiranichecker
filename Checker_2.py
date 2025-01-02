#!/usr/bin/env python
# coding: utf-8

# In[1]:


import fitz  # PyMuPDF
import math
import tkinter as tk
from tkinter import filedialog, messagebox

def extract_highlight_details(pdf_path):
    # Define the mapping of colors to their purpose
    color_map = {
        "Technical Highlight (Yellow)": (1, 1, 0),  # Hirani Group scope
        "Payment/Invoice (Green)": (0, 1, 0),  # Payment/Invoice requirements
        "Exclusion (Red)": (1, 0, 0),  # Exclusion
        "Client Deliverables (Blue)": (0, 0, 1),  # Client deliverables
        "Schedules (Brown)": (0.6, 0.4, 0.2),  # Schedules
    }

    def closest_color(color):
        """Find the closest known color using Euclidean distance."""
        min_distance = float("inf")
        closest_name = "Unknown Highlight"
        for name, rgb in color_map.items():
            distance = math.sqrt(sum((color[i] - rgb[i]) ** 2 for i in range(3)))
            if distance < min_distance:
                min_distance = distance
                closest_name = name
        return closest_name

    try:
        doc = fitz.open(pdf_path)
    except Exception as e:
        messagebox.showerror("Error", f"Could not open PDF: {str(e)}")
        return

    results = []

    for page_number in range(len(doc)):
        page = doc[page_number]
        for annot in page.annots() or []:
            try:
                if annot.type[0] in [8, 1, 21]:  # Include highlight and free text annotations
                    color = annot.colors.get("stroke") or annot.colors.get("fill")
                    if color:
                        # Normalize color and check transparency
                        normalized_color = tuple(round(c, 1) for c in color)
                        category = closest_color(normalized_color)  # Match with closest known color
                        rect = annot.rect  # Get annotation rectangle
                        highlighted_text = page.get_text("words", clip=rect)
                        results.append(f"{category} found on page {page_number + 1}: {highlighted_text}")
                    else:
                        results.append(f"Uncolored annotation found on page {page_number + 1}")
            except Exception as e:
                results.append(f"Error processing annotation on page {page_number + 1}: {str(e)}")

    if results:
        show_results(results)
    else:
        messagebox.showinfo("No Highlights", "No highlights detected in the selected PDF.")

def show_results(results):
    def copy_to_clipboard():
        result_window.clipboard_clear()
        result_window.clipboard_append("\n".join(results))
        result_window.update()
        messagebox.showinfo("Copied", "Highlights have been copied to the clipboard!")

    result_window = tk.Toplevel()
    result_window.title("Highlights Found")

    text_widget = tk.Text(result_window, wrap="word", height=20, width=70)
    text_widget.insert("1.0", "\n".join(results))
    text_widget.configure(state="disabled")
    text_widget.pack(pady=10)

    copy_button = tk.Button(result_window, text="Copy to Clipboard", command=copy_to_clipboard)
    copy_button.pack(side="left", padx=10, pady=10)

    close_button = tk.Button(result_window, text="Close", command=result_window.destroy)
    close_button.pack(side="right", padx=10, pady=10)

def select_pdf_and_extract():
    pdf_path = filedialog.askopenfilename(
        title="Select PDF File",
        filetypes=[("PDF Files", "*.pdf")]
    )
    if pdf_path:
        extract_highlight_details(pdf_path)

def main():
    root = tk.Tk()
    root.title("PDF Highlight Extractor")
    root.geometry("400x200")

    label = tk.Label(root, text="Select a PDF to analyze highlights", font=("Arial", 12))
    label.pack(pady=20)

    button = tk.Button(root, text="Select PDF", command=select_pdf_and_extract, font=("Arial", 12))
    button.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    main()


# In[ ]:




