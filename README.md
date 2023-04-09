There are 2 version of this.
The standalone python script with a nice little gui to select the file and the output folder, and there is the web app version of the pdf splitter.
For the standalone script run the Work_Order_PDF_Splitter.py
For the server based web app run the app.py script and it launches a server at localhost:5000.

Be sure to have a folder named 'output' and one named "uploads' in the directory you have the scripts in. They should create the folders automaticly when run but the "uploads" folder doesnt always generate properly.

Navigate there in a browser.
You can upload a pdf to be split.
This app splits the file and then puts the individual pdf files into a zip file that you can then download. The page refreshes after 5 seconds so the download link is visible.
after downloading your files you can click the delete button and it clears out the split files so you can go again with a new input file.

