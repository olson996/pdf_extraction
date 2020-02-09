from app import app, db
import pdf2image
import zipfile
import base64
from io import BytesIO
from flask import Flask, request, redirect, abort, send_file, render_template, flash, url_for
import os
import shutil
import pytesseract
from PIL import Image
from app.forms import LoginForm, RegistrationForm
from flask_login import current_user, login_user, logout_user, login_required
from app.models import User
from werkzeug.urls import url_parse

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)
    return render_template('login.html', title='Sign In', form=form)

UPLOAD_FOLDER = 'app/static/uploads/'


@app.route('/index')
@app.route('/')
@login_required
def index():
    posts = [
        {
            'author': {'username': 'john'},
            'body': 'Beautiful day in LA'
        }
    ]
    return render_template('index.html', title="Home Page", posts=posts)


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

            outfile = "app/static/uploads/out_text.txt"

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

            f = open(outfile, "r+")
            return_string = f.read()
            f.close()
            return return_string
        else:
            return abort(500)
    else:
        return abort(404)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)
