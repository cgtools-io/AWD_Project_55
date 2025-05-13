from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileRequired
from wtforms import SubmitField, RadioField
from wtforms.validators import InputRequired
# Above are the tools needed to use and validate flask forms
import app.constants as msg

class FileUploadForm(FlaskForm):
    broker = RadioField('Crypto Broker:', choices=[('kraken', 'Kraken'), ('binance', 'Binance'), ('other', 'Other')], validators=[
        InputRequired(message=msg.BROKER_REQUIRED)
    ])
    file = FileField('Upload CSV', validators=[
        FileRequired(),
        FileAllowed(['csv'], msg.CSV_ONLY)
    ])
    submit = SubmitField('Upload')

