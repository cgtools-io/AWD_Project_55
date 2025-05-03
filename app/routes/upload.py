from flask import Blueprint, render_template, flash, redirect, url_for
from werkzeug.utils import secure_filename
from app.forms.file_upload_form import FileUploadForm
import os

upload_bp = Blueprint('upload', __name__)

@upload_bp.route('/file_upload', methods=['GET', 'POST'])
def file_upload():
    form = FileUploadForm()

    if form.validate_on_submit():
        file = form.file.data
        if isinstance(file, list): #Checks in case the file is uploaded as a list
            file = file[0]

        filename = secure_filename(file.filename)

        upload_folder = os.path.join('app/static/uploads')
        os.makedirs(upload_folder, exist_ok=True)
        file.save(os.path.join(upload_folder, filename))

        flash('Upload successful!', 'success')
        return redirect(url_for('upload.file_upload'))

    return render_template('user/file_upload.html', form=form)