# Work_Order_PDF_Splitter_V1
Splits a large PDF of Work Orders into smaller PDFs of individual Work Orders regardless of the # of pages in each WO.
It takes the page # from the first line in the pdf page and uses that to determine where to split the PDF's. It solves a specific problem we have.

you will need python3 and a few packages installed to run the script

* Install python3 from python.org the current latest version is 3.11.3

Once you have python installed you add the packages using python's package manager thats called pip.

- Open a terminal or command line and type:

pip install PyPDF2
--------------------
after that installs type
-------------------------
pip install tkinter

-----------------------------
Now you can run the script using the command line.

got to the folder holding the script, right click inside it and select "Open in terminal"
this will open the command line in the correct path.

type this command to run the script. This will launch the Graphical interface.

python3 Work_Order_PDF_Splitter_V1.py





To use on windows without needing python installed you can use pyinstaller to generate an executable. The command is below.
Or you can try the .exe I've generated. Heres the link.


pyinstaller --onefile --noconsole Work_Order_PDF_Splitter_V1.py
