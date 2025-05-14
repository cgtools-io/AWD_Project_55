from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField
# Above are the tools needed to use and validate flask forms
import app.constants as msg

class FileUploadForm(FlaskForm):
    file = FileField('Upload CSV', validators=[
        FileRequired(),
        FileAllowed(['csv'], msg.CSV_ONLY)
    ])
    submit = SubmitField('Upload')

