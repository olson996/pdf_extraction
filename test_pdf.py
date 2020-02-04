#!/usr/bin/env python3
import PyPDF2
pdfFileObj = open('tax_disclosure.pdf', 'rb')
pdfReader = PyPDF2.PdfFileReader(pdfFileObj)
print(pdfReader.numPages)