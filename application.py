
import pdf2image
import zipfile
import base64
from io import BytesIO
from flask import Flask, request, redirect, abort, send_file, render_template
import os
import shutil
import pytesseract
from PIL import Image

app = Flask(__name__)

UPLOAD_FOLDER = 'static/uploads/'


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/process-pdf', methods=['GET', 'POST'])
def process():
    if request.method == 'POST':
        if 'file' not in request.files:
            print(request.files)
            return redirect('/')
        file = request.files['file']
        if file.filename == '':
            return abort(400)
        if file:
            # delete any existing files in the staging folder
            for filename in os.listdir(UPLOAD_FOLDER):
                file_path = os.path.join(UPLOAD_FOLDER, filename)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print('Failed to delete %s. Reason: %s' % (file_path, e))
            # this function converts pdf to jpg and outputs files int the output folder in jpg format
            image_names = pdf2image.convert_from_bytes(
                file.read(), output_folder=UPLOAD_FOLDER, paths_only=True, fmt='jpg')
            # we'd like to save the bytes of jpg images in database along with pdf and lemma words
            image_bytes = []
            for i in range(len(image_names)):
                with open(image_names[i], 'rb') as image_file:
                    encoded_string = base64.b64encode(image_file.read())
                    image_bytes = image_bytes + [encoded_string]

            outfile = "static/uploads/out_text.txt"

            with open(outfile, 'w', encoding='utf-8') as f:
                # Iterate from 1 to total number of pages
                for i in range(len(image_names)):
                    filename = image_names[i]
                    # Recognize the text as string in image using pytesserct
                    text = str(
                        ((pytesseract.image_to_string(Image.open(filename)))))
                    # To remove this, we replace every '-\n' to ''.
                    text = text.replace('-\n', '')
                    f.write(text)

            return 'Uploaded'
        else:
            return abort(500)
    else:
        return abort(404)


if __name__ == '__main__':
    app.run(host="127.0.0.1")
