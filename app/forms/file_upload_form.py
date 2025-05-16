from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField, RadioField
from wtforms.validators import InputRequired
# Above are the tools needed to use and validate flask forms
import app.constants as msg

class FileUploadForm(FlaskForm):
    # Radio buttons for selecting the broker type (Binance or Kraken)
    broker = RadioField('Choose broker:', choices=[('kraken', 'Kraken'), ('binance', 'Binance')], validators=[
        InputRequired(message=msg.BROKER_REQUIRED)
    ])
    # File input field that only accepts .csv files
    file = FileField('Upload .csv file:', validators=[
        FileRequired(),
        FileAllowed(['csv'], msg.CSV_ONLY)
    ])
    # Submit button to trigger upload and processing
    submit = SubmitField('Upload')
    # Optional second submit (can be used for conditional behaviour)
    calculate = SubmitField('')