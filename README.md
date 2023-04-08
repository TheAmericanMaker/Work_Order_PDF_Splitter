# Work_Order_PDF_Splitter
Splits a large PDF of Work Orders into smaller PDFs of individual Work Orders regardless of the # of pages in each WO.
It takes the page # from the first line in the pdf page and uses that to determine where to split the PDF's. It solves a specific problem we have.

you'll need a couple python packages.

pip install PyPDF2
pip install tkinter

To use on windows without needing python installed you can use pyinstaller to generate an executable. The command is below.

pyinstaller --onefile --noconsole Work_Order_PDF_Splitter.py
