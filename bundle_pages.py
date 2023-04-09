# Import necessary libraries
import sys
import os
import re
import PyPDF2


# Function to extract the page number from a page
def extract_page_number(page):
    try:
        # Extract text from the page and remove leading/trailing whitespace
        text = page.extract_text().strip()
        # Use regular expression to search for the page number in the text
        match = re.search(r"page\s+(\d+)", text, re.IGNORECASE)
        # If a match is found, return the page number as an integer
        if match:
            return int(match.group(1))
    except:
        return None

# Function to process and bundle pages
def bundle_pages(input_pdf_path, output_directory):
    # Open the input PDF file
    with open(input_pdf_path, "rb") as input_pdf_file:
        # Create a PdfReader object to read the input file
        pdf_reader = PyPDF2.PdfReader(input_pdf_file)
        # Create a PdfWriter object to write output files
        pdf_writer = PyPDF2.PdfWriter()

        # Initialize the output file count
        output_file_count = 1

        # Iterate through each page in the input PDF
        for page_number in range(len(pdf_reader.pages)):
            # Get the current page
            page = pdf_reader.pages[page_number]
            # Extract the page number from the page
            extracted_page_number = extract_page_number(page)

            # Check if the extracted page number is not None
            if extracted_page_number is not None:
                # If the extracted page number is 1 and there are pages in the PdfWriter object
                if extracted_page_number == 1 and len(pdf_writer.pages) > 0:
                    # Create the output file path
                    output_file_path = os.path.join(output_directory, f"output_{output_file_count}.pdf")
                    # Open the output file and write the bundled pages
                    with open(output_file_path, "wb") as output_pdf_file:
                        pdf_writer.write(output_pdf_file)
                    # Create a new PdfWriter object for the next bundle
                    pdf_writer = PyPDF2.PdfWriter()
                    # Increment the output file count
                    output_file_count += 1

                # Add the current page to the PdfWriter object
                pdf_writer.add_page(page)

        # Save the last bundle of pages if there are any
        if len(pdf_writer.pages) > 0:
            output_file_path = os.path.join(output_directory, f"output_{output_file_count}.pdf")
            with open(output_file_path, "wb") as output_pdf_file:
                pdf_writer.write(output_pdf_file)

# Main function
def main():
    # Check if the command line arguments are provided correctly
    if len(sys.argv) != 3:
        print("Usage: python3 bundle_pdf.py <input_pdf> <output_directory>")
        sys.exit(1)

    # Get the input PDF path and output directory from the command line arguments
    input_pdf_path = sys.argv[1]
    output_directory = sys.argv[2]

    # Create the output directory if it doesn't exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Process the input PDF and save the bundled pages in the output directory
    bundle_pages(input_pdf_path, output_directory)

# Function to open a file dialog to browse for the input PDF file
def browse_input_file():
    file_path = filedialog.askopenfilename(filetypes=[("PDF files", "*.pdf")])
    # Set the input PDF path in the input field
    input_pdf_path.set(file_path)

# Function to open a folder dialog to browse for the output directory
def browse_output_folder():
    folder_path = filedialog.askdirectory()
    # Set the output directory in the input field
    output_directory.set(folder_path)

# Function to process the PDF using the provided input PDF path and output directory
def process_pdf():
    input_pdf = input_pdf_path.get()
    output_dir = output_directory.get()
    if input_pdf and output_dir:
        bundle_pages(input_pdf, output_dir)


# Run the main function when the script is executed
if __name__ == "__main__":
    main()