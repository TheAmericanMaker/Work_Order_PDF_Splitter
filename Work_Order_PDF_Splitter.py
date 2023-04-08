import sys
import os
import re
import PyPDF2
import tkinter as tk
from tkinter import filedialog

def extract_page_number(page):
    try:
        text = page.extract_text().strip()
        match = re.search(r"page\s+(\d+)", text, re.IGNORECASE)
        if match:
            return int(match.group(1))
    except:
        return None

def bundle_pages(input_pdf_path, output_directory):
    with open(input_pdf_path, "rb") as input_pdf_file:
        pdf_reader = PyPDF2.PdfReader(input_pdf_file)
        pdf_writer = PyPDF2.PdfWriter()

        output_file_count = 1

        for page_number in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_number]
            extracted_page_number = extract_page_number(page)

            if extracted_page_number is not None:
                if extracted_page_number == 1 and len(pdf_writer.pages) > 0:
                    output_file_path = os.path.join(output_directory, f"output_{output_file_count}.pdf")
                    with open(output_file_path, "wb") as output_pdf_file:
                        pdf_writer.write(output_pdf_file)
                    pdf_writer = PyPDF2.PdfWriter()
                    output_file_count += 1

                pdf_writer.add_page(page)

        # Save the last bundle of pages
        if len(pdf_writer.pages) > 0:
            output_file_path = os.path.join(output_directory, f"output_{output_file_count}.pdf")
            with open(output_file_path, "wb") as output_pdf_file:
                pdf_writer.write(output_pdf_file)

def main():
    if len(sys.argv) != 3:
        print("Usage: python3 bundle_pdf.py <input_pdf> <output_directory>")
        sys.exit(1)

    input_pdf_path = sys.argv[1]
    output_directory = sys.argv[2]

    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    bundle_pages(input_pdf_path, output_directory)


def browse_input_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    input_pdf_path.set(file_path)

def browse_output_folder():
    folder_path = filedialog.askdirectory()
    output_directory.set(folder_path)

def process_pdf():
    input_pdf = input_pdf_path.get()
    output_dir = output_directory.get()
    if input_pdf and output_dir:
        bundle_pages(input_pdf, output_dir)

root = tk.Tk()
root.title("PDF Splitter")

frame = tk.Frame(root)
frame.pack(padx=10, pady=10)

input_pdf_path = tk.StringVar()
output_directory = tk.StringVar()

tk.Label(frame, text="Input PDF:").grid(row=0, column=0, sticky="w")
tk.Entry(frame, textvariable=input_pdf_path, width=50).grid(row=0, column=1)
tk.Button(frame, text="Browse", command=browse_input_file).grid(row=0, column=2)

tk.Label(frame, text="Output Directory:").grid(row=1, column=0, sticky="w")
tk.Entry(frame, textvariable=output_directory, width=50).grid(row=1, column=1)
tk.Button(frame, text="Browse", command=browse_output_folder).grid(row=1, column=2)

tk.Button(frame, text="Process", command=process_pdf).grid(row=2, columnspan=3, pady=10)

root.mainloop()

if __name__ == "__main__":
    main()