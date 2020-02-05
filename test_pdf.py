from PIL import Image 
import pytesseract 
import sys 
from pdf2image import convert_from_bytes 
import os 

from pdf2image.exceptions import (
    PDFInfoNotInstalledError,
    PDFPageCountError,
    PDFSyntaxError
)

# Path of the pdf 
PDF_file = "./tax_disclosure.pdf"
  
''' 
Part #1 : Converting PDF to images 
'''
pages = convert_from_bytes(open(PDF_file, 'rb').read()) 
  
# Counter to store images of each page of PDF to image 
image_counter = 1
  
# Iterate through all the pages stored above 
for page in pages: 
    filename = "page_"+str(image_counter)+".jpg"
    page.save(filename, 'JPEG') 
    image_counter = image_counter + 1

#Part #2 - Recognizing text from the images using OCR 
# Variable to get count of total number of pages 
filelimit = image_counter-1
# Creating a text file to write the output 
outfile = "out_text.txt"
# Open the file in append mode so that  
# All contents of all images are added to the same file 
f = open(outfile, "a") 
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
# Iterate from 1 to total number of pages 
for i in range(1, filelimit + 1): 
    filename = "page_"+str(i)+".jpg"
    # Recognize the text as string in image using pytesserct 
    text = str(((pytesseract.image_to_string(Image.open(filename)))))
    # To remove this, we replace every '-\n' to ''. 
    text = text.replace('-\n', '')     
    f.write(text) 
  
# Close the file after writing all the text. 
f.close() 


