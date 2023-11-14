# Work Order PDF Splitter

## Description
A niche tool to split a large PDF file containing multiple "Work Orders" into individual PDF files, each being a separate "Work Order", regardless of the number of pages per Work Order. 

## Motivation
This project was developed to fix a problem in our process of handling and organizing work orders, especially in scenarios where bulk PDFs need to be broken down into individual documents for easier management and access. This problem has now been fixed upstream and this tool is not needed. However, I'll leave it here incase it may be of use to others.

## Features
- Splits a single PDF into multiple PDFs based on Work Order separation.
- Handles PDFs of various lengths and complexities.
- User-friendly interface for easy operation.

## Versions of the Tool

### Standalone Python Script with GUI
- Features a user-friendly GUI for selecting the input file and output folder.
- To use, run `Work_Order_PDF_Splitter.py`.

### Web App Version
- Hosted as a server-based web application accessible at `localhost:5000`.
- To launch, run `app.py`.
- Ensure you have folders named 'output' and 'uploads' in the script directory.
  - Note: The 'uploads' folder may not always generate automatically.

#### How to Use the Web App
1. Navigate to `localhost:5000` in your browser.
2. Upload a PDF to be split.
3. The app splits the PDF and packages the individual files into a downloadable zip file.
4. The page refreshes after 5 seconds to display the download link.
5. After downloading, use the delete button to clear out the split files for a new input file.

## License
- Creative Commons

## Contact
For any inquiries or contributions, please contact me here.
